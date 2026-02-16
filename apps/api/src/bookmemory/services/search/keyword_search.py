from __future__ import annotations

import re

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import and_, func, select, literal_column
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory.db.models.bookmark import Bookmark, BookmarkStatus
from bookmemory.db.models.bookmark_chunk import BookmarkChunk

from bookmemory.services.search.stopwords import STOP_WORDS


def _to_search_terms(search: str) -> list[str]:
    """Converts a search query to a list of search terms"""
    if not search:
        return []

    # lowercase and remove punctuation
    search = search.lower()
    search = re.sub(r"[^\w\s-]", " ", search)

    # remove stopwords and empty strings
    terms: list[str] = []
    for raw in search.split():
        term = re.sub(r"[^\w-]", "", raw)  # extra safety for tsquery
        if len(term) > 1 and term not in STOP_WORDS:
            terms.append(term)

    # dedupe and cap terms to protect against paragraph search
    return list(dict.fromkeys(terms))[:12]


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
    # build the search vector across relevant bookmark fields and the best chunk
    search_vector = func.to_tsvector(
        language,
        func.concat_ws(
            " ",
            func.coalesce(Bookmark.title, ""),
            func.coalesce(Bookmark.description, ""),
            func.coalesce(Bookmark.summary, ""),
            func.coalesce(BookmarkChunk.text, ""),
        ),
    )

    # build the rank vector to assign weights to each field
    search_rank_vector = (
        func.setweight(
            func.to_tsvector(language, func.coalesce(Bookmark.title, "")),
            literal_column("'A'"),
        )
        .op("||")(
            func.setweight(
                func.to_tsvector(language, func.coalesce(Bookmark.description, "")),
                literal_column("'B'"),
            )
        )
        .op("||")(
            func.setweight(
                func.to_tsvector(language, func.coalesce(Bookmark.summary, "")),
                literal_column("'B'"),
            )
        )
        .op("||")(
            func.setweight(
                func.to_tsvector(language, func.coalesce(BookmarkChunk.text, "")),
                literal_column("'C'"),
            )
        )
    )

    # filter out stop words and punctuation
    search_terms = _to_search_terms(search)
    if not search_terms:
        return []

    # build the prefix query to match partial terms
    prefix_query_str = " & ".join(f"{term}:*" for term in search_terms)
    search_query = func.to_tsquery(language, prefix_query_str)

    # select matching bookmark chunks and rank them by keyword score
    search_rank = func.ts_rank_cd(search_rank_vector, search_query)
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
