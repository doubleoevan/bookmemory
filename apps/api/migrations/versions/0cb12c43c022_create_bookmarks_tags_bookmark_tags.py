"""create bookmarks tags bookmark_tags

Revision ID: 0cb12c43c022
Revises: e9885d3454c4
Create Date: 2026-02-05 11:16:59.326411

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0cb12c43c022"
down_revision: Union[str, None] = "e9885d3454c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- enums ---
    # Create the Postgres enum TYPES explicitly (idempotent with checkfirst=True).
    bookmark_type = postgresql.ENUM("link", "note", "file", name="bookmark_type")
    bookmark_status = postgresql.ENUM(
        "pending", "ready", "failed", name="bookmark_status"
    )
    ingest_method = postgresql.ENUM(
        "http", "playwright", "read", "manual", name="ingest_method"
    )

    bind = op.get_bind()
    bookmark_type.create(bind, checkfirst=True)
    bookmark_status.create(bind, checkfirst=True)
    ingest_method.create(bind, checkfirst=True)

    # IMPORTANT: table columns must not try to auto-create enum types again.
    bookmark_type_col = postgresql.ENUM(
        "link", "note", "file", name="bookmark_type", create_type=False
    )
    bookmark_status_col = postgresql.ENUM(
        "pending", "ready", "failed", name="bookmark_status", create_type=False
    )
    ingest_method_col = postgresql.ENUM(
        "http", "playwright", "read", "manual", name="ingest_method", create_type=False
    )

    # --- bookmarks ---
    op.create_table(
        "bookmarks",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", bookmark_type_col, nullable=False, server_default="link"),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "status", bookmark_status_col, nullable=False, server_default="pending"
        ),
        sa.Column("ingest_method", ingest_method_col, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index("ix_bookmarks_user_id", "bookmarks", ["user_id"])
    op.create_index("ix_bookmarks_status", "bookmarks", ["status"])

    # Partial unique index so url may be NULL for note/file
    op.create_index(
        "ix_bookmarks_user_id_url_unique_not_null",
        "bookmarks",
        ["user_id", "url"],
        unique=True,
        postgresql_where=sa.text("url IS NOT NULL"),
    )

    # --- tags ---
    op.create_table(
        "tags",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index("ix_tags_user_id", "tags", ["user_id"])
    op.create_index(
        "ix_tags_user_id_name_unique", "tags", ["user_id", "name"], unique=True
    )

    # --- join table ---
    op.create_table(
        "bookmark_tags",
        sa.Column(
            "bookmark_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bookmarks.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "tag_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tags.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("bookmark_tags")

    op.drop_index("ix_tags_user_id_name_unique", table_name="tags")
    op.drop_index("ix_tags_user_id", table_name="tags")
    op.drop_table("tags")

    op.drop_index("ix_bookmarks_user_id_url_unique_not_null", table_name="bookmarks")
    op.drop_index("ix_bookmarks_status", table_name="bookmarks")
    op.drop_index("ix_bookmarks_user_id", table_name="bookmarks")
    op.drop_table("bookmarks")

    op.execute("DROP TYPE IF EXISTS ingest_method")
    op.execute("DROP TYPE IF EXISTS bookmark_status")
    op.execute("DROP TYPE IF EXISTS bookmark_type")
