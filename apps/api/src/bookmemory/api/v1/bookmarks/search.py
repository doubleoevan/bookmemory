from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bookmemory.db.models.bookmark import Bookmark, BookmarkStatus
from bookmemory.db.session import get_db
from bookmemory.schemas.bookmarks import (
    BookmarkSearchResponse,
    TagMode,
    to_bookmark_response,
)
from bookmemory.schemas.users import CurrentUser
from bookmemory.services.auth.users import get_current_user
from bookmemory.services.embedding.chunk_embed import embed_chunks
from bookmemory.services.tags.normalize_tags import normalize_tags
from bookmemory.services.search.semantic_search import (
    semantic_search,
    SemanticSearchResult,
)
from bookmemory.services.search.keyword_search import (
    keyword_search,
    KeywordSearchResult,
)

router = APIRouter()

# how important each search result type is
SEMANTIC_RESULT_WEIGHT = 0.60
KEYWORD_RESULT_WEIGHT = 0.40

# the minimum match score to return a resul
MINIMUM_SCORE = 0.25


class BookmarkSearchRequest(BaseModel):
    search: str = Field(min_length=1)
    limit: int = Field(default=20, ge=1, le=50)
    tags: list[str] | None = None
    tag_mode: TagMode = "ignore"


def build_snippet(text: str, max_length: int = 320) -> str:
    snippet_text = (text or "").strip().replace("\n", " ")
    if len(snippet_text) <= max_length:
        return snippet_text
    return snippet_text[: max_length - 1] + "…"


@dataclass
class SearchResult:
    bookmark_id: UUID
    chunk_id: UUID
    chunk_text: str
    score: float


def _are_tags_valid(
    *,
    bookmark: Bookmark,
    tag_mode: TagMode,
    tags: list[str],
) -> bool:
    if tag_mode == "ignore":
        return True
    bookmark_tags = {tag.name for tag in (bookmark.tags or [])}
    if tag_mode == "any":
        return any(tag in bookmark_tags for tag in tags)
    if tag_mode == "all":
        return all(tag in bookmark_tags for tag in tags)
    return True


