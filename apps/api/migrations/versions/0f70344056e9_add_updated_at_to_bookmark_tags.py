"""add updated_at to bookmark_tags

Revision ID: 0f70344056e9
Revises: 0cb12c43c022
Create Date: 2026-02-05 13:22:51.289818

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0f70344056e9"
down_revision: Union[str, None] = "0cb12c43c022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bookmark_tags",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("bookmark_tags", "updated_at")
