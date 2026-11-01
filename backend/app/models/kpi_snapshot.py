from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Computed,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.distributor import Distributor
    from app.models.warehouse import Warehouse


class KPISnapshot(PrimaryKeyMixin, Base):
    __tablename__ = "kpi_snapshots"
    __table_args__ = (
        CheckConstraint("total_inventory >= 0", name="ck_kpi_inventory_nonnegative"),
        CheckConstraint("total_revenue >= 0", name="ck_kpi_revenue_nonnegative"),
        CheckConstraint(
            "procurement_cost >= 0", name="ck_kpi_procurement_cost_nonnegative"
        ),
        CheckConstraint(
            "transportation_cost >= 0", name="ck_kpi_transport_cost_nonnegative"
        ),
        CheckConstraint("fuel_cost >= 0", name="ck_kpi_fuel_cost_nonnegative"),
        CheckConstraint("salary_cost >= 0", name="ck_kpi_salary_cost_nonnegative"),
        CheckConstraint(
            "operating_cost >= 0", name="ck_kpi_operating_cost_nonnegative"
        ),
        CheckConstraint("fill_rate BETWEEN 0 AND 1", name="ck_kpi_fill_rate"),
        CheckConstraint("stockout_frequency >= 0", name="ck_kpi_stockout_nonnegative"),
        CheckConstraint("unmet_demand >= 0", name="ck_kpi_unmet_nonnegative"),
        ForeignKeyConstraint(
            ["warehouse_id", "distributor_id"],
            ["warehouses.id", "warehouses.distributor_id"],
            ondelete="RESTRICT",
            name="fk_kpi_warehouse_distributor",
        ),
        UniqueConstraint(
            "distributor_id", "warehouse_id", "snapshot_date", name="uq_kpi_scope_date"
        ),
        Index(
            "uq_kpi_distributor_date",
            "distributor_id",
            "snapshot_date",
            unique=True,
            sqlite_where=text("warehouse_id IS NULL"),
            postgresql_where=text("warehouse_id IS NULL"),
        ),
    )

    distributor_id: Mapped[int] = mapped_column(
        ForeignKey("distributors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    warehouse_id: Mapped[int | None] = mapped_column(index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_inventory: Mapped[float] = mapped_column(
        Numeric(16, 3), default=0, nullable=False
    )
    total_revenue: Mapped[float] = mapped_column(
        Numeric(16, 2), default=0, nullable=False
    )
    procurement_cost: Mapped[float] = mapped_column(
        Numeric(16, 2), default=0, nullable=False
    )
    transportation_cost: Mapped[float] = mapped_column(
        Numeric(16, 2), default=0, nullable=False
    )
    fuel_cost: Mapped[float] = mapped_column(Numeric(16, 2), default=0, nullable=False)
    salary_cost: Mapped[float] = mapped_column(
        Numeric(16, 2), default=0, nullable=False
    )
    operating_cost: Mapped[float] = mapped_column(
        Numeric(16, 2), default=0, nullable=False
    )
    total_profit: Mapped[float] = mapped_column(
        Numeric(16, 2),
        Computed(
            "total_revenue - procurement_cost - transportation_cost - fuel_cost - salary_cost - operating_cost",
            persisted=True,
        ),
    )
    fill_rate: Mapped[float] = mapped_column(Numeric(6, 5), default=0, nullable=False)
    stockout_frequency: Mapped[int] = mapped_column(default=0, nullable=False)
    unmet_demand: Mapped[float] = mapped_column(
        Numeric(16, 3), default=0, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    distributor: Mapped[Distributor] = relationship(back_populates="kpi_snapshots")
    warehouse: Mapped[Warehouse | None] = relationship(
        back_populates="kpi_snapshots", foreign_keys=[warehouse_id]
    )
