from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.calendar import CalendarWeek
    from app.models.product import Product
    from app.models.store import Store


class WeeklySellPrice(PrimaryKeyMixin, Base):
    __tablename__ = "weekly_sell_prices"
    __table_args__ = (
        CheckConstraint("sell_price >= 0", name="ck_sell_price_nonnegative"),
        UniqueConstraint(
            "product_id",
            "store_id",
            "calendar_week_id",
            name="uq_sell_price_product_store_week",
        ),
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    calendar_week_id: Mapped[int] = mapped_column(
        ForeignKey("calendar_weeks.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    sell_price: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)

    product: Mapped[Product] = relationship(back_populates="weekly_prices")
    store: Mapped[Store] = relationship()
    calendar_week: Mapped[CalendarWeek] = relationship(back_populates="sell_prices")
