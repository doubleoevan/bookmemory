from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from pgvector.sqlalchemy import Vector

from bookmemory_api.db.models.base import Base


class BookmarkChunk(Base):
    __tablename__ = "bookmark_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # delete bookmark chunks when their bookmark is deleted
    bookmark_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookmarks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # deterministic order of chunks within a bookmark
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    # raw text content of the chunk produced during http ingestion
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # vector embedding generated asynchronously with OpenAI text-embedding-3-small
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(1536),  # text-embedding-3-small
        nullable=True,
    )


Index(
    "ix_bookmark_chunks_bookmark_id_chunk_index_unique",
    BookmarkChunk.bookmark_id,
    BookmarkChunk.chunk_index,
    unique=True,
)
