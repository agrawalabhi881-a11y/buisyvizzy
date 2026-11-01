"""
contracts/seed_specs.py
Deterministic network topology specification.
Generates exact configuration for 1 Mfr, 2 Dist, 3 Warehouses, 20 Stores, 50 Products, 10 Trucks.
"""

from typing import List, Dict
import numpy as np
from contracts.models import (
    NodeRole,
    TruckStatus,
    ProductContract,
    NodeContract,
    InventoryContract,
    TruckContract,
)


def generate_seed_products(count: int = 50) -> List[ProductContract]:
    categories = ["Beverages", "Snacks", "Household", "Personal Care", "Dairy"]
    products = []
    for i in range(1, count + 1):
        cat = categories[(i - 1) % len(categories)]
        unit_cost = round(float(5.0 + (i % 15) * 2.5), 2)
        unit_price = round(unit_cost * 1.75, 2)
        holding_cost = round(unit_cost * 0.005, 3)
        penalty = round(unit_price * 1.5, 2)
        products.append(
            ProductContract(
                id=f"PROD_{i:03d}",
                sku=f"SKU-{cat[:3].upper()}-{i:03d}",
                name=f"{cat} Item {i}",
                category=cat,
                unit_cost=unit_cost,
                unit_price=unit_price,
                holding_cost_per_day=holding_cost,
                unmet_demand_penalty=penalty,
            )
        )
    return products


def generate_seed_network() -> Dict[str, List[NodeContract]]:
    """
    Creates 1 Mfr, 2 Dist, 3 Warehouses, 20 Stores across 3 spatial clusters:
      Cluster 0: Northeast (Center ~ 40.71, -74.00)
      Cluster 1: Midwest   (Center ~ 41.87, -87.62)
      Cluster 2: South     (Center ~ 33.74, -84.38)
    """
    nodes: List[NodeContract] = []

    # 1 Manufacturer (Centrally located supplier)
    nodes.append(
        NodeContract(
            id="MFR_01",
            name="Apex National Manufacturing Plant",
            role=NodeRole.MANUFACTURER,
            lat=39.9612,
            lon=-82.9988,  # Columbus, OH
            cluster_id=-1,
            max_capacity_units=1000000.0,
            operating_cost_per_day=2000.0,
        )
    )

    # 2 Distributors
    nodes.append(
        NodeContract(
            id="DIST_01",
            name="Eastern Regional Distribution Hub",
            role=NodeRole.DISTRIBUTOR,
            lat=40.0583,
            lon=-74.4057,  # NJ
            cluster_id=0,
            max_capacity_units=200000.0,
            operating_cost_per_day=800.0,
        )
    )
    nodes.append(
        NodeContract(
            id="DIST_02",
            name="Central & Southern Distribution Hub",
            role=NodeRole.DISTRIBUTOR,
            lat=36.1627,
            lon=-86.7816,  # Nashville, TN
            cluster_id=1,
            max_capacity_units=200000.0,
            operating_cost_per_day=800.0,
        )
    )

    # 3 Warehouses (One per primary territory)
    wh_specs = [
        ("WH_01", "Northeast Primary Warehouse", 40.7128, -74.0060, 0, 40000.0),
        ("WH_02", "Midwest Logistics Warehouse", 41.8781, -87.6298, 1, 45000.0),
        ("WH_03", "Southeast Regional Warehouse", 33.7490, -84.3880, 2, 35000.0),
    ]
    for wh_id, name, lat, lon, cluster_id, cap in wh_specs:
        nodes.append(
            NodeContract(
                id=wh_id,
                name=name,
                role=NodeRole.WAREHOUSE,
                lat=lat,
                lon=lon,
                cluster_id=cluster_id,
                max_capacity_units=cap,
                operating_cost_per_day=450.0,
            )
        )

    # 20 Stores distributed across the 3 clusters (7 in Cl 0, 7 in Cl 1, 6 in Cl 2)
    store_offsets = [
        # Cluster 0: Northeast (7 stores)
        (0, 40.75, -73.98), (0, 40.67, -73.94), (0, 40.82, -73.92),
        (0, 40.71, -74.17), (0, 40.91, -74.07), (0, 40.57, -74.15), (0, 41.05, -73.54),
        # Cluster 1: Midwest (7 stores)
        (1, 41.88, -87.63), (1, 41.79, -87.59), (1, 41.97, -87.71),
        (1, 42.04, -87.68), (1, 41.83, -87.82), (1, 41.70, -87.75), (1, 41.90, -88.08),
        # Cluster 2: Southeast (6 stores)
        (2, 33.75, -84.39), (2, 33.84, -84.37), (2, 33.65, -84.42),
        (2, 33.88, -84.51), (2, 33.71, -84.28), (2, 33.95, -84.13),
    ]

    for idx, (cluster_id, lat, lon) in enumerate(store_offsets, start=1):
        nodes.append(
            NodeContract(
                id=f"STORE_{idx:02d}",
                name=f"Retail Store #{idx:02d}",
                role=NodeRole.STORE,
                lat=lat,
                lon=lon,
                cluster_id=cluster_id,
                max_capacity_units=3000.0,
                operating_cost_per_day=75.0,
            )
        )

    return {"nodes": nodes}


def generate_seed_trucks(count: int = 10) -> List[TruckContract]:
    """10 delivery trucks partitioned across the 3 clusters."""
    trucks = []
    # Cluster assignment: 4 trucks in Cl 0, 3 trucks in Cl 1, 3 trucks in Cl 2
    assignments = [0, 0, 0, 0, 1, 1, 1, 2, 2, 2]
    cluster_centers = {
        0: (40.7128, -74.0060),
        1: (41.8781, -87.6298),
        2: (33.7490, -84.3880),
    }

    for i in range(count):
        cluster_id = assignments[i]
        base_lat, base_lon = cluster_centers[cluster_id]
        trucks.append(
            TruckContract(
                id=f"TRUCK_{i+1:02d}",
                name=f"Fleet Truck #{i+1:02d} (Cl {cluster_id})",
                cluster_id=cluster_id,
                capacity_units=600.0,
                status=TruckStatus.IDLE,
                current_lat=base_lat + (i * 0.005),
                current_lon=base_lon + (i * 0.005),
                fuel_cost_per_km=1.25,
                driver_daily_salary=150.0,
                speed_km_per_hour=55.0,
            )
        )
    return trucks


def generate_initial_warehouse_inventories(
    warehouses: List[NodeContract],
    products: List[ProductContract],
    initial_stock_units: float = 250.0,
) -> List[InventoryContract]:
    """Generates initial baseline inventory positions for each warehouse and product."""
    records = []
    for wh in warehouses:
        if wh.role != NodeRole.WAREHOUSE:
            continue
        for prod in products:
            records.append(
                InventoryContract(
                    node_id=wh.id,
                    product_id=prod.id,
                    current_stock=initial_stock_units,
                    reserved_stock=0.0,
                    safety_stock=40.0,
                    reorder_point=100.0,    # s
                    order_up_to=450.0,      # S
                )
            )
    return records
