from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import CreatedAtMixin, PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.distributor import Distributor
    from app.models.inventory import Inventory
    from app.models.kpi_snapshot import KPISnapshot
    from app.models.order import Order
    from app.models.shipment import Shipment
    from app.models.store import Store


class Warehouse(PrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "warehouses"
    __table_args__ = (
        CheckConstraint("storage_capacity > 0", name="ck_warehouse_capacity_positive"),
        CheckConstraint(
            "latitude BETWEEN -90 AND 90",
            name="ck_warehouse_latitude",
        ),
        CheckConstraint(
            "longitude BETWEEN -180 AND 180",
            name="ck_warehouse_longitude",
        ),
        UniqueConstraint("id", "distributor_id"),
    )

    distributor_id: Mapped[int] = mapped_column(
        ForeignKey("distributors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    storage_capacity: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)

    distributor: Mapped[Distributor] = relationship(back_populates="warehouses")
    inventory: Mapped[list[Inventory]] = relationship(back_populates="warehouse")
    stores: Mapped[list[Store]] = relationship(
        back_populates="assigned_warehouse", foreign_keys="Store.assigned_warehouse_id"
    )
    source_orders: Mapped[list[Order]] = relationship(
        back_populates="source_warehouse", foreign_keys="Order.source_warehouse_id"
    )
    shipments: Mapped[list[Shipment]] = relationship(
        back_populates="warehouse", foreign_keys="Shipment.warehouse_id"
    )
    kpi_snapshots: Mapped[list[KPISnapshot]] = relationship(
        back_populates="warehouse",
        foreign_keys="KPISnapshot.warehouse_id",
        overlaps="distributor,kpi_snapshots",
    )
