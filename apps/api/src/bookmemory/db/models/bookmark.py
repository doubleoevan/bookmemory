from __future__ import annotations

import uuid
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bookmemory.db.models.base import Base
from bookmemory.db.models.bookmark_tag import bookmark_tags


if TYPE_CHECKING:
    from bookmemory.db.models.tag import Tag


class BookmarkType(str, Enum):
    link = "link"
    note = "note"
    file = "file"


class BookmarkStatus(str, Enum):
    created = "created"  # saved but not loaded yet
    loading = "loading"  # fetching + extracting + chunking
    processing = "processing"  # AI work: embedding + summarizing
    ready = "ready"
    no_content = "no_content"  # loaded but extracted text was empty or too small
    failed = "failed"


class PreviewMethod(str, Enum):
    content = "content"
    web = "web"


class LoadMethod(str, Enum):
    http = "http"
    playwright = "playwright"
    read = "read"
    manual = "manual"


@dataclass(frozen=True)
class ExtractedContent:
    title: str
    content: str
    load_method: LoadMethod


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

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    type: Mapped[BookmarkType] = mapped_column(
        SAEnum(BookmarkType, name="bookmark_type"),
        nullable=False,
        default=BookmarkType.link,
    )

    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[BookmarkStatus] = mapped_column(
        SAEnum(BookmarkStatus, name="bookmark_status"),
        nullable=False,
        default=BookmarkStatus.created,
        index=True,
    )

    load_method: Mapped[Optional[LoadMethod]] = mapped_column(
        SAEnum(LoadMethod, name="load_method"),
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


Index(
    "ix_bookmarks_user_id_url_unique_not_null",
    Bookmark.user_id,
    Bookmark.url,
    unique=True,
    postgresql_where=Bookmark.url.isnot(None),
)
