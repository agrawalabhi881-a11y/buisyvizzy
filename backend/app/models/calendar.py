from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.sales_record import DailySalesRecord
    from app.models.sell_price import WeeklySellPrice


class CalendarWeek(PrimaryKeyMixin, Base):
    __tablename__ = "calendar_weeks"

    wm_yr_wk: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    sell_prices: Mapped[list[WeeklySellPrice]] = relationship(
        back_populates="calendar_week"
    )
    calendar_dates: Mapped[list[M5CalendarDate]] = relationship(
        back_populates="calendar_week"
    )


class M5CalendarDate(PrimaryKeyMixin, Base):
    __tablename__ = "calendar_dates"
    __table_args__ = (
        CheckConstraint("wday BETWEEN 1 AND 7", name="ck_calendar_wday"),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_calendar_month"),
        UniqueConstraint("date", name="uq_calendar_date"),
    )

    m5_day_id: Mapped[str] = mapped_column("d", String(12), unique=True, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    wm_yr_wk: Mapped[str] = mapped_column(
        ForeignKey("calendar_weeks.wm_yr_wk", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    weekday: Mapped[str] = mapped_column(String(16), nullable=False)
    wday: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    event_name_1: Mapped[str | None] = mapped_column(String(80))
    event_type_1: Mapped[str | None] = mapped_column(String(40))
    event_name_2: Mapped[str | None] = mapped_column(String(80))
    event_type_2: Mapped[str | None] = mapped_column(String(40))
    snap_ca: Mapped[bool] = mapped_column(
        "snap_CA", Boolean, default=False, nullable=False
    )
    snap_tx: Mapped[bool] = mapped_column(
        "snap_TX", Boolean, default=False, nullable=False
    )
    snap_wi: Mapped[bool] = mapped_column(
        "snap_WI", Boolean, default=False, nullable=False
    )

    calendar_week: Mapped[CalendarWeek] = relationship(back_populates="calendar_dates")
    sales_records: Mapped[list[DailySalesRecord]] = relationship(
        back_populates="calendar_date"
    )
