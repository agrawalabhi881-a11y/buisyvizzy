"""
backend/app/sim/runner.py
Multi-seed scenario runner for reproducible Monte Carlo simulations.
Enables fair, paired-difference evaluations between baseline and optimized policies.
"""

from typing import Dict, List, Optional
import numpy as np
from pydantic import BaseModel, Field

from contracts.seed_specs import (
    generate_seed_products,
    generate_seed_network,
    generate_seed_trucks,
    generate_initial_warehouse_inventories,
)
from contracts.models import DisruptionContract, KPISnapshotContract
from backend.app.sim.engine import SupplyChainSimulationEngine


class ScenarioComparisonReport(BaseModel):
    strategy_name: str
    num_runs: int
    duration_ticks: int
    avg_total_cost: float
    ci_95_total_cost: float
    avg_fill_rate: float
    ci_95_fill_rate: float
    avg_stockout_freq: float
    avg_unmet_units: float
    avg_net_profit: float


class MonteCarloScenarioRunner:
    """Executes multi-run Monte Carlo batches with fixed random seeds."""

    def __init__(self, base_seed: int = 1000):
        self.base_seed = base_seed

    def run_single_scenario(
        self,
        seed: int,
        duration_ticks: int = 30,
        disruptions: Optional[List[DisruptionContract]] = None,
        custom_history: Optional[Dict[tuple, float]] = None,
    ) -> List[KPISnapshotContract]:
        """Runs a single simulation run using a deterministic seed."""
        engine = SupplyChainSimulationEngine(seed=seed)

        # Seed network topology
        products = generate_seed_products(50)
        net_data = generate_seed_network()
        nodes = net_data["nodes"]
        trucks = generate_seed_trucks(10)
        inventories = generate_initial_warehouse_inventories(nodes, products, initial_stock_units=300.0)

        engine.initialize_network(products, nodes, trucks, inventories)

        # Optional historical replay data
        if custom_history:
            engine.demand_gen.set_historical_data(custom_history)

        # Schedule disruptions
        if disruptions:
            for d in disruptions:
                engine.disruption_engine.schedule_disruption(d)

        # Run SimPy simulation
        snapshots = engine.run_simpy_simulation(total_ticks=duration_ticks)
        return snapshots

    def run_monte_carlo_batch(
        self,
        strategy_name: str = "Baseline (s, S)",
        num_seeds: int = 10,
        duration_ticks: int = 30,
        disruptions: Optional[List[DisruptionContract]] = None,
    ) -> ScenarioComparisonReport:
        """Runs N reproducible Monte Carlo replications and accrues confidence intervals."""
        costs: List[float] = []
        fill_rates: List[float] = []
        stockout_freqs: List[float] = []
        unmet_units: List[float] = []
        profits: List[float] = []

        for i in range(num_seeds):
            seed = self.base_seed + i
            snapshots = self.run_single_scenario(
                seed=seed,
                duration_ticks=duration_ticks,
                disruptions=disruptions,
            )
            final_snap = snapshots[-1]
            costs.append(final_snap.total_operating_cost)
            fill_rates.append(final_snap.fill_rate)
            stockout_freqs.append(final_snap.stockout_frequency)
            unmet_units.append(final_snap.total_unmet_units)
            profits.append(final_snap.net_profit)

        n = float(num_seeds)
        mean_cost = float(np.mean(costs))
        std_cost = float(np.std(costs, ddof=1)) if n > 1 else 0.0
        ci_cost = 1.96 * (std_cost / np.sqrt(n)) if n > 1 else 0.0

        mean_fill = float(np.mean(fill_rates))
        std_fill = float(np.std(fill_rates, ddof=1)) if n > 1 else 0.0
        ci_fill = 1.96 * (std_fill / np.sqrt(n)) if n > 1 else 0.0

        return ScenarioComparisonReport(
            strategy_name=strategy_name,
            num_runs=num_seeds,
            duration_ticks=duration_ticks,
            avg_total_cost=round(mean_cost, 2),
            ci_95_total_cost=round(ci_cost, 2),
            avg_fill_rate=round(mean_fill, 4),
            ci_95_fill_rate=round(ci_fill, 4),
            avg_stockout_freq=round(float(np.mean(stockout_freqs)), 4),
            avg_unmet_units=round(float(np.mean(unmet_units)), 1),
            avg_net_profit=round(float(np.mean(profits)), 2),
        )
