"""
contracts/models.py
Pydantic contracts defining the data interfaces across all phases.
Ensures zero-coupling between database migrations and in-memory simulation engine.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class NodeRole(str, Enum):
    MANUFACTURER = "MANUFACTURER"
    DISTRIBUTOR = "DISTRIBUTOR"
    WAREHOUSE = "WAREHOUSE"
    STORE = "STORE"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    PARTIAL = "PARTIAL"
    ESCALATED = "ESCALATED"
    CANCELLED = "CANCELLED"


class TruckStatus(str, Enum):
    IDLE = "IDLE"
    IN_TRANSIT = "IN_TRANSIT"
    BROKEN_DOWN = "BROKEN_DOWN"
    MAINTENANCE = "MAINTENANCE"


class DisruptionType(str, Enum):
    SUPPLIER_FAILURE = "SUPPLIER_FAILURE"
    DEMAND_SPIKE = "DEMAND_SPIKE"
    TRANSPORT_DELAY = "TRANSPORT_DELAY"
    WAREHOUSE_OUTAGE = "WAREHOUSE_OUTAGE"


class ProductContract(BaseModel):
    id: str
    sku: str
    name: str
    category: str = "General"
    unit_cost: float = Field(default=10.0, description="Cost to procure/manufacture")
    unit_price: float = Field(default=18.0, description="Retail selling price")
    holding_cost_per_day: float = Field(default=0.05, description="Holding cost per unit per tick")
    unmet_demand_penalty: float = Field(default=25.0, description="Penalty cost per unit of lost sales")


class NodeContract(BaseModel):
    id: str
    name: str
    role: NodeRole
    lat: float
    lon: float
    cluster_id: int
    max_capacity_units: float = Field(default=10000.0, description="Physical storage limit")
    operating_cost_per_day: float = Field(default=100.0, description="Fixed daily operational overhead")


class InventoryContract(BaseModel):
    node_id: str
    product_id: str
    current_stock: float = 0.0
    reserved_stock: float = 0.0
    safety_stock: float = 20.0
    reorder_point: float = 50.0      # 's' in (s, S) policy
    order_up_to: float = 200.0       # 'S' in (s, S) policy


class TruckContract(BaseModel):
    id: str
    name: str
    cluster_id: int
    capacity_units: float = 500.0
    status: TruckStatus = TruckStatus.IDLE
    current_lat: float
    current_lon: float
    fuel_cost_per_km: float = 1.25
    driver_daily_salary: float = 120.0
    speed_km_per_hour: float = 60.0


class OrderLineContract(BaseModel):
    product_id: str
    ordered_units: float
    fulfilled_units: float = 0.0
    unmet_units: float = 0.0


class OrderContract(BaseModel):
    id: str
    store_id: str
    warehouse_id: str
    status: OrderStatus = OrderStatus.PENDING
    created_tick: int
    fulfilled_tick: Optional[int] = None
    lines: List[OrderLineContract] = Field(default_factory=list)


class ShipmentContract(BaseModel):
    id: str
    order_id: str
    origin_id: str
    destination_id: str
    truck_id: Optional[str] = None
    dispatch_tick: int
    expected_arrival_tick: int
    actual_arrival_tick: Optional[int] = None
    distance_km: float = 50.0
    cargo_units: float = 0.0
    status: OrderStatus = OrderStatus.IN_TRANSIT


class DisruptionContract(BaseModel):
    id: str
    disruption_type: DisruptionType
    target_id: str               # node_id, product_id, or lane_id
    start_tick: int
    duration_ticks: int
    severity: float = 1.0        # Multiplier (e.g. 3.0x demand, or 0.0 capacity)
    description: str = ""


class ForecastContract(BaseModel):
    store_id: str
    product_id: str
    tick: int
    p10: float
    p50: float
    p90: float


class KPISnapshotContract(BaseModel):
    tick: int
    total_revenue: float = 0.0
    total_procurement_cost: float = 0.0
    total_holding_cost: float = 0.0
    total_transport_cost: float = 0.0
    total_unmet_demand_cost: float = 0.0
    total_operating_cost: float = 0.0
    net_profit: float = 0.0
    total_demanded_units: float = 0.0
    total_fulfilled_units: float = 0.0
    total_unmet_units: float = 0.0
    fill_rate: float = 1.0
    stockout_frequency: float = 0.0
    active_disruptions_count: int = 0
    network_in_recovery: bool = False
