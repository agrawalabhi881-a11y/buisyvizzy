from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import CreatedAtMixin, PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.inventory import Inventory
    from app.models.order import OrderLine
    from app.models.sales_record import DailySalesRecord
    from app.models.sell_price import WeeklySellPrice
    from app.models.unmet_demand import UnmetDemand


class Product(PrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("unit_cost >= 0", name="ck_product_unit_cost_nonnegative"),
        CheckConstraint(
            "storage_units_per_item > 0", name="ck_product_storage_units_positive"
        ),
    )

    m5_item_id: Mapped[str | None] = mapped_column("item_id", String(32), unique=True)
    department_id: Mapped[str | None] = mapped_column("dept_id", String(32))
    category_id: Mapped[str | None] = mapped_column("cat_id", String(32))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(
        String(32), default="unit", nullable=False
    )
    unit_cost: Mapped[float] = mapped_column(Numeric(14, 4), default=0, nullable=False)
    storage_units_per_item: Mapped[float] = mapped_column(
        Numeric(12, 4), default=1, server_default=text("1"), nullable=False
    )

    inventory: Mapped[list[Inventory]] = relationship(back_populates="product")
    order_lines: Mapped[list[OrderLine]] = relationship(back_populates="product")
    sales_records: Mapped[list[DailySalesRecord]] = relationship(
        back_populates="product"
    )
    weekly_prices: Mapped[list[WeeklySellPrice]] = relationship(
        back_populates="product"
    )
    unmet_demand: Mapped[list[UnmetDemand]] = relationship(back_populates="product")
