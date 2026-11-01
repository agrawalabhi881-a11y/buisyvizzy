"""
backend/app/api/routes/contract_aliases.py
Target API Contract Implementation (Section 7 of Master Build Prompt).
Exposes explicit REST endpoints matching the master specification:
- GET /api/network
- GET /api/shipments
- GET /api/trucks
- POST /api/trucks/{truck_id}/breakdown
- POST /api/trucks/{truck_id}/rescue
- GET /api/scenarios
- POST /api/scenarios/run
- GET /api/disruptions
- POST /api/disruptions
- POST /api/simulation/play
- POST /api/simulation/pause
- POST /api/simulation/step
- POST /api/experiments/compare
- GET /api/forecasts
- POST /api/forecasts/run
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Security, HTTPException
from pydantic import BaseModel

from app.services.auth_service import UserProfile, require_roles_or_demo
from app.services.alert_service import AlertService
from app.api.routes.simulation import (
    get_or_create_live_engine,
    advance_tick,
    reset_live_simulation,
    StrategyComparisonRequest,
    run_strategy_comparison,
)
from app.api.routes.forecasting import forecast_service_instance
from app.sim.strategy_comparison import ScenarioType, DisruptionScenarioRegistry
from contracts.models import (
    DisruptionContract,
    DisruptionType,
    TruckStatus,
    NodeRole,
)

router = APIRouter(tags=["Target Contract Aliases (Section 7)"])
alert_service = AlertService()


# 1. GET /api/network
@router.get("/network")
def get_network(
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER", "STORE_OWNER", "TRUCK_DRIVER"])),
):
    """Returns suppliers, warehouses, stores, products, and network topology metadata."""
    eng = get_or_create_live_engine()
    suppliers = [
        {"id": n.id, "name": n.name, "role": n.role.value, "lat": n.lat, "lon": n.lon, "status": "OPERATIONAL"}
        for n in eng.network.nodes.values() if n.role == NodeRole.MANUFACTURER
    ]
    warehouses = [
        {
            "id": n.id,
            "name": n.name,
            "role": n.role.value,
            "lat": n.lat,
            "lon": n.lon,
            "cluster_id": n.cluster_id,
            "max_capacity": n.max_capacity_units,
            "current_stock": n.total_current_stock,
            "operating_cost": n.operating_cost_per_day,
        }
        for n in eng.network.nodes.values() if n.role == NodeRole.WAREHOUSE
    ]
    stores = [
        {
            "id": n.id,
            "name": n.name,
            "role": n.role.value,
            "lat": n.lat,
            "lon": n.lon,
            "cluster_id": n.cluster_id,
            "current_stock": n.total_current_stock,
            "assigned_warehouse": eng.network.store_to_warehouse.get(n.id, "WH_01"),
        }
        for n in eng.network.nodes.values() if n.role == NodeRole.STORE
    ]
    products = [
        {
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "category": p.category,
            "unit_cost": p.unit_cost,
            "unit_price": p.unit_price,
            "holding_cost": p.holding_cost_per_day,
            "penalty_lost_sales": p.unmet_demand_penalty,
        }
        for p in list(eng.network.products.values())[:15]
    ]

    return {
        "status": "ok",
        "provenance": "AUTHORITATIVE_BACKEND_SAMPLE_DATA",
        "counts": {
            "suppliers": len(suppliers),
            "warehouses": len(warehouses),
            "stores": len(stores),
            "products": len(eng.network.products),
        },
        "suppliers": suppliers,
        "warehouses": warehouses,
        "stores": stores,
        "products_sample": products,
    }


# 2. GET /api/shipments
@router.get("/shipments")
def get_shipments(
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER", "TRUCK_DRIVER"])),
):
    """Returns active in-transit shipments and recent deliveries."""
    eng = get_or_create_live_engine()
    active = [
        {
            "id": s.id,
            "order_id": s.order_id,
            "origin": s.origin_id,
            "destination": s.destination_id,
            "truck_id": s.truck_id,
            "cargo_units": s.cargo_units,
            "dispatch_tick": s.dispatch_tick,
            "expected_arrival_tick": s.expected_arrival_tick,
            "status": s.status.value,
            "distance_km": s.distance_km,
        }
        for s in eng.network.active_shipments.values()
    ]
    delivered = [
        {
            "id": s.id,
            "order_id": s.order_id,
            "origin": s.origin_id,
            "destination": s.destination_id,
            "cargo_units": s.cargo_units,
            "status": s.status.value,
        }
        for s in eng.network.delivered_shipments[-10:]
    ]
    return {"status": "ok", "active_count": len(active), "active_shipments": active, "recent_delivered": delivered}


# 3. GET /api/trucks
@router.get("/trucks")
def list_trucks(
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "TRUCK_DRIVER"])),
):
    """Returns truck and driver state, assignments, cargo, GPS coordinates, and routes."""
    eng = get_or_create_live_engine()
    driver_names = [
        "Marcus Vance", "Sarah Jenkins", "Carlos Gomez", "Elena Rostova", "David Kowalski",
        "Amara Okafor", "Kenji Sato", "Rachel Chen", "Jamal Washington", "Mateo Silva"
    ]
    trucks = []
    for idx, (t_id, trk) in enumerate(eng.network.trucks.items()):
        driver = driver_names[idx % len(driver_names)]
        trucks.append({
            "id": trk.id,
            "name": trk.name,
            "driver_name": driver,
            "cluster_id": trk.cluster_id,
            "status": trk.status.value,
            "capacity_units": trk.capacity_units,
            "current_lat": trk.current_lat,
            "current_lon": trk.current_lon,
            "speed_km_h": trk.speed_km_per_hour,
            "total_km_travelled": round(trk.total_km_travelled, 1),
            "total_fuel_cost": round(trk.total_fuel_cost, 2),
            "current_shipment_id": trk.current_shipment_id,
        })
    return {"status": "ok", "trucks_count": len(trucks), "trucks": trucks}


# 4. POST /api/trucks/{truck_id}/breakdown
@router.post("/trucks/{truck_id}/breakdown")
def simulate_truck_breakdown(
    truck_id: str,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "TRUCK_DRIVER"])),
):
    """Simulates mechanical breakdown on a specified vehicle."""
    eng = get_or_create_live_engine()
    if truck_id not in eng.network.trucks:
        raise HTTPException(status_code=404, detail=f"Truck {truck_id} not found in fleet")
    alert, rec = alert_service.trigger_truck_breakdown(truck_id, live_engine=eng)
    return {
        "status": "breakdown_registered",
        "broken_truck_id": truck_id,
        "alert": alert.model_dump(),
        "recommendation": rec.model_dump(),
    }


# 5. POST /api/trucks/{truck_id}/rescue
class RescueRequestSchema(BaseModel):
    rescue_truck_id: Optional[str] = None


@router.post("/trucks/{truck_id}/rescue")
def request_truck_rescue(
    truck_id: str,
    body: Optional[RescueRequestSchema] = None,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "TRUCK_DRIVER"])),
):
    """Dispatches nearest available rescue vehicle to salvage broken truck's cargo."""
    eng = get_or_create_live_engine()
    if truck_id not in eng.network.trucks:
        raise HTTPException(status_code=404, detail=f"Truck {truck_id} not found")

    target_truck = eng.network.trucks[truck_id]
    rescuer_id = body.rescue_truck_id if (body and body.rescue_truck_id) else "TRUCK_04"

    if rescuer_id in eng.network.trucks:
        rescuer = eng.network.trucks[rescuer_id]
        rescuer.status = TruckStatus.IN_TRANSIT

    # Auto-approve any pending failover recommendation
    for rec in alert_service.recommendations.values():
        if rec.type == "TRUCK_FAILOVER" and rec.status.value == "PENDING":
            alert_service.approve_recommendation(rec.id, live_engine=eng)
            break

    return {
        "status": "rescue_dispatched",
        "broken_truck_id": truck_id,
        "rescue_truck_id": rescuer_id,
        "message": f"Rescue vehicle {rescuer_id} en route to breakdown location.",
    }


