"""
backend/demo_sim.py
Demonstration script showing live tick-by-tick simulation execution,
disruption injection (Admin), and baseline (s, S) recovery.
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


def run_demo():
    print("=" * 80)
    print("  SCM DIGITAL TWIN - LIVE 14-DAY SIMULATION RUN")
    print("  Baseline (s, S) Replenishment with Demand Spike Disruption")
    print("=" * 80)

    engine = SupplyChainSimulationEngine(seed=42)
    products = generate_seed_products(50)
    net_data = generate_seed_network()
    nodes = net_data["nodes"]
    trucks = generate_seed_trucks(10)
    inventories = generate_initial_warehouse_inventories(nodes, products, initial_stock_units=250.0)

    engine.initialize_network(products, nodes, trucks, inventories)

    # Admin injects a 3.5x demand spike on Day 4 for 3 days
    disruption = DisruptionContract(
        id="DISR_BLACK_FRIDAY",
        disruption_type=DisruptionType.DEMAND_SPIKE,
        target_id="ALL",
        start_tick=4,
        duration_ticks=3,
        severity=3.5,
        description="Surge promotion across all retail stores",
    )
    engine.disruption_engine.schedule_disruption(disruption)

    header = f"{'Tick':<6} | {'Disruptions':<12} | {'Demanded':<10} | {'Fulfilled':<10} | {'Fill Rate':<10} | {'Stockouts':<10} | {'Net Profit ($)':<14}"
    print(header)
    print("-" * len(header))

    for day in range(14):
        snap = engine.run_tick()
        disr_status = "SPIKE (3.5x)" if snap.active_disruptions_count > 0 else "Normal"
        print(
            f"Day {snap.tick:<2} | {disr_status:<12} | {snap.total_demanded_units:<10.1f} | "
            f"{snap.total_fulfilled_units:<10.1f} | {snap.fill_rate:<10.2%} | "
            f"{snap.stockout_frequency:<10.2%} | ${snap.net_profit:<13,.2f}"
        )

    print("-" * len(header))
    print(f"\nSimulation complete.")
    print(f"Total Revenue:         ${snap.total_revenue:,.2f}")
    print(f"Total Operating Cost:  ${snap.total_operating_cost:,.2f}")
    print(f"Final Cumulative Fill: {snap.fill_rate:.2%}")
    print(f"Total Unmet Demand:    {snap.total_unmet_units:,.1f} units (${snap.total_unmet_demand_cost:,.2f} penalty)")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
