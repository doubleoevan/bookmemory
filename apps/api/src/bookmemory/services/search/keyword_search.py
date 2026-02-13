from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory.db.models.bookmark import Bookmark, BookmarkStatus
from bookmemory.db.models.bookmark_chunk import BookmarkChunk


@dataclass(frozen=True)
class KeywordSearchResult:
    bookmark_id: UUID
    chunk_id: UUID
    chunk_text: str
    keyword_score: float  # raw ts_rank (we normalize later)


async def keyword_search(
    *,
    session: AsyncSession,
    user_id: UUID,
    search: str,
    limit: int,
    oversample: int = 10,  # fetch extra candidates before ranking
    language: str = "english",
) -> list[KeywordSearchResult]:
    """Returns the best bookmark chunks ranked by Postgres full-text score."""
    search_query = func.plainto_tsquery(language, search)
    search_vector = func.to_tsvector(language, BookmarkChunk.text)
    search_rank = func.ts_rank_cd(search_vector, search_query)

    # select matching bookmark chunks and rank them by keyword score
    search_chunks_statement = (
        select(
            BookmarkChunk.id.label("chunk_id"),
            BookmarkChunk.bookmark_id.label("bookmark_id"),
            BookmarkChunk.text.label("chunk_text"),
            search_rank.label("rank"),
            func.row_number()
            .over(
                partition_by=BookmarkChunk.bookmark_id,
                order_by=search_rank.desc(),
            )
            .label("rn"),
        )
        .join(Bookmark, Bookmark.id == BookmarkChunk.bookmark_id)
        .where(
            and_(
                Bookmark.user_id == user_id,
                Bookmark.status == BookmarkStatus.ready,
                search_vector.op("@@")(search_query),
            )
        )
        .order_by(search_rank.desc())
        .limit(max(limit * oversample, 50))
    )
    search_results = search_chunks_statement.subquery()

    # sort results by keyword score and limit to the top results
    sort_results_statement = (
        select(
            search_results.c.bookmark_id,
            search_results.c.chunk_id,
            search_results.c.chunk_text,
            search_results.c.rank,
        )
        .where(search_results.c.rn == 1)
        .order_by(search_results.c.rank.desc())
        .limit(limit * oversample)
    )
    sorted_results = (await session.execute(sort_results_statement)).all()

    # return keyword search results
    keyword_search_results: list[KeywordSearchResult] = []
    for search_result in sorted_results:
        keyword_search_results.append(
            KeywordSearchResult(
                bookmark_id=search_result.bookmark_id,
                chunk_id=search_result.chunk_id,
                chunk_text=search_result.chunk_text,
                keyword_score=float(search_result.rank or 0.0),
            )
        )

    return keyword_search_results
