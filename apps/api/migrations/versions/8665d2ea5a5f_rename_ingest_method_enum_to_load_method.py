"""rename ingest_method enum to load_method

Revision ID: 8665d2ea5a5f
Revises: dbc07a6dd6a6
Create Date: 2026-02-05 22:55:06.900286

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8665d2ea5a5f"
down_revision: Union[str, None] = "dbc07a6dd6a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # rename the enum type to match the column cast SQLAlchemy is emitting
    op.execute("ALTER TYPE ingest_method RENAME TO load_method")


def downgrade() -> None:
    op.execute("ALTER TYPE load_method RENAME TO ingest_method")
