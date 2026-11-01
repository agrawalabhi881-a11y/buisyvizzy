"""add stable codes for synthetic placeholder stores

Revision ID: ec92d82c4491
Revises: d478aa8f261c
Create Date: 2026-11-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "ec92d82c4491"
down_revision: str | None = "d478aa8f261c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "stores", sa.Column("synthetic_code", sa.String(length=32), nullable=True)
    )
    op.create_unique_constraint(
        "uq_stores_synthetic_code", "stores", ["synthetic_code"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_stores_synthetic_code", "stores", type_="unique")
    op.drop_column("stores", "synthetic_code")
