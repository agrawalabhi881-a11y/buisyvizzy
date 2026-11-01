"""record whether store coordinates are verified or approximate

Revision ID: b2c3d4e5f607
Revises: f18a2ddc6f40
Create Date: 2026-11-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f607"
down_revision: str | None = "f18a2ddc6f40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "stores",
        sa.Column(
            "location_source",
            sa.String(length=80),
            server_default=sa.text("'approximate_seed_location'"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("stores", "location_source")
