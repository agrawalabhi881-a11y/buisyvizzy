"""
backend/tests/test_optimizers.py
Comprehensive test suite for Phase 7 Optimization modules:
Clustering, MILP Inventory Rebalancing, VRP Routing, and Dynamic Breakdown Failover.
"""

import numpy as np
from backend.app.optimizers.clustering import DemandWeightedKMeans
from backend.app.optimizers.rebalance import WarehouseRebalanceOptimizer
from backend.app.optimizers.vrp import CVRPOptimizer, haversine_km
from backend.app.optimizers.failover import DynamicFailoverEngine
from backend.app.sim.runner import MonteCarloScenarioRunner
from contracts.models import DisruptionContract, DisruptionType


def test_demand_weighted_clustering():
    store_ids = [f"STORE_{i:02d}" for i in range(1, 13)]
    # Coordinates in 3 distinct clusters: NY (lat 40.7), Chicago (lat 41.8), Atlanta (lat 33.7)
    coords = np.array([
        [40.71, -74.00], [40.75, -73.98], [40.68, -73.95], [40.80, -74.02],
        [41.87, -87.62], [41.90, -87.65], [41.80, -87.58], [41.95, -87.70],
        [33.74, -84.38], [33.78, -84.40], [33.68, -84.32], [33.82, -84.45],
    ])
    demands = np.array([25.0, 30.0, 15.0, 20.0, 45.0, 50.0, 35.0, 40.0, 10.0, 12.0, 8.0, 15.0])

    kmeans = DemandWeightedKMeans(n_clusters=3, seed=42)
    clusters = kmeans.fit_predict(store_ids, coords, demands)

    # 3 clusters generated
    assert len(clusters) == 3
    # All 12 stores assigned
    total_assigned = sum(len(stores) for stores in clusters.values())
    assert total_assigned == 12

    # Summaries check
    coord_map = {s: (coords[i, 0], coords[i, 1]) for i, s in enumerate(store_ids)}
    demand_map = {s: demands[i] for i, s in enumerate(store_ids)}
    summaries = kmeans.get_cluster_summaries(clusters, coord_map, demand_map)
    assert len(summaries) == 3
    assert all(s.total_demand_weight > 0 for s in summaries)


def test_rebalancing_optimizer_moves_surplus_to_deficit():
    optimizer = WarehouseRebalanceOptimizer()

    warehouses = {
        "WH_01": {"capacity": 5000.0, "current_stock": 3500.0},  # Has surplus
        "WH_02": {"capacity": 5000.0, "current_stock": 200.0},   # Near stockout
    }
    # WH_01 has 800 units (safety 100), surplus = 700
    # WH_02 has 20 units (reorder 300), deficit = 280
    inventories = {
        ("WH_01", "PROD_001"): {"stock": 800.0, "safety": 100.0, "reorder": 200.0},
        ("WH_02", "PROD_001"): {"stock": 20.0, "safety": 100.0, "reorder": 300.0},
    }
    products = {
        "PROD_001": {"penalty": 30.0, "unit_cost": 12.0},
    }
    dist_matrix = {
        ("WH_01", "WH_02"): 150.0,
        ("WH_02", "WH_01"): 150.0,
    }

    plan = optimizer.solve_rebalancing(
        tick=5,
        warehouses=warehouses,
        inventories=inventories,
        products=products,
        distance_matrix=dist_matrix,
    )

    assert plan.solver_status == "OPTIMAL"
    assert len(plan.transfers) == 1
    transfer = plan.transfers[0]

    # Transfer from WH_01 to WH_02 for exact deficit of 280 units
    assert transfer.from_warehouse_id == "WH_01"
    assert transfer.to_warehouse_id == "WH_02"
    assert transfer.product_id == "PROD_001"
    assert transfer.quantity_units == 280.0
    assert transfer.net_economic_benefit > 0.0
    assert plan.net_savings > 0.0