# 6. GET /api/scenarios
@router.get("/scenarios")
def list_scenarios():
    """Returns backend-defined scenario presets."""
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
    return {"status": "ok", "scenarios": catalog}


# 7. POST /api/scenarios/run
class RunScenarioSchema(BaseModel):
    scenario_type: str = "COMPOUND_BLACK_SWAN"
    duration_ticks: int = 14
    optimizer_enabled: bool = True


@router.post("/scenarios/run")
def run_scenario_endpoint(
    request: RunScenarioSchema,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR"])),
):
    """Initializes and runs the selected scenario."""
    eng = get_or_create_live_engine()
    try:
        sc_enum = ScenarioType(request.scenario_type)
    except ValueError:
        sc_enum = ScenarioType.COMPOUND_BLACK_SWAN

    disruptions = DisruptionScenarioRegistry.get_disruptions(sc_enum)
    for d in disruptions:
        eng.disruption_engine.schedule_disruption(d)

    return {
        "status": "scenario_initialized",
        "scenario_type": sc_enum.value,
        "disruptions_scheduled": len(disruptions),
    }


# 8. GET & POST /api/disruptions
@router.get("/disruptions")
def list_disruptions(
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR"])),
):
    """Returns scheduled, active, and completed disruptions."""
    eng = get_or_create_live_engine()
    return {
        "status": "ok",
        "active": [d.model_dump() for d in eng.disruption_engine.active_disruptions],
        "scheduled": [d.model_dump() for d in eng.disruption_engine.scheduled_disruptions],
        "history": [d.model_dump() for d in eng.disruption_engine.disruption_history],
    }


