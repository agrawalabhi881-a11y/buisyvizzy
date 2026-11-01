from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd  # type: ignore[import-untyped]
from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.orm import Session

from app.ingestion.m5 import (
    M5_STORE_IDS,
    STATE_CENTROID_APPROXIMATIONS,
    STORE_DISTRIBUTOR_INDEX,
    STORE_LABELS,
    M5Paths,
    reconcile_database_to_m5_subset,
    select_m5_product_ids,
)
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
    project_root = Path(__file__).resolve().parents[2]
    paths = M5Paths.from_raw_dir(project_root / "data" / "raw" / "m5")
    if paths.missing():
        raise FileNotFoundError(
            "The M5 seed requires the original sales_train_validation.csv, "
            "calendar.csv and sell_prices.csv under data/raw/m5"
        )
    selected_ids = select_m5_product_ids(paths.sales, 50, paths.prices)
    metadata = pd.read_csv(
        paths.sales, usecols=["item_id", "dept_id", "cat_id", "store_id", "state_id"]
    )
    products_by_id = (
        metadata[["item_id", "dept_id", "cat_id"]]
        .drop_duplicates("item_id")
        .set_index("item_id")
    )
    stores_by_id = metadata[["store_id", "state_id"]].drop_duplicates()
    stores = [
        {
            "store_id": store_id,
            "state_id": str(
                stores_by_id.set_index("store_id").loc[store_id, "state_id"]
            ),
        }
        for store_id in M5_STORE_IDS
    ]
    products = [
        {
            "item_id": item_id,
            "dept_id": str(products_by_id.loc[item_id, "dept_id"]),
            "cat_id": str(products_by_id.loc[item_id, "cat_id"]),
        }
        for item_id in selected_ids
    ]
    if path is not None:
        supplied = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(supplied.get("stores"), list) or not isinstance(
            supplied.get("products"), list
        ):
            raise TypeError("M5 catalog 'stores' and 'products' values must be arrays")
        if {row.get("store_id") for row in supplied["stores"]} != set(M5_STORE_IDS):
            raise ValueError("Catalog must contain exactly the 10 original M5 stores")
        if {row.get("item_id") for row in supplied["products"]} != set(selected_ids):
            raise ValueError(
                "Catalog products must exactly match the deterministic 50-item M5 sample"
            )
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
    if len(catalog.get("stores", [])) != 10 or len(catalog.get("products", [])) != 50:
        raise ValueError(
            "Seed catalog must contain exactly 10 M5 stores and 50 M5 products"
        )
    if {entry["store_id"] for entry in catalog["stores"]} != set(M5_STORE_IDS):
        raise ValueError("Seed catalog must use all 10 original M5 store IDs")
    item_ids = {str(entry["item_id"]) for entry in catalog["products"]}
    if len(item_ids) != 50 or any("_" not in item_id for item_id in item_ids):
        raise ValueError("Seed catalog must contain 50 distinct original M5 item IDs")
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
    for entry in catalog["stores"]:
        external_id = str(entry["store_id"])
        state_id = str(entry["state_id"])
        distributor = distributors[STORE_DISTRIBUTOR_INDEX[external_id]]
        if state_id == "CA" and STORE_DISTRIBUTOR_INDEX[external_id] == 0:
            warehouse = warehouses[0]
        elif state_id == "TX" and STORE_DISTRIBUTOR_INDEX[external_id] == 0:
            warehouse = warehouses[1]
        else:
            warehouse = warehouses[2]
        store = _get_or_create(
            session,
            Store,
            {"m5_store_id": external_id},
            {
                "name": STORE_LABELS[external_id],
                "synthetic_code": None,
                "state_id": state_id,
                "distributor_id": distributor.id,
                "assigned_warehouse_id": warehouse.id,
                "latitude": STATE_CENTROID_APPROXIMATIONS.get(state_id, (39.8, -98.6))[
                    0
                ],
                "longitude": STATE_CENTROID_APPROXIMATIONS.get(state_id, (39.8, -98.6))[
                    1
                ],
                "location_source": "approximate_state_centroid_not_store_address",
            },
        )
        stores.append(store)

    products: list[Product] = []
    for entry in catalog["products"]:
        item_id = str(entry["item_id"])
        product = _get_or_create(
            session,
            Product,
            {"m5_item_id": item_id},
            {
                "department_id": str(entry["dept_id"]),
                "category_id": str(entry["cat_id"]),
                "name": item_id,
                "unit_of_measure": "unit",
                "unit_cost": 0,
            },
        )
        products.append(product)

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

    session.flush()
    cleanup = reconcile_database_to_m5_subset(
        session.connection(),
        {str(entry["item_id"]) for entry in catalog["products"]},
        {str(entry["store_id"]) for entry in catalog["stores"]},
    )
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
        "obsolete_stores_removed": cleanup["stores_removed"],
        "obsolete_products_removed": cleanup["products_removed"],
        "obsolete_inventory_records_removed": cleanup["inventory_records_removed"],
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
        description="Seed assumed supply-chain infrastructure around original M5 stores and products"
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=(
            Path(os.environ["M5_SEED_CATALOG"])
            if "M5_SEED_CATALOG" in os.environ
            else None
        ),
        help="Optional JSON file whose IDs must match the deterministic 10-store, 50-product M5 subset",
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
