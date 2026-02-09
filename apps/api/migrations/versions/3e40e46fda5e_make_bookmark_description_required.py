"""make bookmark description required

Revision ID: 3e40e46fda5e
Revises: 4774050f1e8c
Create Date: 2026-02-09 01:14:50.607757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e40e46fda5e'
down_revision: Union[str, None] = '4774050f1e8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "bookmarks",
        "description",
        existing_type=sa.Text(),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "bookmarks",
        "description",
        existing_type=sa.Text(),
        nullable=True,
    )

