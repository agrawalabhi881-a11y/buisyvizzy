"""backfill coordinates and require geographic locations

Revision ID: c36f91b12a70
Revises: a48ff2a5e24c
Create Date: 2026-11-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c36f91b12a70"
down_revision: str | None = "a48ff2a5e24c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Backfill legacy rows deterministically before making coordinates required.
    op.execute(
        "UPDATE stores SET state_id = CASE WHEN id % 3 = 0 THEN 'WI' "
        "WHEN id % 3 = 1 THEN 'CA' ELSE 'TX' END WHERE state_id IS NULL"
    )
    op.execute(
        "UPDATE stores SET latitude = CASE state_id WHEN 'CA' THEN 34.05 "
        "WHEN 'TX' THEN 32.78 WHEN 'WI' THEN 43.04 ELSE 39.0 END "
        "+ (id % 5) * 0.035 WHERE latitude IS NULL"
    )
    op.execute(
        "UPDATE stores SET longitude = CASE state_id WHEN 'CA' THEN -118.24 "
        "WHEN 'TX' THEN -96.80 WHEN 'WI' THEN -87.91 ELSE -98.0 END "
        "+ (id % 4) * 0.04 WHERE longitude IS NULL"
    )
    op.execute(
        "UPDATE warehouses SET latitude = CASE WHEN id % 3 = 1 THEN 34.0522 "
        "WHEN id % 3 = 2 THEN 32.7767 ELSE 43.0389 END WHERE latitude IS NULL"
    )
    op.execute(
        "UPDATE warehouses SET longitude = CASE WHEN id % 3 = 1 THEN -118.2437 "
        "WHEN id % 3 = 2 THEN -96.7970 ELSE -87.9065 END WHERE longitude IS NULL"
    )
    op.drop_constraint("ck_store_latitude", "stores", type_="check")
    op.drop_constraint("ck_store_longitude", "stores", type_="check")
    op.drop_constraint("ck_warehouse_latitude", "warehouses", type_="check")
    op.drop_constraint("ck_warehouse_longitude", "warehouses", type_="check")
    op.create_check_constraint(
        "ck_store_latitude", "stores", "latitude BETWEEN -90 AND 90"
    )
    op.create_check_constraint(
        "ck_store_longitude", "stores", "longitude BETWEEN -180 AND 180"
    )
    op.create_check_constraint(
        "ck_warehouse_latitude", "warehouses", "latitude BETWEEN -90 AND 90"
    )
    op.create_check_constraint(
        "ck_warehouse_longitude", "warehouses", "longitude BETWEEN -180 AND 180"
    )
    op.alter_column("stores", "latitude", existing_type=sa.Float(), nullable=False)
    op.alter_column("stores", "longitude", existing_type=sa.Float(), nullable=False)
    op.alter_column("warehouses", "latitude", existing_type=sa.Float(), nullable=False)
    op.alter_column("warehouses", "longitude", existing_type=sa.Float(), nullable=False)


def downgrade() -> None:
    op.alter_column("warehouses", "longitude", existing_type=sa.Float(), nullable=True)
    op.alter_column("warehouses", "latitude", existing_type=sa.Float(), nullable=True)
    op.alter_column("stores", "longitude", existing_type=sa.Float(), nullable=True)
    op.alter_column("stores", "latitude", existing_type=sa.Float(), nullable=True)
    op.drop_constraint("ck_warehouse_longitude", "warehouses", type_="check")
    op.drop_constraint("ck_warehouse_latitude", "warehouses", type_="check")
    op.drop_constraint("ck_store_longitude", "stores", type_="check")
    op.drop_constraint("ck_store_latitude", "stores", type_="check")
    op.create_check_constraint(
        "ck_warehouse_latitude",
        "warehouses",
        "latitude IS NULL OR latitude BETWEEN -90 AND 90",
    )
    op.create_check_constraint(
        "ck_warehouse_longitude",
        "warehouses",
        "longitude IS NULL OR longitude BETWEEN -180 AND 180",
    )
    op.create_check_constraint(
        "ck_store_latitude", "stores", "latitude IS NULL OR latitude BETWEEN -90 AND 90"
    )
    op.create_check_constraint(
        "ck_store_longitude",
        "stores",
        "longitude IS NULL OR longitude BETWEEN -180 AND 180",
    )