def test_vrp_clarke_wright_capacity_and_2opt():
    vrp = CVRPOptimizer(fuel_cost_per_km=1.25)

    wh_coord = (40.7128, -74.0060)  # Manhattan Depot
    store_coords = {
        "S1": (40.7589, -73.9851),   # Midtown
        "S2": (40.7829, -73.9654),   # Upper East
        "S3": (40.8075, -73.9626),   # Harlem
        "S4": (40.6782, -73.9442),   # Brooklyn Crown Heights
        "S5": (40.6500, -73.9496),   # Flatbush
    }
    # Demands totaling 750 units
    store_demands = {
        "S1": 150.0,
        "S2": 200.0,
        "S3": 100.0,
        "S4": 180.0,
        "S5": 120.0,
    }
    # Two trucks with capacity 450 units each
    trucks = [
        {"id": "TRUCK_A", "capacity": 450.0, "driver_salary": 140.0},
        {"id": "TRUCK_B", "capacity": 450.0, "driver_salary": 140.0},
    ]

    plan = vrp.solve_cluster_vrp(
        cluster_id=0,
        warehouse_id="WH_01",
        wh_coord=wh_coord,
        store_demands=store_demands,
        store_coords=store_coords,
        available_trucks=trucks,
    )

    # Routes must be generated without unassigned stores
    assert len(plan.unassigned_stores) == 0
    assert len(plan.routes) == 2

    # Every route must respect individual truck capacity of 450 units
    for route in plan.routes:
        assert route.total_cargo_units <= 450.0
        assert route.total_distance_km > 0.0
        assert route.estimated_fuel_cost > 0.0
        assert len(route.stops) > 0


def test_dynamic_breakdown_failover_rerouting():
    vrp = CVRPOptimizer()
    failover = DynamicFailoverEngine(vrp_solver=vrp)

    wh_coord = (40.71, -74.00)
    store_coords = {
        "S1": (40.75, -73.98),
        "S2": (40.78, -73.96),
        "S3": (40.82, -73.94),
    }
    store_demands = {"S1": 100.0, "S2": 100.0, "S3": 100.0}
    truck_a = {"id": "TRUCK_BROKEN", "capacity": 500.0, "driver_salary": 150.0}

    initial_plan = vrp.solve_cluster_vrp(
        cluster_id=0,
        warehouse_id="WH_01",
        wh_coord=wh_coord,
        store_demands=store_demands,
        store_coords=store_coords,
        available_trucks=[truck_a],
    )
    initial_route = initial_plan.routes[0]

    # Assume S1 was delivered (index 0), then TRUCK_BROKEN breaks down before S2 and S3
    completed = [0]
    idle_trucks = [
        {"id": "TRUCK_RESCUE", "lat": 40.76, "lon": -73.97, "capacity": 500.0, "driver_salary": 150.0}
    ]

    result = failover.handle_breakdown_and_reroute(
        tick=3,
        broken_truck_id="TRUCK_BROKEN",
        current_route=initial_route,
        completed_stop_indices=completed,
        cluster_id=0,
        idle_trucks=idle_trucks,
        store_coords=store_coords,
    )

    assert result is not None
    new_route, event = result

    # Verify rescue truck took over remaining 2 stops (S2 and S3)
    assert new_route.truck_id == "TRUCK_RESCUE"
    assert len(new_route.stops) == 2
    assert event.rescue_truck_id == "TRUCK_RESCUE"
    assert event.unvisited_stops_count == 2
    assert event.rescue_distance_km > 0.0
    assert event.delay_hours > 0.0


def test_simulation_rebalancing_reduces_unmet_demand():
    runner = MonteCarloScenarioRunner(base_seed=777)
    disruption = DisruptionContract(
        id="DISR_LOCAL_SPIKE",
        disruption_type=DisruptionType.DEMAND_SPIKE,
        target_id="STORE_01",
        start_tick=2,
        duration_ticks=5,
        severity=4.0,
    )

    # Run Baseline (no rebalancing)
    baseline_run = runner.run_single_scenario(
        seed=777,
        duration_ticks=12,
        disruptions=[disruption],
        optimizer_enabled=False,
    )
    # Run with MILP Rebalancing Enabled
    optimized_run = runner.run_single_scenario(
        seed=777,
        duration_ticks=12,
        disruptions=[disruption],
        optimizer_enabled=True,
    )

    base_final = baseline_run[-1]
    opt_final = optimized_run[-1]

    # Both ran on identical customer demand
    assert base_final.total_demanded_units == opt_final.total_demanded_units
    # Rebalancing should fulfill equal or more units and achieve equal or higher fill rate
    assert opt_final.total_fulfilled_units >= base_final.total_fulfilled_units
    assert opt_final.fill_rate >= base_final.fill_rate
