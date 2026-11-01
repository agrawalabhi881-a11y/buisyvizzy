"""
backend/app/api/routes/simulation.py
Simulation & Optimization execution endpoints:
Runs the discrete-event digital twin, injects disruptions, steps ticks,
and runs the paired Monte Carlo strategy comparison.
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, Security
from pydantic import BaseModel

from app.services.auth_service import UserProfile, require_roles, require_roles_or_demo, create_access_token
from app.sim.runner import MonteCarloScenarioRunner
from app.contracts.models import DisruptionContract, DisruptionType
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


@router.get("/demo-token")
def get_demo_token(role: str = "ADMIN"):
    """Convenience helper for testing in Swagger UI: generates a signed Bearer token."""
    token = create_access_token({"sub": f"demo_{role.lower()}", "role": role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": role,
        "instructions": "Copy access_token, click 'Authorize' at top of Swagger docs, and paste token.",
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
    """Advances the live digital twin simulation by 1 tick (day) and returns the state."""
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
