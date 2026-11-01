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
    from app.models.trip import Trip


class Driver(PrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "drivers"
    __table_args__ = (
        UniqueConstraint("id", "distributor_id"),
        UniqueConstraint("distributor_id", "name", name="uq_driver_distributor_name"),
        CheckConstraint("base_salary >= 0", name="ck_driver_base_salary_nonnegative"),
        CheckConstraint(
            "per_distance_rate >= 0", name="ck_driver_distance_rate_nonnegative"
        ),
        CheckConstraint(
            "current_latitude IS NULL OR current_latitude BETWEEN -90 AND 90",
            name="ck_driver_latitude",
        ),
        CheckConstraint(
            "current_longitude IS NULL OR current_longitude BETWEEN -180 AND 180",
            name="ck_driver_longitude",
        ),
        CheckConstraint(
            "salary_type IN ('monthly', 'hourly', 'per_distance', 'mixed')",
            name="ck_driver_salary_type",
        ),
        CheckConstraint(
            "availability_status IN ('available', 'on_trip', 'off_duty', 'inactive')",
            name="ck_driver_availability",
        ),
    )

    distributor_id: Mapped[int] = mapped_column(
        ForeignKey("distributors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(40))
    salary_type: Mapped[str] = mapped_column(String(20), nullable=False)
    base_salary: Mapped[float] = mapped_column(
        Numeric(14, 2), default=0, nullable=False
    )
    per_distance_rate: Mapped[float] = mapped_column(
        Numeric(12, 4), default=0, nullable=False
    )
    current_latitude: Mapped[float | None] = mapped_column(Float)
    current_longitude: Mapped[float | None] = mapped_column(Float)
    availability_status: Mapped[str] = mapped_column(
        String(20), default="available", nullable=False
    )

    distributor: Mapped[Distributor] = relationship(back_populates="drivers")
    trips: Mapped[list[Trip]] = relationship(
        back_populates="driver", foreign_keys="Trip.driver_id"
    )
