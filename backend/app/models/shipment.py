from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Computed,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.manufacturer import Manufacturer
    from app.models.order import Order, OrderLine
    from app.models.store import Store
    from app.models.trip import Trip
    from app.models.truck import Truck
    from app.models.warehouse import Warehouse


class Shipment(PrimaryKeyMixin, Base):
    __tablename__ = "shipments"
    __table_args__ = (
        UniqueConstraint("id", "distributor_id"),
        CheckConstraint(
            "(origin_warehouse_id IS NOT NULL AND origin_manufacturer_id IS NULL) OR "
            "(origin_warehouse_id IS NULL AND origin_manufacturer_id IS NOT NULL)",
            name="ck_shipment_exactly_one_origin",
        ),
        CheckConstraint(
            "(destination_store_id IS NOT NULL AND destination_warehouse_id IS NULL) OR "
            "(destination_store_id IS NULL AND destination_warehouse_id IS NOT NULL)",
            name="ck_shipment_exactly_one_destination",
        ),
        CheckConstraint(
            "status IN ('planned', 'dispatched', 'in_transit', 'delivered', 'delayed', 'cancelled')",
            name="ck_shipment_status",
        ),
        CheckConstraint(
            "estimated_arrival IS NULL OR dispatch_time IS NULL OR estimated_arrival >= dispatch_time",
            name="ck_shipment_eta_after_dispatch",
        ),
        ForeignKeyConstraint(
            ["warehouse_id", "distributor_id"],
            ["warehouses.id", "warehouses.distributor_id"],
            name="fk_shipment_warehouse_distributor",
        ),
        ForeignKeyConstraint(
            ["truck_id", "distributor_id"],
            ["trucks.id", "trucks.distributor_id"],
            name="fk_shipment_truck_distributor",
        ),
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    truck_id: Mapped[int] = mapped_column(
        ForeignKey("trucks.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    distributor_id: Mapped[int] = mapped_column(
        ForeignKey("distributors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    origin_warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="RESTRICT")
    )
    origin_manufacturer_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturers.id", ondelete="RESTRICT")
    )
    destination_store_id: Mapped[int | None] = mapped_column(
        ForeignKey("stores.id", ondelete="RESTRICT")
    )
    destination_warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(20), default="planned", nullable=False)
    dispatch_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estimated_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    order: Mapped[Order] = relationship(back_populates="shipments")
    warehouse: Mapped[Warehouse] = relationship(
        back_populates="shipments", foreign_keys=[warehouse_id]
    )
    truck: Mapped[Truck] = relationship(
        back_populates="shipments", foreign_keys=[truck_id]
    )
    origin_warehouse: Mapped[Warehouse | None] = relationship(
        foreign_keys=[origin_warehouse_id]
    )
    origin_manufacturer: Mapped[Manufacturer | None] = relationship(
        foreign_keys=[origin_manufacturer_id]
    )
    destination_store: Mapped[Store | None] = relationship(back_populates="shipments")
    destination_warehouse: Mapped[Warehouse | None] = relationship(
        foreign_keys=[destination_warehouse_id]
    )
    trips: Mapped[list[Trip]] = relationship(
        back_populates="shipment", foreign_keys="Trip.shipment_id"
    )
    lines: Mapped[list[ShipmentLine]] = relationship(
        back_populates="shipment", cascade="all, delete-orphan"
    )


class ShipmentLine(PrimaryKeyMixin, Base):
    """Tracks shipped quantities outside warehouse/store on-hand inventory."""

    __tablename__ = "shipment_lines"
    __table_args__ = (
        CheckConstraint(
            "quantity_shipped > 0", name="ck_shipment_line_shipped_positive"
        ),
        CheckConstraint(
            "quantity_delivered >= 0", name="ck_shipment_line_delivered_nonnegative"
        ),
        CheckConstraint(
            "quantity_delivered <= quantity_shipped",
            name="ck_shipment_line_delivered_not_above_shipped",
        ),
        UniqueConstraint(
            "shipment_id", "order_line_id", name="uq_shipment_line_order_line"
        ),
    )

    shipment_id: Mapped[int] = mapped_column(
        ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_line_id: Mapped[int] = mapped_column(
        ForeignKey("order_lines.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity_shipped: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    quantity_delivered: Mapped[float] = mapped_column(
        Numeric(14, 3), default=0, nullable=False
    )
    quantity_in_transit: Mapped[float] = mapped_column(
        Numeric(14, 3),
        Computed("quantity_shipped - quantity_delivered", persisted=True),
    )

    shipment: Mapped[Shipment] = relationship(back_populates="lines")
    order_line: Mapped[OrderLine] = relationship(back_populates="shipment_lines")
