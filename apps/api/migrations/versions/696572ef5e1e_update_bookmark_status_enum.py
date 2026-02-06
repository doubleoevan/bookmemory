"""update bookmark_status enum

Revision ID: 696572ef5e1e
Revises: bfcaa2465fc5
Create Date: 2026-02-05 21:17:21.835822

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "696572ef5e1e"
down_revision: Union[str, None] = "bfcaa2465fc5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # remove the old default
    op.execute("ALTER TABLE bookmarks ALTER COLUMN status DROP DEFAULT")

    # create a new enum without 'pending'
    op.execute("""
        CREATE TYPE bookmark_status_v2 AS ENUM ('created', 'loading', 'processing', 'ready', 'failed')
    """)

    # swap the column to the new enum
    op.execute("""
        ALTER TABLE bookmarks
        ALTER COLUMN status TYPE bookmark_status_v2
        USING status::text::bookmark_status_v2
    """)

    # drop the old enum type and rename the new one
    op.execute("DROP TYPE bookmark_status")
    op.execute("ALTER TYPE bookmark_status_v2 RENAME TO bookmark_status")

    # set the new default
    op.execute("ALTER TABLE bookmarks ALTER COLUMN status SET DEFAULT 'created'")


def downgrade() -> None:
    pass
