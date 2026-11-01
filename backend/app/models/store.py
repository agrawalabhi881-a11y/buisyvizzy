from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import CreatedAtMixin, PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.distributor import Distributor
    from app.models.inventory import Inventory
    from app.models.order import Order
    from app.models.shipment import Shipment
    from app.models.unmet_demand import UnmetDemand
    from app.models.warehouse import Warehouse


class Store(PrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "stores"
    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_store_latitude"),
        CheckConstraint(
            "longitude BETWEEN -180 AND 180",
            name="ck_store_longitude",
        ),
        UniqueConstraint("id", "distributor_id"),
        ForeignKeyConstraint(
            ["assigned_warehouse_id", "distributor_id"],
            ["warehouses.id", "warehouses.distributor_id"],
            ondelete="RESTRICT",
            name="fk_store_assigned_warehouse_distributor",
        ),
    )

    m5_store_id: Mapped[str | None] = mapped_column("store_id", String(20), unique=True)
    synthetic_code: Mapped[str | None] = mapped_column(String(32), unique=True)
    state_id: Mapped[str] = mapped_column(String(8), nullable=False)
    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    distributor_id: Mapped[int] = mapped_column(
        ForeignKey("distributors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    assigned_warehouse_id: Mapped[int] = mapped_column(nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    distributor: Mapped[Distributor] = relationship(back_populates="stores")
    assigned_warehouse: Mapped[Warehouse] = relationship(
        back_populates="stores",
        foreign_keys=[assigned_warehouse_id],
        overlaps="distributor,stores",
    )
    inventory: Mapped[list[Inventory]] = relationship(back_populates="store")
    orders: Mapped[list[Order]] = relationship(
        back_populates="source_store", foreign_keys="Order.source_store_id"
    )
    shipments: Mapped[list[Shipment]] = relationship(back_populates="destination_store")
    unmet_demand: Mapped[list[UnmetDemand]] = relationship(back_populates="store")
