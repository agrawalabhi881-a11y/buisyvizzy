"""SQLAlchemy models, imported together so Alembic sees complete metadata."""

from app.models.calendar import CalendarWeek, M5CalendarDate
from app.models.disruption import Disruption, DisruptionTarget
from app.models.distributor import Distributor
from app.models.driver import Driver
from app.models.inventory import Inventory
from app.models.kpi_snapshot import KPISnapshot
from app.models.manufacturer import Manufacturer
from app.models.order import Backorder, Order, OrderLine
from app.models.product import Product
from app.models.sales_record import DailySalesRecord
from app.models.sell_price import WeeklySellPrice
from app.models.shipment import Shipment, ShipmentLine
from app.models.store import Store
from app.models.trip import Trip
from app.models.truck import Truck
from app.models.unmet_demand import UnmetDemand
from app.models.warehouse import Warehouse

__all__ = [
    "Backorder",
    "CalendarWeek",
    "DailySalesRecord",
    "Disruption",
    "DisruptionTarget",
    "Distributor",
    "Driver",
    "Inventory",
    "KPISnapshot",
    "M5CalendarDate",
    "Manufacturer",
    "Order",
    "OrderLine",
    "Product",
    "Shipment",
    "ShipmentLine",
    "Store",
    "Trip",
    "Truck",
    "UnmetDemand",
    "Warehouse",
    "WeeklySellPrice",
]
