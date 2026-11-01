from sqlalchemy.orm import Session

from app.models import Distributor, Driver, Inventory, Product, Store, Truck, Warehouse
from scripts.seed import run_seed


def test_seed_is_reproducible_and_does_not_invent_m5_ids(engine) -> None:
    first = run_seed(engine, None)
    second = run_seed(engine, None)

    assert first == second
    assert first["manufacturers"] == 1
    assert first["distributors"] == 2
    assert first["warehouses"] == 3
    assert first["stores"] == 10
    assert first["products"] == 50
    assert first["trucks"] == 10
    assert first["drivers"] == 10
    assert first["stores_per_distributor_1"] == 5
    assert first["stores_per_distributor_2"] == 5
    assert first["stores_per_warehouse_1"] == 3
    assert first["stores_per_warehouse_2"] == 2
    assert first["stores_per_warehouse_3"] == 5
    assert first["trucks_per_distributor_1"] == 5
    assert first["trucks_per_distributor_2"] == 5
    assert first["drivers_per_distributor_1"] == 5
    assert first["drivers_per_distributor_2"] == 5
    with Session(engine) as session:
        stores = session.query(Store).all()
        assert all(store.m5_store_id is None for store in stores)
        assert {store.synthetic_code for store in stores} == {
            f"SYN-STORE-{index:03d}" for index in range(1, 11)
        }
        assert all(
            store.latitude is not None and store.longitude is not None
            for store in stores
        )
        assert all(store.state_id in {"CA", "TX", "WI"} for store in stores)
        assert all(
            product.m5_item_id is None for product in session.query(Product).all()
        )
        assert session.query(Inventory).count() == 650
        assert (
            session.query(Inventory).filter(Inventory.warehouse_id.is_not(None)).count()
            == 150
        )
        assert (
            session.query(Inventory).filter(Inventory.store_id.is_not(None)).count()
            == 500
        )
        assert all(
            warehouse.latitude is not None and warehouse.longitude is not None
            for warehouse in session.query(Warehouse)
        )
        for distributor in session.query(Distributor):
            assert sum(store.distributor_id == distributor.id for store in stores) == 5
            assert (
                session.query(Truck).filter_by(distributor_id=distributor.id).count()
                == 5
            )
            assert (
                session.query(Driver).filter_by(distributor_id=distributor.id).count()
                == 5
            )
        for store in stores:
            assert store.assigned_warehouse.distributor_id == store.distributor_id


def test_seed_accepts_actual_m5_identifier_configuration(engine) -> None:
    catalog = {
        "stores": [{"store_id": "CA_1", "state_id": "CA"}],
        "products": [{"item_id": "ITEM_001", "dept_id": "FOODS_1", "cat_id": "FOODS"}],
    }
    run_seed(engine, None)
    # Actual catalog IDs replace synthetic placeholders without growing the network.
    from scripts.seed import seed_database

    with Session(engine) as session, session.begin():
        counts = seed_database(session, catalog)

    assert counts["stores"] == 10
    assert counts["products"] == 50
    assert counts["inventory_records"] == 650
    with Session(engine) as session:
        m5_store = session.query(Store).filter_by(m5_store_id="CA_1").one()
        assert m5_store.state_id == "CA"
        m5_product = session.query(Product).filter_by(m5_item_id="ITEM_001").one()
        assert m5_product.department_id == "FOODS_1"
        assert m5_product.category_id == "FOODS"
