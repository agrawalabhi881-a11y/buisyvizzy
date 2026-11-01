"""
backend/app/sim/network.py
In-memory domain models for the simulation state.
Zero database dependency - operates purely on dataclasses and high-performance dict lookups.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math
from contracts.models import (
    NodeRole,
    OrderStatus,
    TruckStatus,
    ProductContract,
    NodeContract,
    InventoryContract,
    TruckContract,
)


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two geocoordinates in kilometers."""
    r = 6371.0  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 2)


@dataclass
class ProductState:
    id: str
    sku: str
    name: str
    category: str
    unit_cost: float
    unit_price: float
    holding_cost_per_day: float
    unmet_demand_penalty: float


@dataclass
class InventoryState:
    node_id: str
    product_id: str
    current_stock: float
    reserved_stock: float = 0.0
    safety_stock: float = 20.0
    reorder_point: float = 50.0   # s
    order_up_to: float = 200.0    # S

    @property
    def available_stock(self) -> float:
        return max(0.0, self.current_stock - self.reserved_stock)


@dataclass
class NodeState:
    id: str
    name: str
    role: NodeRole
    lat: float
    lon: float
    cluster_id: int
    max_capacity_units: float
    operating_cost_per_day: float
    # product_id -> InventoryState
    inventory: Dict[str, InventoryState] = field(default_factory=dict)

    @property
    def total_current_stock(self) -> float:
        return sum(inv.current_stock for inv in self.inventory.values())

    @property
    def remaining_capacity(self) -> float:
        return max(0.0, self.max_capacity_units - self.total_current_stock)


@dataclass
class TruckState:
    id: str
    name: str
    cluster_id: int
    capacity_units: float
    status: TruckStatus
    current_lat: float
    current_lon: float
    fuel_cost_per_km: float
    driver_daily_salary: float
    speed_km_per_hour: float
    current_shipment_id: Optional[str] = None
    total_km_travelled: float = 0.0
    total_fuel_cost: float = 0.0
    total_salaries_paid: float = 0.0


@dataclass
class OrderLineState:
    product_id: str
    ordered_units: float
    fulfilled_units: float = 0.0
    unmet_units: float = 0.0


@dataclass
class OrderState:
    id: str
    store_id: str
    warehouse_id: str
    status: OrderStatus
    created_tick: int
    fulfilled_tick: Optional[int] = None
    lines: List[OrderLineState] = field(default_factory=list)

    @property
    def total_ordered_units(self) -> float:
        return sum(l.ordered_units for l in self.lines)

    @property
    def total_fulfilled_units(self) -> float:
        return sum(l.fulfilled_units for l in self.lines)

    @property
    def total_unmet_units(self) -> float:
        return sum(l.unmet_units for l in self.lines)


@dataclass
class ShipmentState:
    id: str
    order_id: str
    origin_id: str
    destination_id: str
    truck_id: Optional[str]
    dispatch_tick: int
    expected_arrival_tick: int
    distance_km: float
    cargo_units: float
    status: OrderStatus
    lines: List[OrderLineState] = field(default_factory=list)


class NetworkState:
    """The complete in-memory graph of supply chain nodes, trucks, and relationships."""

    def __init__(self):
        self.products: Dict[str, ProductState] = {}
        self.nodes: Dict[str, NodeState] = {}
        self.trucks: Dict[str, TruckState] = {}
        self.orders: Dict[str, OrderState] = {}
        self.active_shipments: Dict[str, ShipmentState] = {}
        self.delivered_shipments: List[ShipmentState] = []
        # Fast lookup mapping: store_id -> nearest warehouse_id
        self.store_to_warehouse: Dict[str, str] = {}
        # Cluster mapping: cluster_id -> list of node_ids
        self.clusters: Dict[int, List[str]] = {}

    def load_from_contracts(
        self,
        products: List[ProductContract],
        nodes: List[NodeContract],
        trucks: List[TruckContract],
        inventories: List[InventoryContract],
    ):
        """Populates the in-memory graph from Pydantic contracts."""
        for p in products:
            self.products[p.id] = ProductState(
                id=p.id,
                sku=p.sku,
                name=p.name,
                category=p.category,
                unit_cost=p.unit_cost,
                unit_price=p.unit_price,
                holding_cost_per_day=p.holding_cost_per_day,
                unmet_demand_penalty=p.unmet_demand_penalty,
            )

        for n in nodes:
            node_state = NodeState(
                id=n.id,
                name=n.name,
                role=n.role,
                lat=n.lat,
                lon=n.lon,
                cluster_id=n.cluster_id,
                max_capacity_units=n.max_capacity_units,
                operating_cost_per_day=n.operating_cost_per_day,
            )
            self.nodes[n.id] = node_state
            if n.cluster_id not in self.clusters:
                self.clusters[n.cluster_id] = []
            self.clusters[n.cluster_id].append(n.id)

        for inv in inventories:
            if inv.node_id in self.nodes:
                self.nodes[inv.node_id].inventory[inv.product_id] = InventoryState(
                    node_id=inv.node_id,
                    product_id=inv.product_id,
                    current_stock=inv.current_stock,
                    reserved_stock=inv.reserved_stock,
                    safety_stock=inv.safety_stock,
                    reorder_point=inv.reorder_point,
                    order_up_to=inv.order_up_to,
                )

        for t in trucks:
            self.trucks[t.id] = TruckState(
                id=t.id,
                name=t.name,
                cluster_id=t.cluster_id,
                capacity_units=t.capacity_units,
                status=t.status,
                current_lat=t.current_lat,
                current_lon=t.current_lon,
                fuel_cost_per_km=t.fuel_cost_per_km,
                driver_daily_salary=t.driver_daily_salary,
                speed_km_per_hour=t.speed_km_per_hour,
            )

        # Wire each store to its nearest warehouse
        warehouses = [n for n in self.nodes.values() if n.role == NodeRole.WAREHOUSE]
        for n in self.nodes.values():
            if n.role == NodeRole.STORE:
                # Find closest warehouse by haversine distance
                closest_wh = min(
                    warehouses,
                    key=lambda wh: haversine_distance_km(n.lat, n.lon, wh.lat, wh.lon),
                )
                self.store_to_warehouse[n.id] = closest_wh.id

    def get_distance(self, node_id_1: str, node_id_2: str) -> float:
        n1 = self.nodes.get(node_id_1)
        n2 = self.nodes.get(node_id_2)
        if not n1 or not n2:
            return 50.0
        return haversine_distance_km(n1.lat, n1.lon, n2.lat, n2.lon)
