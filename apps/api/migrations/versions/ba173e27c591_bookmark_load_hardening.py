"""bookmark load hardening

Revision ID: ba173e27c591
Revises: 8665d2ea5a5f
Create Date: 2026-02-06 17:10:27.523453

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "ba173e27c591"
down_revision: Union[str, None] = "8665d2ea5a5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # vector index for cosine similarity search
    op.execute("""
               CREATE INDEX IF NOT EXISTS ix_bookmark_chunks_embedding_hnsw_cosine
                   ON bookmark_chunks
                   USING hnsw (embedding vector_cosine_ops)
                   WHERE embedding IS NOT NULL
               """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_bookmark_chunks_embedding_hnsw_cosine")
