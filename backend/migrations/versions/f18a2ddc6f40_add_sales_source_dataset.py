"""record historical sales dataset provenance

Revision ID: f18a2ddc6f40
Revises: ec92d82c4491
Create Date: 2026-11-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f18a2ddc6f40"
down_revision: str | None = "ec92d82c4491"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "daily_sales_records",
        sa.Column(
            "source_dataset",
            sa.String(length=64),
            server_default=sa.text("'m5_forecasting'"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("daily_sales_records", "source_dataset")
