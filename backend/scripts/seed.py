from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.orm import Session

from app.models import (
    Distributor,
    Driver,
    Inventory,
    Manufacturer,
    Product,
    Store,
    Truck,
    Warehouse,
)

NETWORK_CONFIG = {
    "manufacturers": 1,
    "distributors": 2,
    "warehouses": 3,
    "stores": 10,
    "products": 50,
    "trucks": 10,
    "drivers": 10,
}
SYNTHETIC_STORE_COUNT = NETWORK_CONFIG["stores"]
SYNTHETIC_TRUCK_COUNT = 10


def load_catalog(path: Path | None) -> dict[str, list[dict[str, Any]]]:
    if path is None:
        return {"stores": [], "products": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    stores = payload.get("stores", [])
    products = payload.get("products", [])
    if not isinstance(stores, list) or not isinstance(products, list):
        raise TypeError("M5 catalog 'stores' and 'products' values must be arrays")
    if len(stores) > 10:
        raise ValueError("M5 seed catalog may contain at most the 10 actual M5 stores")
    if len(products) > NETWORK_CONFIG["products"]:
        raise ValueError("Product catalog exceeds configured seed limit of 50")
    return {"stores": stores, "products": products}


def _get_or_create(
    session: Session, model: type[Any], identity: dict[str, Any], values: dict[str, Any]
) -> Any:
    instance = session.scalar(select(model).filter_by(**identity))
    if instance is None:
        instance = model(**(identity | values))
        session.add(instance)
        session.flush()
    else:
        # Seed-owned attributes (name, location, ownership, capacities, etc.)
        # are reconciled on every run. Fields absent from values, notably valid
        # external M5 identifiers, are preserved.
        for key, value in values.items():
            setattr(instance, key, value)
    return instance


def seed_database(
    session: Session, catalog: dict[str, list[dict[str, Any]]]
) -> dict[str, int]:
    manufacturer = _get_or_create(
        session,
        Manufacturer,
        {"name": "Synthetic Manufacturer 001"},
        {
            "location": "Synthetic Region A",
            "contact_email": "manufacturer@example.invalid",
        },
    )

    distributors = [
        _get_or_create(
            session,
            Distributor,
            {"name": f"Synthetic Distributor {index:03d}"},
            {
                "manufacturer_id": manufacturer.id,
                "location": f"Synthetic Region {chr(64 + index)}",
                "contact_email": f"distributor{index}@example.invalid",
            },
        )
        for index in (1, 2)
    ]

    warehouse_specs = (
        ("Synthetic Warehouse 001", 0, "California", 100_000, 34.0522, -118.2437),
        ("Synthetic Warehouse 002", 0, "Texas", 100_000, 32.7767, -96.7970),
        ("Synthetic Warehouse 003", 1, "Wisconsin", 100_000, 43.0389, -87.9065),
    )
    warehouses: list[Warehouse] = []
    for (
        name,
        distributor_index,
        location,
        capacity,
        latitude,
        longitude,
    ) in warehouse_specs:
        warehouses.append(
            _get_or_create(
                session,
                Warehouse,
                {"name": name},
                {
                    "distributor_id": distributors[distributor_index].id,
                    "location": location,
                    "storage_capacity": capacity,
                    "latitude": latitude,
                    "longitude": longitude,
                },
            )
        )

    stores: list[Store] = []
    m5_stores = catalog["stores"]
    # Approximate synthetic sites in CA, TX and WI. These are not official store
    # coordinates; they provide deterministic, geographically valid seed data.
    state_sites = {
        "CA": (34.05, -118.24),
        "TX": (32.78, -96.80),
        "WI": (43.04, -87.91),
    }
    for index in range(SYNTHETIC_STORE_COUNT):
        if index < len(m5_stores):
            entry = m5_stores[index]
            external_id = str(entry["store_id"])
            identity = {"m5_store_id": external_id}
            if session.scalar(select(Store).filter_by(m5_store_id=external_id)) is None:
                # Convert the corresponding placeholder store in place if an
                # actual M5 catalog is added after the synthetic seed.
                identity = {"name": f"Synthetic Store {index + 1:03d}"}
            store_name = str(entry.get("name") or f"M5 Store {external_id}")
            state_id = str(entry["state_id"])
        else:
            external_id = ""
            identity = {"name": f"Synthetic Store {index + 1:03d}"}
            store_name = identity["name"]
            state_id = ("CA", "CA", "CA", "TX", "TX", "WI", "WI", "WI", "WI", "WI")[
                index
            ]
            base_lat, base_lon = state_sites[state_id]
        if index < len(m5_stores):
            # M5 state IDs are retained; coordinates remain clearly approximate.
            state_id = str(entry["state_id"])
            base_lat, base_lon = state_sites.get(state_id, (34.05, -118.24))
        distributor_index = 0 if index < 5 else 1
        warehouse_index = 0 if index < 3 else (1 if index < 5 else 2)
        store = _get_or_create(
            session,
            Store,
            identity,
            {
                "name": store_name,
                "synthetic_code": (
                    None if index < len(m5_stores) else f"SYN-STORE-{index + 1:03d}"
                ),
                "state_id": state_id,
                "distributor_id": distributors[distributor_index].id,
                "assigned_warehouse_id": warehouses[warehouse_index].id,
                "latitude": round(base_lat + (index % 5) * 0.035, 6),
                "longitude": round(base_lon + (index % 4) * 0.04, 6),
            },
        )
        if index < len(m5_stores):
            store.m5_store_id = external_id
            store.synthetic_code = None
            store.state_id = state_id
            store.name = store_name
        stores.append(store)

    products: list[Product] = []
    for catalog_index, entry in enumerate(catalog["products"], start=1):
        item_id = str(entry["item_id"])
        product_identity = {"m5_item_id": item_id}
        if session.scalar(select(Product).filter_by(m5_item_id=item_id)) is None:
            product_identity = {"name": f"Synthetic Product {catalog_index:03d}"}
        products.append(
            _get_or_create(
                session,
                Product,
                product_identity,
                {
                    "department_id": str(entry["dept_id"]),
                    "category_id": str(entry["cat_id"]),
                    "name": str(entry.get("name") or item_id),
                    "unit_of_measure": "unit",
                    "unit_cost": 0,
                },
            )
        )
        products[-1].m5_item_id = item_id
        products[-1].department_id = str(entry["dept_id"])
        products[-1].category_id = str(entry["cat_id"])
        if entry.get("name"):
            products[-1].name = str(entry["name"])

    # These are explicitly synthetic products, not fabricated M5 identifiers.
    while len(products) < NETWORK_CONFIG["products"]:
        index = len(products) + 1
        products.append(
            _get_or_create(
                session,
                Product,
                {"name": f"Synthetic Product {index:03d}"},
                {"unit_of_measure": "unit", "unit_cost": 0},
            )
        )

    for index in range(NETWORK_CONFIG["trucks"]):
        distributor_index = index % 2
        _get_or_create(
            session,
            Truck,
            {"registration_number": f"SYN-TRK-{index + 1:03d}"},
            {
                "distributor_id": distributors[distributor_index].id,
                "capacity": 10_000,
                "fuel_efficiency": 8.5,
            },
        )

    for distributor_index, distributor in enumerate(distributors):
        for driver_index in range(5):
            name = (
                f"Synthetic Driver {distributor_index + 1:02d}-{driver_index + 1:02d}"
            )
            _get_or_create(
                session,
                Driver,
                {"distributor_id": distributor.id, "name": name},
                {
                    "salary_type": "monthly",
                    "base_salary": 0,
                    "per_distance_rate": 0,
                },
            )

    for product in products:
        for warehouse in warehouses:
            _get_or_create(
                session,
                Inventory,
                {"product_id": product.id, "warehouse_id": warehouse.id},
                {"quantity_on_hand": 0, "quantity_reserved": 0, "reorder_level": 0},
            )
        for store in stores:
            _get_or_create(
                session,
                Inventory,
                {"product_id": product.id, "store_id": store.id},
                {"quantity_on_hand": 0, "quantity_reserved": 0, "reorder_level": 0},
            )

    session.flush()
    counts = {
        "manufacturers": int(
            session.scalar(select(func.count()).select_from(Manufacturer)) or 0
        ),
        "distributors": int(
            session.scalar(select(func.count()).select_from(Distributor)) or 0
        ),
        "warehouses": int(
            session.scalar(select(func.count()).select_from(Warehouse)) or 0
        ),
        "stores": int(session.scalar(select(func.count()).select_from(Store)) or 0),
        "products": int(session.scalar(select(func.count()).select_from(Product)) or 0),
        "trucks": int(session.scalar(select(func.count()).select_from(Truck)) or 0),
        "drivers": int(session.scalar(select(func.count()).select_from(Driver)) or 0),
        "inventory_records": int(
            session.scalar(select(func.count()).select_from(Inventory)) or 0
        ),
        "warehouse_inventory_records": int(
            session.scalar(
                select(func.count())
                .select_from(Inventory)
                .where(Inventory.warehouse_id.is_not(None))
            )
            or 0
        ),
        "store_inventory_records": int(
            session.scalar(
                select(func.count())
                .select_from(Inventory)
                .where(Inventory.store_id.is_not(None))
            )
            or 0
        ),
        "stores_per_distributor_1": int(
            session.scalar(
                select(func.count())
                .select_from(Store)
                .where(Store.distributor_id == distributors[0].id)
            )
            or 0
        ),
        "stores_per_distributor_2": int(
            session.scalar(
                select(func.count())
                .select_from(Store)
                .where(Store.distributor_id == distributors[1].id)
            )
            or 0
        ),
        "stores_per_warehouse_1": int(
            session.scalar(
                select(func.count())
                .select_from(Store)
                .where(Store.assigned_warehouse_id == warehouses[0].id)
            )
            or 0
        ),
        "stores_per_warehouse_2": int(
            session.scalar(
                select(func.count())
                .select_from(Store)
                .where(Store.assigned_warehouse_id == warehouses[1].id)
            )
            or 0
        ),
        "stores_per_warehouse_3": int(
            session.scalar(
                select(func.count())
                .select_from(Store)
                .where(Store.assigned_warehouse_id == warehouses[2].id)
            )
            or 0
        ),
        "trucks_per_distributor_1": int(
            session.scalar(
                select(func.count())
                .select_from(Truck)
                .where(Truck.distributor_id == distributors[0].id)
            )
            or 0
        ),
        "trucks_per_distributor_2": int(
            session.scalar(
                select(func.count())
                .select_from(Truck)
                .where(Truck.distributor_id == distributors[1].id)
            )
            or 0
        ),
        "drivers_per_distributor_1": int(
            session.scalar(
                select(func.count())
                .select_from(Driver)
                .where(Driver.distributor_id == distributors[0].id)
            )
            or 0
        ),
        "drivers_per_distributor_2": int(
            session.scalar(
                select(func.count())
                .select_from(Driver)
                .where(Driver.distributor_id == distributors[1].id)
            )
            or 0
        ),
    }
    return counts


def run_seed(engine: Engine, catalog_path: Path | None) -> dict[str, int]:
    catalog = load_catalog(catalog_path)
    with Session(engine) as session, session.begin():
        return seed_database(session, catalog)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed the synthetic supply-chain network"
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=(
            Path(os.environ["M5_SEED_CATALOG"])
            if "M5_SEED_CATALOG" in os.environ
            else None
        ),
        help="Optional JSON catalog containing actual M5 store and product identifiers",
    )
    args = parser.parse_args()
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL must point to an already migrated database")
    counts = run_seed(create_engine(database_url), args.catalog)
    print("Seed complete (safe to rerun):")
    for label, count in counts.items():
        print(f"  {label}: {count}")
    with Session(create_engine(database_url)) as session:
        for store in session.scalars(select(Store).order_by(Store.name)):
            print(
                f"  store {store.name}: {store.latitude}, {store.longitude} -> {store.assigned_warehouse.name}"
            )
        for warehouse in session.scalars(select(Warehouse).order_by(Warehouse.name)):
            print(
                f"  warehouse {warehouse.name}: {warehouse.latitude}, {warehouse.longitude}"
            )


if __name__ == "__main__":
    main()
