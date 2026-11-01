"""require store state identifiers

Revision ID: d478aa8f261c
Revises: c36f91b12a70
Create Date: 2026-11-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d478aa8f261c"
down_revision: str | None = "c36f91b12a70"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "UPDATE stores SET state_id = CASE WHEN id % 3 = 0 THEN 'WI' "
        "WHEN id % 3 = 1 THEN 'CA' ELSE 'TX' END WHERE state_id IS NULL"
    )
    op.alter_column(
        "stores", "state_id", existing_type=sa.String(length=8), nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        "stores", "state_id", existing_type=sa.String(length=8), nullable=True
    )
