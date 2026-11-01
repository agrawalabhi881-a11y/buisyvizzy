from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.calendar import M5CalendarDate
    from app.models.product import Product
    from app.models.store import Store


class DailySalesRecord(PrimaryKeyMixin, Base):
    __tablename__ = "daily_sales_records"
    __table_args__ = (
        CheckConstraint("units_sold >= 0", name="ck_sales_units_nonnegative"),
        UniqueConstraint(
            "product_id",
            "store_id",
            "calendar_date_id",
            name="uq_sales_product_store_date",
        ),
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    calendar_date_id: Mapped[int] = mapped_column(
        ForeignKey("calendar_dates.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    units_sold: Mapped[int] = mapped_column(nullable=False)
    source_dataset: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="m5_forecasting",
        server_default=text("'m5_forecasting'"),
    )

    product: Mapped[Product] = relationship(back_populates="sales_records")
    store: Mapped[Store] = relationship()
    calendar_date: Mapped[M5CalendarDate] = relationship(back_populates="sales_records")
