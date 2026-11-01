"""
backend/app/api/routes/simulation.py
Simulation & Optimization execution endpoints:
Runs the discrete-event digital twin, injects disruptions, and runs the MILP optimizer.
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, Security
from pydantic import BaseModel

from app.services.auth_service import UserProfile, require_roles
from app.sim.runner import MonteCarloScenarioRunner
from app.contracts.models import DisruptionContract, DisruptionType
from app.optimizers.rebalance import WarehouseRebalanceOptimizer
from app.sim.strategy_comparison import (
    ScenarioType,
    StrategyComparisonEvaluator,
    DisruptionScenarioRegistry,
    ScenarioComparisonReport,
)

router = APIRouter(prefix="/simulation", tags=["Simulation & Optimization"])


class SimulationRunRequest(BaseModel):
    seed: int = 42
    duration_ticks: int = 14
    optimizer_enabled: bool = False
    demand_spike_severity: Optional[float] = None
    supplier_failure_severity: Optional[float] = None


@router.post("/run")
def run_simulation(
    request: SimulationRunRequest,
    user: UserProfile = Security(require_roles(["ADMIN", "DISTRIBUTOR"])),
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
    user: UserProfile = Security(require_roles(["ADMIN", "DISTRIBUTOR"])),
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
