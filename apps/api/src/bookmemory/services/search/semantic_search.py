from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory.db.models.bookmark import Bookmark, BookmarkStatus
from bookmemory.db.models.bookmark_chunk import BookmarkChunk


@dataclass(frozen=True)
class SemanticSearchResult:
    bookmark_id: UUID
    chunk_id: UUID
    chunk_text: str
    semantic_score: float  # 0..1 (higher is better)


async def semantic_search(
    *,
    session: AsyncSession,
    user_id: UUID,
    search: list[float],
    limit: int,
    oversample: int = 10,  # fetch extra candidates before ranking
) -> list[SemanticSearchResult]:
    """Returns the best bookmark chunks ranked by semantic similarity."""
    chunk_distance = BookmarkChunk.embedding.cosine_distance(search)

    # select matching bookmark chunks and rank them by semantic distance
    search_chunks_statement = (
        select(
            BookmarkChunk.id.label("chunk_id"),
            BookmarkChunk.bookmark_id.label("bookmark_id"),
            BookmarkChunk.text.label("chunk_text"),
            chunk_distance.label("distance"),
            func.row_number()
            .over(
                partition_by=BookmarkChunk.bookmark_id,
                order_by=chunk_distance.asc(),
            )
            .label("rn"),
        )
        .join(Bookmark, Bookmark.id == BookmarkChunk.bookmark_id)
        .where(
            and_(
                Bookmark.user_id == user_id,
                Bookmark.status == BookmarkStatus.ready,
                BookmarkChunk.embedding.isnot(None),
            )
        )
        .order_by(chunk_distance.asc())
        .limit(max(limit * oversample, 50))
    )

    # sort results by semantic distance and limit to the top results
    search_results = search_chunks_statement.subquery()
    sort_results_statement = (
        select(
            search_results.c.bookmark_id,
            search_results.c.chunk_id,
            search_results.c.chunk_text,
            search_results.c.distance,
        )
        .where(search_results.c.rn == 1)
        .order_by(search_results.c.distance.asc())
        .limit(limit * oversample)
    )
    sorted_results = (await session.execute(sort_results_statement)).all()

    # return keyword search results
    semantic_search_results: list[SemanticSearchResult] = []
    for search_result in sorted_results:
        distance = float(search_result.distance or 1.0)
        semantic_score = max(0.0, min(1.0, 1.0 - distance))

        semantic_search_results.append(
            SemanticSearchResult(
                bookmark_id=search_result.bookmark_id,
                chunk_id=search_result.chunk_id,
                chunk_text=search_result.chunk_text,
                semantic_score=semantic_score,
            )
        )

    return semantic_search_results