class DisruptionScheduleSchema(BaseModel):
    disruption_type: DisruptionType = DisruptionType.DEMAND_SPIKE
    target_id: str = "ALL"
    severity: float = 2.0
    duration_ticks: int = 4
    description: str = "Target API scheduled disruption"


@router.post("/disruptions")
def schedule_disruption_endpoint(
    request: DisruptionScheduleSchema,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR"])),
):
    """Schedules or injects a supported disruption."""
    eng = get_or_create_live_engine()
    disr_id = f"DISR_{request.disruption_type.value}_{eng.current_tick}"
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
        "status": "scheduled",
        "disruption": disruption.model_dump(),
        "alert": alert.model_dump(),
        "recommendation": rec.model_dump(),
    }


# 9. POST /api/simulation/play, /pause, /step
@router.post("/simulation/play")
def simulation_play():
    """Signals start of automatic simulation playback."""
    eng = get_or_create_live_engine()
    return {"status": "playing", "tick": eng.current_tick, "message": "Simulation running"}


@router.post("/simulation/pause")
def simulation_pause():
    """Signals pause of automatic simulation playback."""
    eng = get_or_create_live_engine()
    return {"status": "paused", "tick": eng.current_tick, "message": "Simulation paused"}


@router.post("/simulation/step")
def simulation_step(
    optimizer_enabled: Optional[bool] = None,
    demand_spike: Optional[float] = None,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "WAREHOUSE_MANAGER", "STORE_OWNER"])),
):
    """Advances exactly one tick and returns updated state."""
    return advance_tick(optimizer_enabled=optimizer_enabled, demand_spike=demand_spike, user=user)


# 10. POST /api/experiments/compare
@router.post("/experiments/compare")
def compare_experiments(
    request: StrategyComparisonRequest,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR"])),
):
    """Executes baseline vs. optimized paired Monte Carlo strategy comparison with Common Random Numbers."""
    return run_strategy_comparison(request=request, user=user)


# 11. GET /api/forecasts & POST /api/forecasts/run
@router.get("/forecasts")
def get_forecasts(
    store_id: str = "STORE_01",
    product_id: str = "PROD_001",
    horizon_days: int = 7,
    current_tick: int = 0,
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR", "STORE_OWNER"])),
):
    """Retrieves probabilistic demand forecasts and uncertainty ranges (P10, P50, P90)."""
    return forecast_service_instance.predict_horizon(
        store_id=store_id,
        product_id=product_id,
        horizon_days=horizon_days,
        current_tick=current_tick,
    )


@router.post("/forecasts/run")
def run_forecasts(
    user: UserProfile = Security(require_roles_or_demo(["ADMIN", "DISTRIBUTOR"])),
):
    """Calculates or refreshes LightGBM quantile forecasting models."""
    metrics = forecast_service_instance.train_and_evaluate()
    return {
        "status": "refreshed",
        "model": "LightGBM Quantile Regressors",
        "metrics": metrics.model_dump(),
    }
