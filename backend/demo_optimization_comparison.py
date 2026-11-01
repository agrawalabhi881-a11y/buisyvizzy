"""
backend/demo_optimization_comparison.py
Head-to-Head Comparative Benchmark:
Baseline Policy vs. Optimized Policy (MILP Rebalancing + VRP Routing)
Under identical customer demand and stochastic disruptions.
"""

import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from contracts.seed_specs import (
    generate_seed_products,
    generate_seed_network,
    generate_seed_trucks,
    generate_initial_warehouse_inventories,
)
from contracts.models import DisruptionContract, DisruptionType
from backend.app.sim.engine import SupplyChainSimulationEngine


def run_comparison(seed: int = 1234, duration_days: int = 14):
    print("=" * 88)
    print("  SCM DIGITAL TWIN - PHASE 7 OPTIMIZATION COMPARATIVE BENCHMARK")
    print("  Evaluation: Baseline Policy vs. MILP Rebalancing & VRP Routing")
    print(f"  Configuration: {duration_days} Days, Seed={seed}, Disruption=Severe Supplier Blackout + Demand Spike")
    print("=" * 88)

    disruptions = [
        DisruptionContract(
            id="DISR_SUPPLIER_FAIL",
            disruption_type=DisruptionType.SUPPLIER_FAILURE,
            target_id="MFR_01",
            start_tick=3,
            duration_ticks=6,
            severity=3.0,  # 3x supplier lead time delay
            description="Upstream manufacturer equipment failure",
        ),
        DisruptionContract(
            id="DISR_LOCAL_SURGE",
            disruption_type=DisruptionType.DEMAND_SPIKE,
            target_id="STORE_01",
            start_tick=4,
            duration_ticks=4,
            severity=3.5,  # 3.5x demand spike on cluster 0
            description="Flash regional promotion spike",
        ),
    ]

    # Helper to set up network
    def setup_engine(optimizer_enabled: bool) -> SupplyChainSimulationEngine:
        eng = SupplyChainSimulationEngine(seed=seed, optimizer_enabled=optimizer_enabled)
        products = generate_seed_products(50)
        net_data = generate_seed_network()
        nodes = net_data["nodes"]
        trucks = generate_seed_trucks(10)
        inventories = generate_initial_warehouse_inventories(nodes, products, initial_stock_units=200.0)
        eng.initialize_network(products, nodes, trucks, inventories)
        for d in disruptions:
            eng.disruption_engine.schedule_disruption(d)
        return eng

    # 1. Run Baseline Policy
    eng_baseline = setup_engine(optimizer_enabled=False)
    for _ in range(duration_days):
        eng_baseline.run_tick()
    base_kpi = eng_baseline.kpi_accruer.snapshots[-1]

    # 2. Run Optimized Policy (MILP Rebalancing + VRP)
    eng_optimized = setup_engine(optimizer_enabled=True)
    for _ in range(duration_days):
        eng_optimized.run_tick()
    opt_kpi = eng_optimized.kpi_accruer.snapshots[-1]

    # Compute deltas
    unmet_reduction = base_kpi.total_unmet_units - opt_kpi.total_unmet_units
    fill_rate_delta = (opt_kpi.fill_rate - base_kpi.fill_rate) * 100
    profit_improvement = opt_kpi.net_profit - base_kpi.net_profit
    total_rebalanced = sum(
        p.total_units_rebalanced for p in eng_optimized.rebalancing_history
    )

    def fmt_cur_delta(val: float) -> str:
        sign = "+" if val >= 0 else "-"
        return f"{sign}${abs(val):,.2f}"

    def fmt_pct_delta(val: float) -> str:
        sign = "+" if val >= 0 else "-"
        return f"{sign}{abs(val):.2f}% pts"

    # Print Side-by-Side Comparison
    print(f"\n{'Metric':<34} | {'Baseline Policy':<18} | {'Optimized Policy':<18} | {'Delta / Improvement':<18}")
    print("-" * 96)
    print(f"{'Customer Demanded Units':<34} | {base_kpi.total_demanded_units:<18,.1f} | {opt_kpi.total_demanded_units:<18,.1f} | {'Identical (CRN)':<18}")
    print(f"{'Units Fulfilled':<34} | {base_kpi.total_fulfilled_units:<18,.1f} | {opt_kpi.total_fulfilled_units:<18,.1f} | {f'+{opt_kpi.total_fulfilled_units - base_kpi.total_fulfilled_units:,.1f} units':<18}")
    print(f"{'Unmet Demand (Lost Sales)':<34} | {base_kpi.total_unmet_units:<18,.1f} | {opt_kpi.total_unmet_units:<18,.1f} | {f'-{unmet_reduction:,.1f} units':<18}")
    print(f"{'Fill Rate (Service Level)':<34} | {base_kpi.fill_rate:<18.2%} | {opt_kpi.fill_rate:<18.2%} | {fmt_pct_delta(fill_rate_delta):<18}")
    print(f"{'Stockout Order Frequency':<34} | {base_kpi.stockout_frequency:<18.2%} | {opt_kpi.stockout_frequency:<18.2%} | {fmt_pct_delta((opt_kpi.stockout_frequency - base_kpi.stockout_frequency)*100):<18}")
    print(f"{'Stockout Penalties Accrued':<34} | ${base_kpi.total_unmet_demand_cost:<17,.2f} | ${opt_kpi.total_unmet_demand_cost:<17,.2f} | {fmt_cur_delta(opt_kpi.total_unmet_demand_cost - base_kpi.total_unmet_demand_cost):<18}")
    print(f"{'Total Gross Revenue':<34} | ${base_kpi.total_revenue:<17,.2f} | ${opt_kpi.total_revenue:<17,.2f} | {fmt_cur_delta(opt_kpi.total_revenue - base_kpi.total_revenue):<18}")
    print(f"{'Total Operating Cost':<34} | ${base_kpi.total_operating_cost:<17,.2f} | ${opt_kpi.total_operating_cost:<17,.2f} | {fmt_cur_delta(opt_kpi.total_operating_cost - base_kpi.total_operating_cost):<18}")
    print(f"{'Net Operational Profit':<34} | ${base_kpi.net_profit:<17,.2f} | ${opt_kpi.net_profit:<17,.2f} | {fmt_cur_delta(profit_improvement):<18}")
    print("-" * 96)
    print(f"Total Inter-Warehouse Stock Rebalanced: {total_rebalanced:,.1f} units")
    print(f"Unmet Demand Penalty Avoided:          ${base_kpi.total_unmet_demand_cost - opt_kpi.total_unmet_demand_cost:,.2f}")
    print("=" * 88 + "\n")


if __name__ == "__main__":
    run_comparison()
