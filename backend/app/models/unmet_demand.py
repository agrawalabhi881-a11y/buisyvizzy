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
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.product import Product
    from app.models.store import Store


class UnmetDemand(PrimaryKeyMixin, Base):
    __tablename__ = "unmet_demand"
    __table_args__ = (
        CheckConstraint("requested_quantity > 0", name="ck_unmet_requested_positive"),
        CheckConstraint(
            "fulfilled_quantity >= 0", name="ck_unmet_fulfilled_nonnegative"
        ),
        CheckConstraint("unmet_quantity >= 0", name="ck_unmet_quantity_nonnegative"),
        CheckConstraint(
            "fulfilled_quantity + unmet_quantity <= requested_quantity",
            name="ck_unmet_quantities_valid",
        ),
        UniqueConstraint("order_id", "product_id", name="uq_unmet_order_product"),
        ForeignKeyConstraint(
            ["order_id", "store_id"],
            ["orders.id", "orders.source_store_id"],
            ondelete="RESTRICT",
            name="fk_unmet_store_order",
        ),
    )

    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), nullable=False, index=True
    )
    requested_quantity: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    fulfilled_quantity: Mapped[float] = mapped_column(
        Numeric(14, 3), default=0, nullable=False
    )
    unmet_quantity: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(String(255))

    store: Mapped[Store] = relationship(back_populates="unmet_demand")
    product: Mapped[Product] = relationship(back_populates="unmet_demand")
    order: Mapped[Order] = relationship(
        back_populates="unmet_demand", foreign_keys=[order_id]
    )
