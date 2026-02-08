"""bookmark status no_content and vector index

Revision ID: 18161e338c53
Revises: ba173e27c591
Create Date: 2026-02-06 17:10:44.524564

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "18161e338c53"
down_revision: Union[str, None] = "ba173e27c591"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # add no_content to the bookmark_status enum
    op.execute("ALTER TYPE bookmark_status ADD VALUE IF NOT EXISTS 'no_content'")

    # vector index for cosine similarity search
    op.execute("""
               CREATE INDEX IF NOT EXISTS ix_bookmark_chunks_embedding_hnsw_cosine
                   ON bookmark_chunks
                       USING hnsw (embedding vector_cosine_ops)
                   WHERE embedding IS NOT NULL
               """)


def downgrade() -> None:
    # drop the vector index
    op.execute("DROP INDEX IF EXISTS ix_bookmark_chunks_embedding_hnsw_cosine")
