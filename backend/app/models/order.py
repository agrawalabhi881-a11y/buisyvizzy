from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
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
from app.models.mixins import CreatedAtMixin, PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.distributor import Distributor
    from app.models.manufacturer import Manufacturer
    from app.models.product import Product
    from app.models.shipment import Shipment, ShipmentLine
    from app.models.store import Store
    from app.models.unmet_demand import UnmetDemand
    from app.models.warehouse import Warehouse


class Order(PrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "(order_type = 'store_order' AND source_store_id IS NOT NULL "
            "AND source_warehouse_id IS NULL AND source_distributor_id IS NULL "
            "AND destination_distributor_id IS NOT NULL AND destination_manufacturer_id IS NULL) OR "
            "(order_type = 'procurement' AND source_store_id IS NULL "
            "AND source_warehouse_id IS NULL AND source_distributor_id IS NOT NULL "
            "AND destination_distributor_id IS NULL AND destination_manufacturer_id IS NOT NULL) OR "
            "(order_type = 'warehouse_replenishment' AND source_store_id IS NULL "
            "AND source_warehouse_id IS NOT NULL AND source_distributor_id IS NULL "
            "AND destination_distributor_id IS NOT NULL AND destination_manufacturer_id IS NULL)",
            name="ck_order_flow_endpoints",
        ),
        CheckConstraint(
            "order_type IN ('store_order', 'procurement', 'warehouse_replenishment')",
            name="ck_order_type",
        ),
        CheckConstraint(
            "status IN ('draft', 'submitted', 'confirmed', 'partially_fulfilled', "
            "'fulfilled', 'cancelled', 'expired')",
            name="ck_order_status",
        ),
        CheckConstraint(
            "expected_delivery_date IS NULL OR expected_delivery_date >= order_date",
            name="ck_order_expected_after_order",
        ),
        UniqueConstraint("id", "source_store_id"),
        ForeignKeyConstraint(
            ["source_store_id", "destination_distributor_id"],
            ["stores.id", "stores.distributor_id"],
            name="fk_order_store_distributor",
        ),
        ForeignKeyConstraint(
            ["source_warehouse_id", "destination_distributor_id"],
            ["warehouses.id", "warehouses.distributor_id"],
            name="fk_order_warehouse_distributor",
        ),
        ForeignKeyConstraint(
            ["source_distributor_id", "destination_manufacturer_id"],
            ["distributors.id", "distributors.manufacturer_id"],
            name="fk_order_distributor_manufacturer",
        ),
    )

    order_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    order_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    source_store_id: Mapped[int | None] = mapped_column(
        ForeignKey("stores.id"), index=True
    )
    source_warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id"), index=True
    )
    source_distributor_id: Mapped[int | None] = mapped_column(
        ForeignKey("distributors.id"), index=True
    )
    destination_distributor_id: Mapped[int | None] = mapped_column(
        ForeignKey("distributors.id"), index=True
    )
    destination_manufacturer_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturers.id"), index=True
    )
    status: Mapped[str] = mapped_column(String(24), default="draft", nullable=False)
    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expected_delivery_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    actual_delivery_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    source_store: Mapped[Store | None] = relationship(
        back_populates="orders", foreign_keys=[source_store_id]
    )
    source_warehouse: Mapped[Warehouse | None] = relationship(
        back_populates="source_orders", foreign_keys=[source_warehouse_id]
    )
    source_distributor: Mapped[Distributor | None] = relationship(
        back_populates="orders", foreign_keys=[source_distributor_id]
    )
    destination_distributor: Mapped[Distributor | None] = relationship(
        foreign_keys=[destination_distributor_id]
    )
    destination_manufacturer: Mapped[Manufacturer | None] = relationship(
        foreign_keys=[destination_manufacturer_id]
    )
    lines: Mapped[list[OrderLine]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    shipments: Mapped[list[Shipment]] = relationship(back_populates="order")
    unmet_demand: Mapped[list[UnmetDemand]] = relationship(
        back_populates="order", foreign_keys="UnmetDemand.order_id"
    )


class OrderLine(PrimaryKeyMixin, Base):
    __tablename__ = "order_lines"
    __table_args__ = (
        CheckConstraint(
            "quantity_requested > 0", name="ck_order_line_requested_positive"
        ),
        CheckConstraint(
            "quantity_fulfilled >= 0", name="ck_order_line_fulfilled_nonnegative"
        ),
        CheckConstraint(
            "quantity_fulfilled <= quantity_requested",
            name="ck_order_line_fulfilled_not_above_requested",
        ),
        CheckConstraint("unit_price >= 0", name="ck_order_line_unit_price_nonnegative"),
        UniqueConstraint("order_id", "product_id", name="uq_order_line_product"),
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity_requested: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    quantity_fulfilled: Mapped[float] = mapped_column(
        Numeric(14, 3), default=0, nullable=False
    )
    backorder_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    unit_price: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)

    order: Mapped[Order] = relationship(back_populates="lines")
    product: Mapped[Product] = relationship(back_populates="order_lines")
    backorder: Mapped[Backorder | None] = relationship(
        back_populates="order_line", cascade="all, delete-orphan", uselist=False
    )
    shipment_lines: Mapped[list[ShipmentLine]] = relationship(
        back_populates="order_line"
    )


class Backorder(PrimaryKeyMixin, Base):
    __tablename__ = "backorders"
    __table_args__ = (
        CheckConstraint(
            "remaining_quantity > 0", name="ck_backorder_remaining_positive"
        ),
        CheckConstraint(
            "status IN ('open', 'fulfilled', 'expired', 'cancelled')",
            name="ck_backorder_status",
        ),
    )

    order_line_id: Mapped[int] = mapped_column(
        ForeignKey("order_lines.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    remaining_quantity: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(16), default="open", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    order_line: Mapped[OrderLine] = relationship(back_populates="backorder")
