from datetime import UTC, datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Backorder,
    Distributor,
    Inventory,
    KPISnapshot,
    Manufacturer,
    Order,
    OrderLine,
    Product,
    Shipment,
    ShipmentLine,
    Store,
    Truck,
    Warehouse,
)


def test_relationships_and_inventory_rollup(session: Session) -> None:
    store = session.scalar(select(Store).where(Store.name == "Test store"))
    assert store is not None
    assert store.assigned_warehouse.name == "Test warehouse"
    assert store.distributor.manufacturer.name == "Test manufacturer"

    product = session.scalar(select(Product).where(Product.name == "Test product"))
    assert product is not None
    warehouse = store.assigned_warehouse
    session.add(Inventory(product=product, warehouse=warehouse, quantity_on_hand=7))
    session.add(Inventory(product=product, store=store, quantity_on_hand=3))
    session.commit()

    distributor = session.scalar(select(Distributor))
    assert distributor is not None
    warehouse_total = session.scalar(
        select(func.coalesce(func.sum(Inventory.quantity_on_hand), 0))
        .join(Warehouse, Inventory.warehouse_id == Warehouse.id)
        .where(Warehouse.distributor_id == distributor.id)
    )
    assert float(warehouse_total) == 7


@pytest.mark.parametrize(
    "inventory_values",
    [
        {"quantity_on_hand": -1},
        {"quantity_on_hand": 2, "quantity_reserved": 3},
        {"warehouse_id": None, "store_id": None},
        {"store_id": 1},
    ],
)
def test_invalid_inventory_is_rejected(
    session: Session, inventory_values: dict[str, object]
) -> None:
    product = session.scalar(select(Product).where(Product.name == "Test product"))
    warehouse = session.scalar(
        select(Warehouse).where(Warehouse.name == "Test warehouse")
    )
    assert product is not None and warehouse is not None
    values: dict[str, object] = {
        "product_id": product.id,
        "warehouse_id": warehouse.id,
        "quantity_on_hand": 1,
        "quantity_reserved": 0,
    }
    values.update(inventory_values)
    with pytest.raises(IntegrityError):
        session.add(Inventory(**values))  # type: ignore[arg-type]
        session.commit()
    session.rollback()