@router.post("/search", response_model=list[BookmarkSearchResponse])
async def search_bookmarks(
    payload: BookmarkSearchRequest,
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[BookmarkSearchResponse]:
    search_text = payload.search.strip()
    if search_text == "":
        raise HTTPException(status_code=422, detail="search is required")

    # normalize tags and fix tag_mode if needed
    normalized_tags = normalize_tags(payload.tags)
    tag_mode = payload.tag_mode
    if tag_mode != "ignore" and len(normalized_tags) == 0:
        tag_mode = "ignore"

    # run a semantic search and map the esults to bookmark ids
    user_id: UUID = current_user.id
    query_embedding = (await embed_chunks([search_text]))[0]
    semantic_results: list[SemanticSearchResult] = await semantic_search(
        session=session,
        user_id=user_id,
        search=query_embedding,
        limit=payload.limit,
        oversample=10,
    )
    semantic_result_by_bookmark: dict[UUID, SemanticSearchResult] = {
        search_result.bookmark_id: search_result for search_result in semantic_results
    }

    # run keyword search and map the results to bookmark ids
    keyword_results: list[KeywordSearchResult] = await keyword_search(
        session=session,
        user_id=user_id,
        search=search_text,
        limit=payload.limit,
        oversample=10,
        language="english",
    )
    keyword_result_by_bookmark: dict[UUID, KeywordSearchResult] = {
        search_result.bookmark_id: search_result for search_result in keyword_results
    }

    # combine semantic and keyword search result bookmark ids
    # or return an empty list if there are no results
    search_result_bookmark_ids = set(semantic_result_by_bookmark.keys()) | set(
        keyword_result_by_bookmark.keys()
    )
    if not search_result_bookmark_ids:
        return []

    # load user bookmarks with tags for filtering
    select_bookmarks_statements = (
        select(Bookmark)
        .where(
            and_(
                Bookmark.user_id == user_id,
                Bookmark.status == BookmarkStatus.ready,
                Bookmark.id.in_(list(search_result_bookmark_ids)),
            )
        )
        .options(selectinload(Bookmark.tags))
    )
    user_bookmarks = (
        (await session.execute(select_bookmarks_statements)).scalars().all()
    )
    user_bookmarks_by_id = {bookmark.id: bookmark for bookmark in user_bookmarks}

    # use the highest keyword score to divide
    # and normalize keyword scores to between 0 and 1
    max_keyword_score = 0.0
    for keyword_search_result in keyword_results:
        if keyword_search_result.keyword_score > max_keyword_score:
            max_keyword_score = keyword_search_result.keyword_score

    # combine semantic and keyword search results and sort them by score
    combined_results: list[SearchResult] = []
    for bookmark_id in search_result_bookmark_ids:
        # filter bookmarks by user
        bookmark = user_bookmarks_by_id.get(bookmark_id)
        if bookmark is None:
            continue

        # filter bookmarks by tags
        if not _are_tags_valid(
            bookmark=bookmark, tag_mode=tag_mode, tags=normalized_tags
        ):
            continue

        # calculate the semantic score for the bookmark
        semantic_score = 0.0
        semantic_chunk_id: UUID | None = None
        semantic_text: str | None = None
        semantic_search_result = semantic_result_by_bookmark.get(bookmark_id)
        if semantic_search_result is not None:
            semantic_score = semantic_search_result.semantic_score
            semantic_chunk_id = semantic_search_result.chunk_id
            semantic_text = semantic_search_result.chunk_text

        # calculate the keyword score for the bookmark
        keyword_score = 0.0
        keyword_chunk_id: UUID | None = None
        keyword_text: str | None = None
        keyword_result: KeywordSearchResult | None = keyword_result_by_bookmark.get(
            bookmark_id
        )
        if keyword_result is not None:
            if max_keyword_score > 0.0:
                keyword_score = keyword_result.keyword_score / max_keyword_score
            keyword_chunk_id = keyword_result.chunk_id
            keyword_text = keyword_result.chunk_text

        # filter out results with low scores
        search_result_score = (SEMANTIC_RESULT_WEIGHT * semantic_score) + (
            KEYWORD_RESULT_WEIGHT * keyword_score
        )
        if search_result_score < MINIMUM_SCORE:
            continue

        # choose a representative to chunk use for a snippet
        # prefer keyword chunks over semantic chunks for highlighting
        if keyword_chunk_id is not None and keyword_text is not None:
            chunk_id = keyword_chunk_id
            chunk_text = keyword_text
        elif semantic_chunk_id is not None and semantic_text is not None:
            chunk_id = semantic_chunk_id
            chunk_text = semantic_text
        else:
            # shouldn't happen, but just in case
            continue

        # add the combined search result
        combined_results.append(
            SearchResult(
                bookmark_id=bookmark_id,
                chunk_id=chunk_id,
                chunk_text=chunk_text,
                score=float(max(0.0, min(1.0, search_result_score))),
            )
        )

    # sort and limit the results by score
    combined_results.sort(key=lambda search_result: search_result.score, reverse=True)
    sorted_search_results = combined_results[: payload.limit]

    # return the search results as responses
    search_responses: list[BookmarkSearchResponse] = []
    for search_result in sorted_search_results:
        bookmark = user_bookmarks_by_id.get(search_result.bookmark_id)
        if bookmark is None:
            continue

        search_responses.append(
            BookmarkSearchResponse(
                **to_bookmark_response(bookmark).model_dump(),
                search_mode="search",
                snippet=build_snippet(search_result.chunk_text),
                score=search_result.score,
                chunk_id=search_result.chunk_id,
            )
        )

    return search_responses
