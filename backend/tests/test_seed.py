from sqlalchemy.orm import Session

from app.models import Distributor, Driver, Inventory, Product, Store, Truck, Warehouse
from scripts.seed import seed_database

M5_STORES = (
    "CA_1",
    "CA_2",
    "CA_3",
    "CA_4",
    "TX_1",
    "TX_2",
    "TX_3",
    "WI_1",
    "WI_2",
    "WI_3",
)


def _catalog() -> dict[str, list[dict[str, str]]]:
    return {
        "stores": [
            {"store_id": store_id, "state_id": store_id.split("_")[0]}
            for store_id in M5_STORES
        ],
        "products": [
            {
                "item_id": f"FOODS_1_{index:03d}",
                "dept_id": "FOODS_1",
                "cat_id": "FOODS",
            }
            for index in range(1, 51)
        ],
    }


def test_seed_is_reproducible_and_contains_only_m5_catalog(engine) -> None:
    with Session(engine) as session, session.begin():
        first = seed_database(session, _catalog())
    with Session(engine) as session, session.begin():
        second = seed_database(session, _catalog())

    assert first == second
    assert first["manufacturers"] == 1
    assert first["distributors"] == 2
    assert first["warehouses"] == 3
    assert first["stores"] == 10
    assert first["products"] == 50
    assert first["trucks"] == 10
    assert first["drivers"] == 10
    assert first["inventory_records"] == 0
    assert first["stores_per_distributor_1"] == 5
    assert first["stores_per_distributor_2"] == 5
    assert first["trucks_per_distributor_1"] == 5
    assert first["trucks_per_distributor_2"] == 5
    assert first["drivers_per_distributor_1"] == 5
    assert first["drivers_per_distributor_2"] == 5

    with Session(engine) as session:
        stores = session.query(Store).all()
        products = session.query(Product).all()
        assert {store.m5_store_id for store in stores} == set(M5_STORES)
        assert {store.name for store in stores} == {
            f"Store {index}" for index in range(1, 11)
        }
        assert all(store.synthetic_code is None for store in stores)
        assert all(
            store.location_source == "approximate_state_centroid_not_store_address"
            for store in stores
        )
        assert all(
            store.assigned_warehouse.distributor_id == store.distributor_id
            for store in stores
        )
        assert len(products) == 50
        assert all(product.m5_item_id is not None for product in products)
        assert session.query(Inventory).count() == 0
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
        assert session.query(Warehouse).count() == 3


def test_seed_rejects_wrong_size_or_non_m5_store_catalog(engine) -> None:
    catalog = _catalog()
    catalog["stores"] = catalog["stores"][:-1]
    with Session(engine) as session:
        try:
            seed_database(session, catalog)
        except ValueError as error:
            assert "exactly 10 M5 stores" in str(error)
        else:
            raise AssertionError("invalid catalog unexpectedly accepted")
