"""
backend/app/api/routes/simulation.py
Simulation & Optimization execution endpoints:
Runs the discrete-event digital twin, injects disruptions, steps ticks,
manages fleet telemetry, and executes the paired Monte Carlo strategy comparison.
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, Security
from pydantic import BaseModel

from app.services.auth_service import UserProfile, require_roles_or_demo
from app.services.alert_service import AlertService
from app.sim.runner import MonteCarloScenarioRunner
from contracts.models import DisruptionContract, DisruptionType, TruckStatus
from app.contracts.seed_specs import (
    generate_seed_products,
    generate_seed_network,
    generate_seed_trucks,
    generate_initial_warehouse_inventories,
)
from app.sim.engine import SupplyChainSimulationEngine
from app.optimizers.rebalance import WarehouseRebalanceOptimizer
from app.sim.strategy_comparison import (
    ScenarioType,
    StrategyComparisonEvaluator,
    DisruptionScenarioRegistry,
    ScenarioComparisonReport,
)

router = APIRouter(prefix="/simulation", tags=["Simulation & Optimization"])
alert_service = AlertService()

# Global in-memory engine for live tick-by-tick simulation playback
live_engine: Optional[SupplyChainSimulationEngine] = None


def get_or_create_live_engine(seed: int = 42, optimizer_enabled: bool = True) -> SupplyChainSimulationEngine:
    global live_engine
    if live_engine is None:
        live_engine = SupplyChainSimulationEngine(seed=seed, optimizer_enabled=optimizer_enabled)
        products = generate_seed_products(50)
        net_data = generate_seed_network()
        nodes = net_data["nodes"]
        trucks = generate_seed_trucks(10)
        inventories = generate_initial_warehouse_inventories(nodes, products, initial_stock_units=300.0)
        live_engine.initialize_network(products, nodes, trucks, inventories)
    return live_engine


class SimulationRunRequest(BaseModel):
    seed: int = 42
    duration_ticks: int = 14
    optimizer_enabled: bool = False
    demand_spike_severity: Optional[float] = None
    supplier_failure_severity: Optional[float] = None




@router.get("/state")
def get_simulation_state(
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER", "STORE_OWNER", "TRUCK_DRIVER"])),
):
    """Returns the single authoritative backend state of the live digital twin."""
    eng = get_or_create_live_engine()
    last_snap = eng.kpi_accruer.snapshots[-1] if eng.kpi_accruer.snapshots else None

    fleet_summary = []
    for trk_id, trk in eng.network.trucks.items():
        fleet_summary.append({
            "id": trk.id,
            "name": trk.name,
            "cluster_id": trk.cluster_id,
            "status": trk.status.value,
            "capacity": trk.capacity_units,
            "speed_km_h": trk.speed_km_per_hour,
            "current_lat": trk.current_lat,
            "current_lon": trk.current_lon,
            "fuel_cost": round(trk.total_fuel_cost, 2),
            "km_travelled": round(trk.total_km_travelled, 1),
            "current_shipment_id": trk.current_shipment_id,
        })

    active_disrs = [
        d.model_dump() for d in eng.disruption_engine.active_disruptions
    ]

    return {
        "status": "ok",
        "tick": eng.current_tick,
        "optimizer_enabled": eng.optimizer_enabled,
        "active_disruptions": active_disrs,
        "fleet": fleet_summary,
        "active_alerts_count": len([a for a in alert_service.alerts.values() if a.status.value == "ACTIVE"]),
        "pending_recommendations_count": len([r for r in alert_service.recommendations.values() if r.status.value == "PENDING"]),
        "metrics": last_snap.model_dump() if last_snap else {
            "tick": 0,
            "total_revenue": 0.0,
            "total_procurement_cost": 0.0,
            "total_holding_cost": 0.0,
            "total_transport_cost": 0.0,
            "total_unmet_demand_cost": 0.0,
            "total_operating_cost": 0.0,
            "net_profit": 0.0,
            "fill_rate": 0.992,
            "stockout_frequency": 0.008,
            "total_demanded_units": 0.0,
            "total_fulfilled_units": 0.0,
            "total_unmet_units": 0.0,
        },
        "kpi_history": [s.model_dump() for s in eng.kpi_accruer.snapshots[-25:]],
        "provenance": {
            "source": "NEXUS_SIMPY_DISCRETE_EVENT_TWIN",
            "deterministic_seed": eng.seed,
            "authoritative": True,
        },
    }


@router.get("/fleet")
def get_fleet_telemetry(
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "TRUCK_DRIVER"])),
):
    """Returns detailed telemetry and GPS status for all 10 fleet vehicles."""
    eng = get_or_create_live_engine()
    fleet = []
    for trk_id, trk in eng.network.trucks.items():
        fleet.append({
            "id": trk.id,
            "name": trk.name,
            "cluster_id": trk.cluster_id,
            "status": trk.status.value,
            "capacity": trk.capacity_units,
            "speed_km_h": trk.speed_km_per_hour,
            "current_lat": trk.current_lat,
            "current_lon": trk.current_lon,
            "fuel_cost": round(trk.total_fuel_cost, 2),
            "km_travelled": round(trk.total_km_travelled, 1),
            "current_shipment_id": trk.current_shipment_id,
        })
    return {"status": "ok", "trucks": fleet}


class BreakdownRequest(BaseModel):
    truck_id: str = "TRUCK_03"


@router.post("/truck-breakdown")
def trigger_truck_breakdown_endpoint(
    request: BreakdownRequest,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER", "TRUCK_DRIVER"])),
):
    """Triggers realistic mechanical breakdown, creates critical alert, and generates failover rescue recommendation."""
    eng = get_or_create_live_engine()
    alert, rec = alert_service.trigger_truck_breakdown(request.truck_id, live_engine=eng)
    return {
        "status": "breakdown_registered",
        "broken_truck_id": request.truck_id,
        "alert": alert.model_dump(),
        "recommendation": rec.model_dump(),
    }


class RescueRequest(BaseModel):
    broken_truck_id: str = "TRUCK_03"
    rescue_truck_id: str = "TRUCK_04"


@router.post("/fleet/rescue")
def execute_rescue_dispatch(
    request: RescueRequest,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "TRUCK_DRIVER"])),
):
    """Dispatches the nearest available rescue vehicle to salvage stranded cargo."""
    eng = get_or_create_live_engine()
    if request.broken_truck_id in eng.network.trucks and request.rescue_truck_id in eng.network.trucks:
        rescuer = eng.network.trucks[request.rescue_truck_id]
        rescuer.status = TruckStatus.IN_TRANSIT

    # Auto approve linked recommendation if present
    for rec in alert_service.recommendations.values():
        if rec.type == "TRUCK_FAILOVER" and rec.status.value == "PENDING":
            alert_service.approve_recommendation(rec.id, live_engine=eng)
            break

    return {
        "status": "rescue_dispatched",
        "broken_truck_id": request.broken_truck_id,
        "rescue_truck_id": request.rescue_truck_id,
        "message": f"Rescue vehicle {request.rescue_truck_id} en route to breakdown location.",
    }


class DisruptionInjectRequest(BaseModel):
    disruption_type: DisruptionType = DisruptionType.DEMAND_SPIKE
    target_id: str = "ALL"
    severity: float = 2.0
    duration_ticks: int = 4
    description: str = "Manual disruption injection"


@router.post("/disruptions/inject")
def inject_custom_disruption(
    request: DisruptionInjectRequest,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR"])),
):
    """Injects custom disruption into the live engine and generates alert & mitigation recommendation."""
    eng = get_or_create_live_engine()
    disr_id = f"INJ_{request.disruption_type.value}_{eng.current_tick}"
    disruption = DisruptionContract(
        id=disr_id,
        disruption_type=request.disruption_type,
        target_id=request.target_id,
        start_tick=eng.current_tick,
        duration_ticks=request.duration_ticks,
        severity=request.severity,
        description=request.description,
    )
    eng.disruption_engine.schedule_disruption(disruption)
    alert, rec = alert_service.trigger_disruption_alert(
        disruption_type=request.disruption_type.value,
        target_id=request.target_id,
        severity=request.severity,
        duration=request.duration_ticks,
        live_engine=eng,
    )
    return {
        "status": "injected",
        "disruption": disruption.model_dump(),
        "alert": alert.model_dump(),
        "recommendation": rec.model_dump(),
    }


@router.post("/run")
def run_simulation(
    request: SimulationRunRequest,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR"])),
):
    """Executes discrete-event digital twin simulation and returns KPI snapshots."""
    runner = MonteCarloScenarioRunner(base_seed=request.seed)
    disruptions = []

    if request.demand_spike_severity:
        disruptions.append(
            DisruptionContract(
                id="API_DISR_SPIKE",
                disruption_type=DisruptionType.DEMAND_SPIKE,
                target_id="ALL",
                start_tick=3,
                duration_ticks=4,
                severity=request.demand_spike_severity,
                description="API-triggered demand spike",
            )
        )

    if request.supplier_failure_severity:
        disruptions.append(
            DisruptionContract(
                id="API_DISR_SUPPLIER",
                disruption_type=DisruptionType.SUPPLIER_FAILURE,
                target_id="MFR_01",
                start_tick=2,
                duration_ticks=5,
                severity=request.supplier_failure_severity,
                description="API-triggered supplier failure",
            )
        )

    snapshots = runner.run_single_scenario(
        seed=request.seed,
        duration_ticks=request.duration_ticks,
        disruptions=disruptions,
        optimizer_enabled=request.optimizer_enabled,
    )

    final = snapshots[-1]
    return {
        "status": "completed",
        "duration_ticks": request.duration_ticks,
        "optimizer_enabled": request.optimizer_enabled,
        "final_kpis": final.model_dump(),
        "snapshots": [s.model_dump() for s in snapshots],
    }


@router.post("/tick")
def advance_tick(
    optimizer_enabled: Optional[bool] = None,
    demand_spike: Optional[float] = None,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER", "STORE_OWNER"])),
):
    """Advances the live digital twin simulation by 1 tick (day) and returns the authoritative state."""
    eng = get_or_create_live_engine()
    if optimizer_enabled is not None:
        eng.optimizer_enabled = optimizer_enabled

    if demand_spike and demand_spike > 1.0:
        eng.disruption_engine.schedule_disruption(
            DisruptionContract(
                id=f"TICK_DISR_{eng.current_tick}",
                disruption_type=DisruptionType.DEMAND_SPIKE,
                target_id="ALL",
                start_tick=eng.current_tick,
                duration_ticks=3,
                severity=demand_spike,
                description="Live tick-injected demand spike",
            )
        )

    snapshot = eng.run_tick()

    alert_service.log_activity(
        event_type="SIMULATION_TICK",
        description=f"Advanced simulation to Tick {snapshot.tick}. Fill rate: {snapshot.fill_rate * 100:.1f}%.",
        tick=snapshot.tick,
        details={"fill_rate": snapshot.fill_rate, "unmet_units": snapshot.total_unmet_units},
    )

    return {
        "status": "ok",
        "tick": snapshot.tick,
        "snapshot": snapshot.model_dump(),
    }


@router.post("/reset")
def reset_live_simulation(
    seed: int = 42,
    optimizer_enabled: bool = False,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER", "STORE_OWNER"])),
):
    """Resets the live digital twin engine back to Tick 0."""
    global live_engine
    live_engine = None
    eng = get_or_create_live_engine(seed=seed, optimizer_enabled=optimizer_enabled)
    alert_service.reset()
    return {
        "status": "reset",
        "tick": 0,
        "optimizer_enabled": optimizer_enabled,
    }


class StrategyComparisonRequest(BaseModel):
    scenario_type: ScenarioType = ScenarioType.COMPOUND_BLACK_SWAN
    num_seeds: int = 10
    duration_ticks: int = 30


@router.get("/scenarios/catalog")
def get_scenario_catalog():
    """Returns the list of 5 standardized disruption benchmark scenarios."""
    catalog = []
    for sc in ScenarioType:
        name, desc = DisruptionScenarioRegistry.get_metadata(sc)
        disruptions = DisruptionScenarioRegistry.get_disruptions(sc)
        catalog.append({
            "scenario_type": sc.value,
            "name": name,
            "description": desc,
            "disruptions_count": len(disruptions),
            "disruptions": [d.model_dump() for d in disruptions],
        })
    return {"catalog": catalog}


@router.post("/strategy-comparison", response_model=ScenarioComparisonReport)
def run_strategy_comparison(
    request: StrategyComparisonRequest,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR"])),
):
    """
    Executes paired Monte Carlo comparisons (Baseline s,S vs. Optimized MILP+Quantiles+VRP)
    using Common Random Numbers (CRN).
    Returns paired differences, 95% Confidence Intervals, two-tailed p-values,
    and tick-by-tick recovery trajectories.
    """
    evaluator = StrategyComparisonEvaluator(base_seed=1000)
    report = evaluator.evaluate_scenario(
        scenario_type=request.scenario_type,
        num_seeds=request.num_seeds,
        duration_ticks=request.duration_ticks,
    )
    return report
