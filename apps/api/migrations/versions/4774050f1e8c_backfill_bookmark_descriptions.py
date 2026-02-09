"""backfill bookmark descriptions

Revision ID: 4774050f1e8c
Revises: 18161e338c53
Create Date: 2026-02-09 01:11:28.790391

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4774050f1e8c"
down_revision: Union[str, None] = "18161e338c53"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Backfill description from title where missing
    op.execute(
        sa.text(
            """
            UPDATE bookmarks
            SET description = title
            WHERE description IS NULL
              AND title IS NOT NULL
              AND title <> '';
            """
        )
    )

    # Final safety fallback (should be rare)
    op.execute(
        sa.text(
            """
            UPDATE bookmarks
            SET description = ''
            WHERE description IS NULL;
            """
        )
    )


def downgrade() -> None:
    pass
