"""rename ingest_method to load_method

Revision ID: dbc07a6dd6a6
Revises: 696572ef5e1e
Create Date: 2026-02-05 22:39:11.157835

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "dbc07a6dd6a6"
down_revision: Union[str, None] = "696572ef5e1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "bookmarks",
        "ingest_method",
        new_column_name="load_method",
    )


def downgrade() -> None:
    op.alter_column(
        "bookmarks",
        "load_method",
        new_column_name="ingest_method",
    )
