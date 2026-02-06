"""create bookmark_chunks

Revision ID: bfcaa2465fc5
Revises: 0f70344056e9
Create Date: 2026-02-05 14:49:07.317650

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "bfcaa2465fc5"
down_revision: Union[str, None] = "0f70344056e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ensure pgvector exists
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "bookmark_chunks",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "bookmark_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bookmarks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
    )

    op.create_index(
        "ix_bookmark_chunks_bookmark_id",
        "bookmark_chunks",
        ["bookmark_id"],
    )

    op.create_index(
        "ix_bookmark_chunks_bookmark_id_chunk_index_unique",
        "bookmark_chunks",
        ["bookmark_id", "chunk_index"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_bookmark_chunks_bookmark_id_chunk_index_unique",
        table_name="bookmark_chunks",
    )
    op.drop_index("ix_bookmark_chunks_bookmark_id", table_name="bookmark_chunks")
    op.drop_table("bookmark_chunks")
