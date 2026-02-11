from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bookmemory.services.auth.users import get_current_user
from bookmemory.db.models.bookmark import (
    Bookmark,
    BookmarkStatus,
)
from bookmemory.db.models.bookmark_chunk import BookmarkChunk
from bookmemory.db.session import get_db
from bookmemory.schemas.bookmarks import (
    BookmarkSearchResponse,
    to_bookmark_response,
    TagMode,
)
from bookmemory.schemas.users import CurrentUser
from bookmemory.services.bookmarks.get_bookmark import get_user_bookmark

router = APIRouter()

MINIMUM_SIMILARITY_SCORE = 0.30  # any related score lower than this will be ignored


@router.get("/{bookmark_id}/related", response_model=list[BookmarkSearchResponse])
async def get_related_bookmarks(
    bookmark_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    tag_mode: TagMode = Query(default="ignore"),
    limit: int = Query(default=10, ge=1, le=20),
) -> list[BookmarkSearchResponse]:
    # find the bookmark or throw a 404 if not found
    user_id: UUID = current_user.id
    try:
        bookmark = await get_user_bookmark(
            bookmark_id=bookmark_id,
            user_id=user_id,
            session=session,
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="bookmark not found")

    # load the embedding for the first bookmark chunk
    select_bookmark_chunk_statement = (
        select(BookmarkChunk)
        .where(
            and_(
                BookmarkChunk.bookmark_id == bookmark.id,
                BookmarkChunk.embedding.isnot(None),
            )
        )
        .order_by(BookmarkChunk.chunk_index.asc())
        .limit(1)
    )
    bookmark_chunk = (
        await session.execute(select_bookmark_chunk_statement)
    ).scalar_one_or_none()
    if bookmark_chunk is None or bookmark_chunk.embedding is None:
        return []
    query_embedding = bookmark_chunk.embedding

    # select related bookmark chunks by distance to the query embedding
    chunk_distance = BookmarkChunk.embedding.cosine_distance(query_embedding)
    select_related_bookmarks_statement = (
        select(
            BookmarkChunk.id.label("chunk_id"),
            BookmarkChunk.bookmark_id.label("bookmark_id"),
            BookmarkChunk.text.label("chunk_text"),
            chunk_distance.label("distance"),
            func.row_number()
            .over(partition_by=BookmarkChunk.bookmark_id, order_by=chunk_distance.asc())
            .label("rn"),
        )
        .join(Bookmark, Bookmark.id == BookmarkChunk.bookmark_id)
        .where(
            and_(
                Bookmark.user_id == user_id,
                Bookmark.id != bookmark.id,
                Bookmark.status == BookmarkStatus.ready,
                BookmarkChunk.embedding.isnot(None),
            )
        )
        .order_by(chunk_distance.asc())
        .limit(max(limit * 50, 200))
    )
    sorted_bookmark_chunks_query = select_related_bookmarks_statement.subquery()
    most_relevant_bookmark_chunks_statement = (
        select(
            sorted_bookmark_chunks_query.c.chunk_id,
            sorted_bookmark_chunks_query.c.bookmark_id,
            sorted_bookmark_chunks_query.c.chunk_text,
            sorted_bookmark_chunks_query.c.distance,
        )
        .where(sorted_bookmark_chunks_query.c.rn == 1)
        .order_by(sorted_bookmark_chunks_query.c.distance.asc())
    )

    # return no results if no relevant bookmark chunks were found
    related_bookmark_chunks = (
        await session.execute(most_relevant_bookmark_chunks_statement)
    ).all()
    if not related_bookmark_chunks:
        return []

    # select and map related bookmarks to their IDs
    related_bookmark_ids = [
        related_chunk.bookmark_id for related_chunk in related_bookmark_chunks
    ]
    related_bookmarks_statement = (
        select(Bookmark)
        .where(and_(Bookmark.user_id == user_id, Bookmark.id.in_(related_bookmark_ids)))
        .options(selectinload(Bookmark.tags))
    )
    related_bookmarks = (
        (await session.execute(related_bookmarks_statement)).scalars().all()
    )
    related_bookmarks_by_id = {
        related_bookmark.id: related_bookmark for related_bookmark in related_bookmarks
    }

    # map related bookmark chunks to their bookmarks and return bookmark search results
    related_bookmark_responses: list[BookmarkSearchResponse] = []
    bookmark_tag_ids: set[UUID] = set()
    if tag_mode != "ignore":
        bookmark_tag_ids = {tag.id for tag in (bookmark.tags or [])}
    for related_chunk in related_bookmark_chunks:
        related_bookmark = related_bookmarks_by_id.get(related_chunk.bookmark_id)
        if related_bookmark is None:
            continue

        # filter out related bookmarks with a low similarity score
        distance = float(related_chunk.distance or 1.0)
        similarity_score = max(0.0, min(1.0, 1.0 - distance))
        if similarity_score < MINIMUM_SIMILARITY_SCORE:
            continue

        # filter related bookmarks out based on the tag mode
        if tag_mode != "ignore":
            related_tag_ids = {tag.id for tag in (related_bookmark.tags or [])}
            shared_tag_ids = bookmark_tag_ids.intersection(related_tag_ids)
            if tag_mode == "any" and not shared_tag_ids:
                continue
            if (
                tag_mode == "all"
                and bookmark_tag_ids
                and not bookmark_tag_ids.issubset(related_tag_ids)
            ):
                continue

        # generate a snippet of the related bookmark chunk
        snippet_text = (related_chunk.chunk_text or "").strip()
        snippet = snippet_text[:240] + ("…" if len(snippet_text) > 240 else "")

        # add the related bookmark to the search results
        related_bookmark_responses.append(
            BookmarkSearchResponse(
                **to_bookmark_response(related_bookmark).model_dump(),
                search_mode="related",
                snippet=snippet,
                score=similarity_score,
                chunk_id=related_chunk.chunk_id,
            )
        )

        # stop adding related bookmarks if we reach the limit
        if len(related_bookmark_responses) >= limit:
            break

    return related_bookmark_responses
