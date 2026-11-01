from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine

from app.ingestion.m5 import _postgres_copy_batch


def test_postgres_copy_batch_is_conflict_safe() -> None:
    database_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("set DATABASE_URL to run PostgreSQL COPY integration test")

    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql(
                "CREATE TEMP TABLE ingestion_copy_target "
                "(product_id integer, store_id integer, day_id integer, units integer, "
                "UNIQUE(product_id, store_id, day_id))"
            )
            connection.exec_driver_sql(
                "CREATE TEMP TABLE ingestion_copy_stage "
                "(product_id integer, store_id integer, day_id integer, units integer) "
                "ON COMMIT PRESERVE ROWS"
            )
            connection.commit()

            rows = [
                {"product_id": 1, "store_id": 2, "day_id": 3, "units": 4},
                {"product_id": 1, "store_id": 2, "day_id": 4, "units": 0},
            ]
            inserted = _postgres_copy_batch(
                connection,
                "ingestion_copy_stage",
                "ingestion_copy_target",
                ["product_id", "store_id", "day_id", "units"],
                rows,
                ["product_id", "store_id", "day_id"],
            )
            repeated = _postgres_copy_batch(
                connection,
                "ingestion_copy_stage",
                "ingestion_copy_target",
                ["product_id", "store_id", "day_id", "units"],
                rows,
                ["product_id", "store_id", "day_id"],
            )
            count = connection.exec_driver_sql(
                "SELECT count(*) FROM ingestion_copy_target"
            ).scalar_one()
            assert inserted == 2
            assert repeated == 0
            assert count == 2
    finally:
        engine.dispose()
