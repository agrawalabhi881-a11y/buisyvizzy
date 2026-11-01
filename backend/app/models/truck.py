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
    from app.models.disruption import DisruptionTarget
    from app.models.distributor import Distributor
    from app.models.shipment import Shipment
    from app.models.trip import Trip


class Truck(PrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "trucks"
    __table_args__ = (
        UniqueConstraint("id", "distributor_id"),
        CheckConstraint("capacity > 0", name="ck_truck_capacity_positive"),
        CheckConstraint(
            "fuel_efficiency > 0", name="ck_truck_fuel_efficiency_positive"
        ),
        CheckConstraint(
            "current_latitude IS NULL OR current_latitude BETWEEN -90 AND 90",
            name="ck_truck_latitude",
        ),
        CheckConstraint(
            "current_longitude IS NULL OR current_longitude BETWEEN -180 AND 180",
            name="ck_truck_longitude",
        ),
        CheckConstraint(
            "availability_status IN ('available', 'on_trip', 'maintenance', 'inactive')",
            name="ck_truck_availability_status",
        ),
    )

    distributor_id: Mapped[int] = mapped_column(
        ForeignKey("distributors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    registration_number: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False
    )
    capacity: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    fuel_efficiency: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    current_latitude: Mapped[float | None] = mapped_column(Float)
    current_longitude: Mapped[float | None] = mapped_column(Float)
    availability_status: Mapped[str] = mapped_column(
        String(20), default="available", nullable=False
    )

    distributor: Mapped[Distributor] = relationship(back_populates="trucks")
    shipments: Mapped[list[Shipment]] = relationship(
        back_populates="truck", foreign_keys="Shipment.truck_id"
    )
    trips: Mapped[list[Trip]] = relationship(
        back_populates="truck", foreign_keys="Trip.truck_id"
    )
    disruption_targets: Mapped[list[DisruptionTarget]] = relationship(
        back_populates="truck"
    )
