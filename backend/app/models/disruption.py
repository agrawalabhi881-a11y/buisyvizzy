from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.distributor import Distributor
    from app.models.manufacturer import Manufacturer
    from app.models.store import Store
    from app.models.truck import Truck
    from app.models.warehouse import Warehouse


class Disruption(PrimaryKeyMixin, Base):
    __tablename__ = "disruptions"
    __table_args__ = (
        CheckConstraint(
            "disruption_type IN ('supplier_failure', 'warehouse_disruption', 'demand_spike', 'transport_delay')",
            name="ck_disruption_type",
        ),
        CheckConstraint("severity BETWEEN 1 AND 5", name="ck_disruption_severity"),
        CheckConstraint(
            "status IN ('planned', 'active', 'resolved', 'cancelled')",
            name="ck_disruption_status",
        ),
        CheckConstraint(
            "end_time IS NULL OR end_time >= start_time",
            name="ck_disruption_end_after_start",
        ),
    )

    disruption_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    severity: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(20), default="planned", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    affected_entities: Mapped[list[DisruptionTarget]] = relationship(
        back_populates="disruption", cascade="all, delete-orphan"
    )


class DisruptionTarget(PrimaryKeyMixin, Base):
    """Typed foreign keys identify affected entities without polymorphic references."""

    __tablename__ = "disruption_targets"
    __table_args__ = (
        CheckConstraint(
            "(manufacturer_id IS NOT NULL AND distributor_id IS NULL AND warehouse_id IS NULL AND store_id IS NULL AND truck_id IS NULL) OR "
            "(manufacturer_id IS NULL AND distributor_id IS NOT NULL AND warehouse_id IS NULL AND store_id IS NULL AND truck_id IS NULL) OR "
            "(manufacturer_id IS NULL AND distributor_id IS NULL AND warehouse_id IS NOT NULL AND store_id IS NULL AND truck_id IS NULL) OR "
            "(manufacturer_id IS NULL AND distributor_id IS NULL AND warehouse_id IS NULL AND store_id IS NOT NULL AND truck_id IS NULL) OR "
            "(manufacturer_id IS NULL AND distributor_id IS NULL AND warehouse_id IS NULL AND store_id IS NULL AND truck_id IS NOT NULL)",
            name="ck_disruption_target_exactly_one_entity",
        ),
        Index(
            "uq_disruption_target_manufacturer",
            "disruption_id",
            "manufacturer_id",
            unique=True,
            sqlite_where=text("manufacturer_id IS NOT NULL"),
            postgresql_where=text("manufacturer_id IS NOT NULL"),
        ),
        Index(
            "uq_disruption_target_distributor",
            "disruption_id",
            "distributor_id",
            unique=True,
            sqlite_where=text("distributor_id IS NOT NULL"),
            postgresql_where=text("distributor_id IS NOT NULL"),
        ),
        Index(
            "uq_disruption_target_warehouse",
            "disruption_id",
            "warehouse_id",
            unique=True,
            sqlite_where=text("warehouse_id IS NOT NULL"),
            postgresql_where=text("warehouse_id IS NOT NULL"),
        ),
        Index(
            "uq_disruption_target_store",
            "disruption_id",
            "store_id",
            unique=True,
            sqlite_where=text("store_id IS NOT NULL"),
            postgresql_where=text("store_id IS NOT NULL"),
        ),
        Index(
            "uq_disruption_target_truck",
            "disruption_id",
            "truck_id",
            unique=True,
            sqlite_where=text("truck_id IS NOT NULL"),
            postgresql_where=text("truck_id IS NOT NULL"),
        ),
    )

    disruption_id: Mapped[int] = mapped_column(
        ForeignKey("disruptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    manufacturer_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturers.id", ondelete="RESTRICT")
    )
    distributor_id: Mapped[int | None] = mapped_column(
        ForeignKey("distributors.id", ondelete="RESTRICT")
    )
    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="RESTRICT")
    )
    store_id: Mapped[int | None] = mapped_column(
        ForeignKey("stores.id", ondelete="RESTRICT")
    )
    truck_id: Mapped[int | None] = mapped_column(
        ForeignKey("trucks.id", ondelete="RESTRICT")
    )

    disruption: Mapped[Disruption] = relationship(back_populates="affected_entities")
    manufacturer: Mapped[Manufacturer | None] = relationship()
    distributor: Mapped[Distributor | None] = relationship()
    warehouse: Mapped[Warehouse | None] = relationship()
    store: Mapped[Store | None] = relationship()
    truck: Mapped[Truck | None] = relationship(back_populates="disruption_targets")
