from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import CreatedAtMixin, PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.driver import Driver
    from app.models.kpi_snapshot import KPISnapshot
    from app.models.manufacturer import Manufacturer
    from app.models.order import Order
    from app.models.store import Store
    from app.models.truck import Truck
    from app.models.warehouse import Warehouse


class Distributor(PrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "distributors"
    __table_args__ = (UniqueConstraint("id", "manufacturer_id"),)

    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(40))

    manufacturer: Mapped[Manufacturer] = relationship(back_populates="distributors")
    warehouses: Mapped[list[Warehouse]] = relationship(back_populates="distributor")
    stores: Mapped[list[Store]] = relationship(back_populates="distributor")
    trucks: Mapped[list[Truck]] = relationship(back_populates="distributor")
    drivers: Mapped[list[Driver]] = relationship(back_populates="distributor")
    orders: Mapped[list[Order]] = relationship(
        back_populates="source_distributor", foreign_keys="Order.source_distributor_id"
    )
    kpi_snapshots: Mapped[list[KPISnapshot]] = relationship(
        back_populates="distributor"
    )
