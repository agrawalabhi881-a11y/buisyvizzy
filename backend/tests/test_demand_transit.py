"""
backend/tests/test_demand_transit.py
Validates stochastic demand sampling, lognormal transit lead-times, and truck failover.
"""

import numpy as np
from backend.app.sim.demand import DemandGenerator
from backend.app.sim.transit import TransitEngine
from backend.app.sim.network import NetworkState, TruckState, ShipmentState
from contracts.models import TruckStatus, OrderStatus


def test_demand_generator_seasonality():
    gen = DemandGenerator(seed=123)
    # Day 5 (Saturday) multiplier should produce higher average demand than Day 0 (Monday)
    sat_demands = [
        gen.sample_demand("STORE_01", "PROD_001", "Beverages", tick=5)
        for _ in range(100)
    ]
    mon_demands = [
        gen.sample_demand("STORE_01", "PROD_001", "Beverages", tick=0)
        for _ in range(100)
    ]
    assert np.mean(sat_demands) > np.mean(mon_demands)


def test_stochastic_lead_time_distribution():
    engine = TransitEngine(seed=456)
    # Long-haul freight lane (1200 km) takes multiple days
    lead_times = [
        engine.sample_lead_time_ticks(distance_km=1200.0, speed_km_h=55.0)
        for _ in range(200)
    ]
    # Transit lead time should always be >= 1
    assert all(lt >= 1 for lt in lead_times)
    # Heavy tail: maximum sampled lead time should exceed mean
    assert max(lead_times) > np.mean(lead_times)


def test_truck_breakdown_and_cluster_failover():
    engine = TransitEngine(seed=789)
    net = NetworkState()

    # Create primary truck and standby truck in Cluster 0
    t1 = TruckState(
        id="TRUCK_01",
        name="Truck 1",
        cluster_id=0,
        capacity_units=500.0,
        status=TruckStatus.IN_TRANSIT,
        current_lat=40.71,
        current_lon=-74.00,
        fuel_cost_per_km=1.25,
        driver_daily_salary=120.0,
        speed_km_per_hour=60.0,
    )
    t2 = TruckState(
        id="TRUCK_02",
        name="Truck 2 Standby",
        cluster_id=0,
        capacity_units=500.0,
        status=TruckStatus.IDLE,
        current_lat=40.72,
        current_lon=-74.01,
        fuel_cost_per_km=1.25,
        driver_daily_salary=120.0,
        speed_km_per_hour=60.0,
    )
    net.trucks["TRUCK_01"] = t1
    net.trucks["TRUCK_02"] = t2

    shipment = ShipmentState(
        id="SHIP_01",
        order_id="ORD_01",
        origin_id="WH_01",
        destination_id="STORE_01",
        truck_id="TRUCK_01",
        dispatch_tick=1,
        expected_arrival_tick=2,
        distance_km=40.0,
        cargo_units=150.0,
        status=OrderStatus.IN_TRANSIT,
    )

    replacement = engine.execute_failover(t1, shipment, net)

    # Assert broken truck is marked BROKEN_DOWN
    assert t1.status == TruckStatus.BROKEN_DOWN
    # Assert replacement truck took over shipment and became IN_TRANSIT
    assert replacement is not None
    assert replacement.id == "TRUCK_02"
    assert replacement.status == TruckStatus.IN_TRANSIT
    assert shipment.truck_id == "TRUCK_02"
    # Delay penalty added
    assert shipment.expected_arrival_tick == 3
