from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bookmemory.services.tags.normalize_tags import normalize_tags
from bookmemory.db.models.bookmark import Bookmark, BookmarkStatus
from bookmemory.db.models.bookmark_chunk import BookmarkChunk
from bookmemory.db.models.tag import Tag
from bookmemory.db.session import get_db
from bookmemory.schemas.bookmarks import (
    BookmarkSearchResponse,
    to_bookmark_response,
    TagMode,
)
from bookmemory.schemas.users import CurrentUser
from bookmemory.services.auth.users import get_current_user
from bookmemory.services.embedding.chunk_embed import embed_chunks

router = APIRouter()

MINIMUM_SIMILARITY_SCORE = 0.25  # any similarity score lower than this will be ignored


class BookmarkSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=20, ge=1, le=50)

    # v1: allow multi-tag request shape even if UI only uses 0–1 tags today
    tags: list[str] | None = None
    tag_mode: TagMode = "ignore"


def build_snippet(text: str, max_length: int = 240) -> str:
    snippet_text = (text or "").strip().replace("\n", " ")
    if len(snippet_text) <= max_length:
        return snippet_text
    return snippet_text[: max_length - 1] + "…"


@router.post("/search", response_model=list[BookmarkSearchResponse])
async def search_bookmarks(
    payload: BookmarkSearchRequest,
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[BookmarkSearchResponse]:
    # validate the query
    query_text = payload.query.strip()
    if query_text == "":
        raise HTTPException(status_code=422, detail="query is required")

    # ignore any tag filtering if the user provided no tags
    normalized_tags = normalize_tags(payload.tags)
    tag_mode = payload.tag_mode
    if tag_mode != "ignore" and len(normalized_tags) == 0:
        tag_mode = "ignore"

    # search bookmark chunks by distance to the query embedding
    user_id: UUID = current_user.id
    query_embedding = (await embed_chunks([query_text]))[0]  # embed the query text
    chunk_distance = BookmarkChunk.embedding.cosine_distance(query_embedding)
    select_related_chunks_statement = (
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
        .limit(max(payload.limit * 10, 50))
    )

    # filter bookmark search results by requiring at least one matching tag
    if tag_mode == "any":
        select_related_chunks_statement = select_related_chunks_statement.join(
            Bookmark.tags
        ).where(
            and_(
                Tag.user_id == user_id,
                Tag.name.in_(normalized_tags),
            )
        )

    # filter bookmark search results by requiring all matching tags
    if tag_mode == "all":
        required_count = len(normalized_tags)
        select_matching_bookmarks_statement = (
            select(Bookmark.id.label("bookmark_id"))
            .join(Bookmark.tags)
            .where(
                and_(
                    Bookmark.user_id == user_id,
                    Tag.user_id == user_id,
                    Tag.name.in_(normalized_tags),
                )
            )
            .group_by(Bookmark.id)
            .having(func.count(func.distinct(Tag.name)) == required_count)
            .subquery()
        )
        select_related_chunks_statement = select_related_chunks_statement.join(
            select_matching_bookmarks_statement,
            select_matching_bookmarks_statement.c.bookmark_id == Bookmark.id,
        )

    # choose the most relevant bookmark chunk and sort by distance
    sorted_chunk_query = select_related_chunks_statement.subquery()
    most_relevant_chunks_statement = (
        select(
            sorted_chunk_query.c.chunk_id,
            sorted_chunk_query.c.bookmark_id,
            sorted_chunk_query.c.chunk_text,
            sorted_chunk_query.c.distance,
        )
        .where(sorted_chunk_query.c.rn == 1)
        .order_by(sorted_chunk_query.c.distance.asc())
        .limit(payload.limit)
    )

    # use bookmark chunks to build the bookmark search results
    related_chunks = (await session.execute(most_relevant_chunks_statement)).all()
    if not related_chunks:
        return []

    # load the related bookmarks for the bookmark chunks and map them by ID
    related_bookmark_ids = [row.bookmark_id for row in related_chunks]
    select_bookmarks_statement = (
        select(Bookmark)
        .where(and_(Bookmark.user_id == user_id, Bookmark.id.in_(related_bookmark_ids)))
        .options(selectinload(Bookmark.tags))
    )
    related_bookmarks = (
        (await session.execute(select_bookmarks_statement)).scalars().all()
    )
    related_bookmarks_by_id = {bookmark.id: bookmark for bookmark in related_bookmarks}

    # return bookmark search responses
    search_responses: list[BookmarkSearchResponse] = []
    for row in related_chunks:
        related_bookmark = related_bookmarks_by_id.get(row.bookmark_id)
        if related_bookmark is None:
            continue

        distance = float(row.distance or 1.0)
        similarity_score = max(0.0, min(1.0, 1.0 - distance))
        if similarity_score < MINIMUM_SIMILARITY_SCORE:
            continue

        search_responses.append(
            BookmarkSearchResponse(
                bookmark=to_bookmark_response(related_bookmark),
                snippet=build_snippet(row.chunk_text),
                score=similarity_score,
                chunk_id=row.chunk_id,
            )
        )

    return search_responses
