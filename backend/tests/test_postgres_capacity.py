import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import DBAPIError


def test_postgres_capacity_trigger_enforces_aggregate_and_updates() -> None:
    database_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("set DATABASE_URL to run PostgreSQL trigger integration test")

    engine = create_engine(database_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            suffix = uuid4().hex
            manufacturer_id = connection.exec_driver_sql(
                "INSERT INTO manufacturers (name, location) VALUES (%s, %s) RETURNING id",
                (f"capacity-test-{suffix}", "test"),
            ).scalar_one()
            distributor_id = connection.exec_driver_sql(
                "INSERT INTO distributors (name, manufacturer_id, location) "
                "VALUES (%s, %s, %s) RETURNING id",
                (f"capacity-test-{suffix}", manufacturer_id, "test"),
            ).scalar_one()
            warehouse_id = connection.exec_driver_sql(
                "INSERT INTO warehouses "
                "(distributor_id, name, location, latitude, longitude, storage_capacity) "
                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (distributor_id, f"capacity-test-{suffix}", "test", 34.0, -118.0, 10),
            ).scalar_one()
            product_id = connection.exec_driver_sql(
                "INSERT INTO products "
                "(item_id, name, unit_of_measure, unit_cost, storage_units_per_item) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (f"cap-{suffix[:20]}", "capacity-test", "unit", 0, 2),
            ).scalar_one()

            connection.exec_driver_sql(
                "INSERT INTO inventories "
                "(product_id, warehouse_id, quantity_on_hand, quantity_reserved, reorder_level) "
                "VALUES (%s, %s, %s, %s, %s)",
                (product_id, warehouse_id, 4, 0, 0),
            )

            with pytest.raises(DBAPIError) as exceeded, connection.begin_nested():
                connection.exec_driver_sql(
                    "UPDATE warehouses SET storage_capacity = 7 WHERE id = %s",
                    (warehouse_id,),
                )
            assert getattr(exceeded.value.orig, "sqlstate", None) == "23514"

            with pytest.raises(DBAPIError) as exceeded, connection.begin_nested():
                connection.exec_driver_sql(
                    "INSERT INTO inventories "
                    "(product_id, warehouse_id, quantity_on_hand, quantity_reserved, reorder_level) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (product_id, warehouse_id, 2, 0, 0),
                )
            assert getattr(exceeded.value.orig, "sqlstate", None) == "23514"
        finally:
            transaction.rollback()
    engine.dispose()
