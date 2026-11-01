from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    func,
    text,
)
from sqlalchemy.engine import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import Table

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.store import Store
    from app.models.warehouse import Warehouse


class Inventory(PrimaryKeyMixin, Base):
    __tablename__ = "inventories"
    __table_args__ = (
        CheckConstraint(
            "(warehouse_id IS NOT NULL AND store_id IS NULL) OR "
            "(warehouse_id IS NULL AND store_id IS NOT NULL)",
            name="ck_inventory_exactly_one_location",
        ),
        CheckConstraint(
            "quantity_on_hand >= 0", name="ck_inventory_on_hand_nonnegative"
        ),
        CheckConstraint(
            "quantity_reserved >= 0", name="ck_inventory_reserved_nonnegative"
        ),
        CheckConstraint(
            "quantity_reserved <= quantity_on_hand",
            name="ck_inventory_reserved_not_above_on_hand",
        ),
        CheckConstraint("reorder_level >= 0", name="ck_inventory_reorder_nonnegative"),
        CheckConstraint(
            "maximum_stock_level IS NULL OR maximum_stock_level >= reorder_level",
            name="ck_inventory_max_at_least_reorder",
        ),
        Index(
            "uq_inventory_product_warehouse",
            "product_id",
            "warehouse_id",
            unique=True,
            sqlite_where=text("warehouse_id IS NOT NULL"),
            postgresql_where=text("warehouse_id IS NOT NULL"),
        ),
        Index(
            "uq_inventory_product_store",
            "product_id",
            "store_id",
            unique=True,
            sqlite_where=text("store_id IS NOT NULL"),
            postgresql_where=text("store_id IS NOT NULL"),
        ),
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="RESTRICT"), index=True
    )
    store_id: Mapped[int | None] = mapped_column(
        ForeignKey("stores.id", ondelete="RESTRICT"), index=True
    )
    quantity_on_hand: Mapped[float] = mapped_column(
        Numeric(14, 3), default=0, nullable=False
    )
    quantity_reserved: Mapped[float] = mapped_column(
        Numeric(14, 3), default=0, nullable=False
    )
    reorder_level: Mapped[float] = mapped_column(
        Numeric(14, 3), default=0, nullable=False
    )
    maximum_stock_level: Mapped[float | None] = mapped_column(Numeric(14, 3))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    product: Mapped[Product] = relationship(back_populates="inventory")
    warehouse: Mapped[Warehouse | None] = relationship(back_populates="inventory")
    store: Mapped[Store | None] = relationship(back_populates="inventory")


@listens_for(Inventory.__table__, "after_create")
def _create_sqlite_capacity_triggers(
    target: Table, connection: Connection, **_kwargs: object
) -> None:
    if connection.dialect.name != "sqlite":
        return
    connection.exec_driver_sql(
        """CREATE TRIGGER enforce_inventory_warehouse_capacity_insert
        BEFORE INSERT ON inventories
        WHEN NEW.warehouse_id IS NOT NULL AND
          (SELECT COALESCE(SUM(i.quantity_on_hand * p.storage_units_per_item), 0)
           FROM inventories AS i JOIN products AS p ON p.id = i.product_id
           WHERE i.warehouse_id = NEW.warehouse_id) +
          NEW.quantity_on_hand * (SELECT storage_units_per_item FROM products WHERE id = NEW.product_id) >
          (SELECT storage_capacity FROM warehouses WHERE id = NEW.warehouse_id)
        BEGIN SELECT RAISE(ABORT, 'warehouse capacity exceeded'); END"""
    )
    connection.exec_driver_sql(
        """CREATE TRIGGER enforce_inventory_warehouse_capacity_update
        BEFORE UPDATE OF warehouse_id, quantity_on_hand ON inventories
        WHEN NEW.warehouse_id IS NOT NULL AND
          (SELECT COALESCE(SUM(i.quantity_on_hand * p.storage_units_per_item), 0)
           FROM inventories AS i JOIN products AS p ON p.id = i.product_id
           WHERE i.warehouse_id = NEW.warehouse_id AND i.id != OLD.id) +
          NEW.quantity_on_hand * (SELECT storage_units_per_item FROM products WHERE id = NEW.product_id) >
          (SELECT storage_capacity FROM warehouses WHERE id = NEW.warehouse_id)
        BEGIN SELECT RAISE(ABORT, 'warehouse capacity exceeded'); END"""
    )
    connection.exec_driver_sql("""CREATE TRIGGER enforce_warehouse_capacity_update
        BEFORE UPDATE OF storage_capacity ON warehouses
        WHEN (SELECT COALESCE(SUM(i.quantity_on_hand * p.storage_units_per_item), 0)
              FROM inventories AS i JOIN products AS p ON p.id = i.product_id
              WHERE i.warehouse_id = OLD.id) > NEW.storage_capacity
        BEGIN SELECT RAISE(ABORT, 'warehouse capacity exceeded'); END""")
    connection.exec_driver_sql(
        """CREATE TRIGGER prevent_stocked_product_storage_change
        BEFORE UPDATE OF storage_units_per_item ON products
        WHEN NEW.storage_units_per_item != OLD.storage_units_per_item AND
          EXISTS (SELECT 1 FROM inventories WHERE product_id = OLD.id)
        BEGIN SELECT RAISE(ABORT, 'cannot change product storage units while inventory records exist'); END"""
    )
