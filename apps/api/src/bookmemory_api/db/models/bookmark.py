from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bookmemory_api.db.models.base import Base
from bookmemory_api.db.models.bookmark_tag import bookmark_tags


if TYPE_CHECKING:
    from bookmemory_api.db.models.tag import Tag


class BookmarkType(str, enum.Enum):
    link = "link"
    note = "note"
    file = "file"


class BookmarkStatus(str, enum.Enum):
    created = "created"  # saved but not loaded yet
    loading = "loading"  # fetching + extracting + chunking
    processing = "processing"  # AI work (summaries, embeddings)
    ready = "ready"
    failed = "failed"


class IngestMethod(str, enum.Enum):
    http = "http"
    playwright = "playwright"
    read = "read"
    manual = "manual"


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # title is required.
    # default comes from scrape.
    # user may override later.
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    # optional user-provided description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # link, note, file
    type: Mapped[BookmarkType] = mapped_column(
        Enum(BookmarkType, name="bookmark_type"),
        nullable=False,
        default=BookmarkType.link,
    )

    # nullable for note or file
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # content scraped from a link or file at ingestion time, manually entered for note
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # nullable summary created by AI provider
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # created, loading, processing, ready, failed
    status: Mapped[BookmarkStatus] = mapped_column(
        Enum(BookmarkStatus, name="bookmark_status"),
        nullable=False,
        default=BookmarkStatus.created,
        index=True,
    )

    # http or playwright for links, read for files, manual for notes
    ingest_method: Mapped[Optional[IngestMethod]] = mapped_column(
        Enum(IngestMethod, name="ingest_method"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=bookmark_tags,
        back_populates="bookmarks",
        lazy="selectin",
    )


# partial unique index so that url can be NULL for future types
Index(
    "ix_bookmarks_user_id_url_unique_not_null",
    Bookmark.user_id,
    Bookmark.url,
    unique=True,
    postgresql_where=Bookmark.url.isnot(None),
)
