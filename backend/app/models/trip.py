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
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.driver import Driver
    from app.models.shipment import Shipment
    from app.models.truck import Truck


class Trip(PrimaryKeyMixin, Base):
    __tablename__ = "trips"
    __table_args__ = (
        ForeignKeyConstraint(
            ["truck_id", "distributor_id"],
            ["trucks.id", "trucks.distributor_id"],
            name="fk_trip_truck_distributor",
        ),
        ForeignKeyConstraint(
            ["driver_id", "distributor_id"],
            ["drivers.id", "drivers.distributor_id"],
            name="fk_trip_driver_distributor",
        ),
        ForeignKeyConstraint(
            ["shipment_id", "distributor_id"],
            ["shipments.id", "shipments.distributor_id"],
            name="fk_trip_shipment_distributor",
        ),
        CheckConstraint("distance >= 0", name="ck_trip_distance_nonnegative"),
        CheckConstraint(
            "estimated_duration >= 0", name="ck_trip_estimated_duration_nonnegative"
        ),
        CheckConstraint(
            "actual_duration IS NULL OR actual_duration >= 0",
            name="ck_trip_actual_duration_nonnegative",
        ),
        CheckConstraint(
            "fuel_consumed IS NULL OR fuel_consumed >= 0",
            name="ck_trip_fuel_nonnegative",
        ),
        CheckConstraint(
            "trip_status IN ('planned', 'in_progress', 'completed', 'cancelled')",
            name="ck_trip_status",
        ),
        CheckConstraint(
            "end_time IS NULL OR end_time >= start_time", name="ck_trip_end_after_start"
        ),
    )

    truck_id: Mapped[int] = mapped_column(
        ForeignKey("trucks.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    shipment_id: Mapped[int] = mapped_column(
        ForeignKey("shipments.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    distributor_id: Mapped[int] = mapped_column(
        ForeignKey("distributors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    start_location: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    distance: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    estimated_duration: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    actual_duration: Mapped[float | None] = mapped_column(Numeric(12, 2))
    fuel_consumed: Mapped[float | None] = mapped_column(Numeric(12, 3))
    trip_status: Mapped[str] = mapped_column(
        String(20), default="planned", nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    truck: Mapped[Truck] = relationship(back_populates="trips", foreign_keys=[truck_id])
    driver: Mapped[Driver] = relationship(
        back_populates="trips", foreign_keys=[driver_id]
    )
    shipment: Mapped[Shipment] = relationship(
        back_populates="trips", foreign_keys=[shipment_id]
    )
