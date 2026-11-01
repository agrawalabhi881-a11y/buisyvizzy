"""
backend/tests/test_sim_engine.py
Tests the end-to-end discrete-event simulation engine and tick loop.
"""

from contracts.seed_specs import (
    generate_seed_products,
    generate_seed_network,
    generate_seed_trucks,
    generate_initial_warehouse_inventories,
)
from backend.app.sim.engine import SupplyChainSimulationEngine


def test_simulation_runs_and_accrues_kpis():
    engine = SupplyChainSimulationEngine(seed=999)

    products = generate_seed_products(20)
    net_data = generate_seed_network()
    nodes = net_data["nodes"]
    trucks = generate_seed_trucks(6)
    inventories = generate_initial_warehouse_inventories(nodes, products, initial_stock_units=200.0)

    engine.initialize_network(products, nodes, trucks, inventories)

    # Run for 7 ticks (1 full week)
    snapshots = engine.run_simpy_simulation(total_ticks=7)

    assert len(snapshots) == 7
    final_snap = snapshots[-1]

    # KPIs must be non-zero and accumulated
    assert final_snap.total_revenue > 0.0
    assert final_snap.total_operating_cost > 0.0
    assert final_snap.total_demanded_units > 0.0
    assert final_snap.total_fulfilled_units > 0.0
    assert 0.0 <= final_snap.fill_rate <= 1.0

    # Orders and active/delivered shipments must have moved
    assert len(engine.network.orders) > 0
    assert len(engine.network.delivered_shipments) > 0