def test_duplicate_product_location_inventory_is_rejected(session: Session) -> None:
    product = session.scalar(select(Product).where(Product.name == "Test product"))
    warehouse = session.scalar(
        select(Warehouse).where(Warehouse.name == "Test warehouse")
    )
    assert product is not None and warehouse is not None
    session.add_all(
        [
            Inventory(product=product, warehouse=warehouse, quantity_on_hand=1),
            Inventory(product=product, warehouse=warehouse, quantity_on_hand=1),
        ]
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_warehouse_capacity_is_enforced_for_aggregate_and_updates(
    session: Session,
) -> None:
    first = session.scalar(select(Product).where(Product.name == "Test product"))
    warehouse = session.scalar(
        select(Warehouse).where(Warehouse.name == "Test warehouse")
    )
    assert first is not None and warehouse is not None
    second = Product(name="Second product", storage_units_per_item=2)
    session.add(second)
    session.flush()
    session.add(Inventory(product=first, warehouse=warehouse, quantity_on_hand=6))
    session.commit()

    with pytest.raises(IntegrityError, match="cannot change product storage units"):
        first.storage_units_per_item = 2
        session.commit()
    session.rollback()

    with pytest.raises(IntegrityError, match="warehouse capacity exceeded"):
        session.add(Inventory(product=second, warehouse=warehouse, quantity_on_hand=3))
        session.commit()
    session.rollback()

    with pytest.raises(IntegrityError, match="warehouse capacity exceeded"):
        warehouse.storage_capacity = 5
        session.commit()
    session.rollback()


def test_order_line_constraints_and_partial_fulfillment(session: Session) -> None:
    store = session.scalar(select(Store).where(Store.name == "Test store"))
    product = session.scalar(select(Product).where(Product.name == "Test product"))
    assert store is not None and product is not None
    order = Order(
        order_number="SO-TEST-001",
        order_type="store_order",
        source_store=store,
        destination_distributor=store.distributor,
    )
    line = OrderLine(
        product=product,
        quantity_requested=10,
        quantity_fulfilled=1,
        unit_price=3,
        backorder_expires_at=datetime(2030, 1, 1, tzinfo=UTC),
    )
    line.backorder = Backorder(
        remaining_quantity=6, expires_at=line.backorder_expires_at
    )
    order.lines.append(line)
    session.add(order)
    session.commit()
    session.refresh(line)
    assert float(line.backorder.remaining_quantity) == 6

    truck = Truck(
        distributor_id=store.distributor_id,
        registration_number="TEST-TRUCK-1",
        capacity=100,
        fuel_efficiency=8,
    )
    shipment = Shipment(
        order=order,
        warehouse=store.assigned_warehouse,
        truck=truck,
        distributor_id=store.distributor_id,
        origin_warehouse=store.assigned_warehouse,
        destination_store=store,
    )
    shipment_line = ShipmentLine(
        order_line=line, quantity_shipped=4, quantity_delivered=1
    )
    shipment.lines.append(shipment_line)
    session.add(shipment)
    session.commit()
    session.refresh(shipment_line)
    assert float(shipment_line.quantity_in_transit) == 3
    assert float(line.quantity_requested) - float(line.quantity_fulfilled) - float(
        shipment_line.quantity_in_transit
    ) == float(line.backorder.remaining_quantity)

    invalid = OrderLine(
        order=order,
        product=Product(name="Invalid line product"),
        quantity_requested=2,
        quantity_fulfilled=3,
        unit_price=1,
    )
    session.add(invalid)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_order_flow_foreign_keys_keep_entities_in_their_network(
    session: Session,
) -> None:
    store = session.scalar(select(Store).where(Store.name == "Test store"))
    assert store is not None
    manufacturer = store.distributor.manufacturer
    procurement = Order(
        order_number="PO-TEST-001",
        order_type="procurement",
        source_distributor=store.distributor,
        destination_manufacturer=manufacturer,
    )
    session.add(procurement)
    session.flush()
    warehouse_replenishment = Order(
        order_number="WR-TEST-001",
        order_type="warehouse_replenishment",
        source_warehouse=store.assigned_warehouse,
        destination_distributor=store.distributor,
    )
    session.add(warehouse_replenishment)
    session.commit()

    other_manufacturer = Manufacturer(name="Other manufacturer", location="Other")
    session.add(other_manufacturer)
    session.flush()
    invalid_procurement = Order(
        order_number="PO-TEST-002",
        order_type="procurement",
        source_distributor=store.distributor,
        destination_manufacturer=other_manufacturer,
    )
    session.add(invalid_procurement)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_m5_external_ids_are_unique(session: Session) -> None:
    store = session.scalar(select(Store).where(Store.name == "Test store"))
    warehouse = session.scalar(
        select(Warehouse).where(Warehouse.name == "Test warehouse")
    )
    assert store is not None and warehouse is not None
    store.m5_store_id = "CA_1"
    product = Product(name="M5 product 1", m5_item_id="ITEM_1")
    session.add(product)
    session.commit()

    duplicate_store = Store(
        name="Duplicate M5 store",
        m5_store_id="CA_1",
        state_id="CA",
        distributor_id=store.distributor_id,
        assigned_warehouse_id=warehouse.id,
    )
    duplicate_product = Product(name="Duplicate M5 product", m5_item_id="ITEM_1")
    session.add_all([duplicate_store, duplicate_product])
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_kpi_profit_is_consistent_and_scope_is_unique(session: Session) -> None:
    distributor = session.scalar(select(Distributor))
    assert distributor is not None
    snapshot = KPISnapshot(
        distributor=distributor,
        snapshot_date=datetime(2026, 1, 1).date(),
        total_revenue=100,
        procurement_cost=30,
        transportation_cost=10,
        fuel_cost=5,
        salary_cost=15,
        operating_cost=10,
    )
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    assert float(snapshot.total_profit) == 30

    duplicate = KPISnapshot(
        distributor=distributor, snapshot_date=snapshot.snapshot_date
    )
    session.add(duplicate)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
