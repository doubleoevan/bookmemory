from __future__ import annotations

from typing import cast, List, Optional, Literal
from uuid import UUID

import anyio

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.limit_offset import LimitOffsetParams
from fastapi_pagination.ext.sqlalchemy import apaginate

import sqlalchemy as sa
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bookmemory_api.db.models.bookmark import (
    Bookmark,
    BookmarkStatus,
    BookmarkType,
    LoadMethod,
)
from bookmemory_api.db.models.bookmark_chunk import BookmarkChunk
from bookmemory_api.db.models.tag import Tag

from bookmemory_api.db.session import get_db

from bookmemory_api.schemas.users import CurrentUser
from bookmemory_api.schemas.bookmarks import (
    BookmarkCreateRequest,
    BookmarkResponse,
    TagResponse,
)

from bookmemory_api.api.dependencies.auth import get_current_user

from bookmemory_api.services.extraction.http_fetch import fetch_html, FetchError
from bookmemory_api.services.extraction.html_extract import extract_content
from bookmemory_api.services.extraction.text_chunk import chunk_text
from bookmemory_api.services.extraction.playwright_fetch import (
    PlaywrightFetchError,
    fetch_rendered_html,
)

MINIMUM_HTTP_LENGTH = (
    600  # switch to playwright if the extracted http length falls below a threshold
)
MAXIMUM_CONTENT_LENGTH = 250_000
MAXIMUM_FETCH_SECONDS = 35.0

# limit concurrent HTTP fetches to avoid tying up API workers
CONCURRENT_HTTP_FETCH_LIMIT = anyio.Semaphore(20)
CONCURRENT_PLAYWRIGHT_FETCH_LIMIT = anyio.Semaphore(
    2
)  # playwright uses a lot of resources

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


def _trim_extracted_text(text: str) -> str:
    trimmed = (text or "").strip()
    if len(trimmed) > MAXIMUM_CONTENT_LENGTH:
        return trimmed[:MAXIMUM_CONTENT_LENGTH]
    return trimmed


def _should_fallback_to_playwright(*, extracted_text: str) -> bool:
    """Returns true if the extracted text is too short"""
    return len((extracted_text or "").strip()) < MINIMUM_HTTP_LENGTH


def _normalize_tag_names(tag_names: list[str]) -> list[str]:
    # trim whitespace from bookmark tag names
    trimmed_tags = [name.strip() for name in tag_names if name.strip()]

    # remove duplicate bookmark tags
    unique_tags: set[str] = set()
    normalized_tags: list[str] = []
    for name in trimmed_tags:
        if name in unique_tags:
            continue
        unique_tags.add(name)
        normalized_tags.append(name)

    return normalized_tags


async def _get_or_create_tags(
    *,
    session: AsyncSession,
    user_id: UUID,
    tag_names: List[str],
) -> List[Tag]:
    # do nothing if there are no normalized tags
    normalized_tags = _normalize_tag_names(tag_names)
    if not normalized_tags:
        return []

    # check if tags already exist
    select_tags_statement = select(Tag).where(
        and_(Tag.user_id == user_id, Tag.name.in_(normalized_tags))
    )
    existing_tags = (await session.execute(select_tags_statement)).scalars().all()
    existing_tags_by_name = {tag.name: tag for tag in existing_tags}

    # check for new tags
    new_tags: list[Tag] = []
    for tag_name in normalized_tags:
        if tag_name in existing_tags_by_name:
            continue
        new_tag = Tag(user_id=user_id, name=tag_name)
        session.add(new_tag)
        new_tags.append(new_tag)

    # flush pending inserts so that new tags get IDs
    if new_tags:
        await session.flush()

    # return new and existing tags in the order they were provided
    tags: List[Tag] = []
    for tag in normalized_tags:
        if tag in existing_tags_by_name:
            tags.append(existing_tags_by_name[tag])
        else:
            for new_tag in new_tags:
                if new_tag.name == tag:
                    tags.append(new_tag)
                    break

    return tags


def _to_bookmark_response(bookmark: Bookmark) -> BookmarkResponse:
    return BookmarkResponse(
        id=bookmark.id,
        user_id=bookmark.user_id,
        title=bookmark.title,
        description=bookmark.description,
        type=bookmark.type.value,
        url=bookmark.url,
        status=bookmark.status.value,
        load_method=(bookmark.load_method.value if bookmark.load_method else None),
        created_at=bookmark.created_at,
        updated_at=bookmark.updated_at,
        tags=[TagResponse(id=tag.id, name=tag.name) for tag in bookmark.tags],
    )


@router.post("", response_model=BookmarkResponse)
async def create_bookmark(
    payload: BookmarkCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> BookmarkResponse:
    # create the tags
    user_id: UUID = current_user.id
    tags = await _get_or_create_tags(
        session=session,
        user_id=user_id,
        tag_names=payload.tags,
    )

    # validate required bookmark fields
    title = (payload.title or "").strip()
    if title == "":
        raise HTTPException(status_code=422, detail="title is required")
    bookmark_type = BookmarkType(payload.type)
    if bookmark_type == BookmarkType.link:
        url = (payload.url or "").strip()
        if url == "":
            raise HTTPException(
                status_code=422,
                detail="url is required for link bookmarks",
            )
    else:
        url = None  # url should be None unless the bookmark is a link

    # create the bookmark
    bookmark = Bookmark(
        user_id=user_id,
        title=title,
        description=(payload.description.strip() if payload.description else None),
        type=bookmark_type,
        url=url,
        status=BookmarkStatus.created,
        tags=tags,
    )
    session.add(bookmark)
    await session.commit()

    # return the newly created bookmark
    select_bookmark_statement = (
        select(Bookmark)
        .where(and_(Bookmark.id == bookmark.id, Bookmark.user_id == user_id))
        .options(selectinload(Bookmark.tags))
    )
    new_bookmark = (await session.execute(select_bookmark_statement)).scalar_one()
    return _to_bookmark_response(new_bookmark)


@router.get("", response_model=LimitOffsetPage[BookmarkResponse])
async def get_bookmarks(
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    query: Optional[str] = Query(default=None),
    search_mode: Literal["keyword", "semantic"] = Query(default="keyword"),
    tags: list[str] = Query(default_factory=list, alias="tag"),
    tag_mode: Literal["any", "all"] = Query(default="any"),
    sort: str = Query(
        default="alphabetical", pattern="^(alphabetical|recent|relevance)$"
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> LimitOffsetPage[BookmarkResponse]:
    # filter bookmarks by user ID
    user_id: UUID = current_user.id
    select_bookmarks_statement = (
        select(Bookmark)
        .where(Bookmark.user_id == user_id)
        .options(selectinload(Bookmark.tags))
    )

    # filter bookmarks by query
    query_text = query.strip() if query is not None else ""
    if query_text != "":
        if search_mode == "keyword":
            like_query = f"%{query_text}%"
            select_bookmarks_statement = select_bookmarks_statement.where(
                or_(
                    Bookmark.title.ilike(like_query),
                    Bookmark.url.ilike(like_query),
                    Bookmark.description.ilike(like_query),
                    Bookmark.summary.ilike(like_query),
                    Bookmark.content.ilike(like_query),
                )
            )
        else:
            # TODO: semantic search
            raise HTTPException(
                status_code=501,
                detail="semantic search is not implemented yet",
            )

    # filter bookmarks by tag
    normalized_tags = _normalize_tag_names(tags)
    if normalized_tags:
        select_bookmarks_statement = select_bookmarks_statement.join(
            Bookmark.tags
        ).where(
            and_(
                Tag.user_id == user_id,
                Tag.name.in_(normalized_tags),
            )
        )

        # select bookmarks with all or any tags based on the tag mode
        if tag_mode == "all":
            select_bookmarks_statement = select_bookmarks_statement.group_by(
                Bookmark.id
            ).having(func.count(func.distinct(Tag.id)) == len(normalized_tags))
        else:
            select_bookmarks_statement = select_bookmarks_statement.distinct(
                Bookmark.id
            )
    else:
        select_bookmarks_statement = select_bookmarks_statement.distinct(Bookmark.id)

    # validate sort options
    if sort == "relevance" and search_mode != "semantic":
        raise HTTPException(
            status_code=422,
            detail="sort=relevance is only valid for semantic search",
        )

    # sort bookmarks
    if sort == "alphabetical":
        select_bookmarks_statement = select_bookmarks_statement.order_by(
            func.lower(Bookmark.title).asc(),
            Bookmark.created_at.desc(),
        )
    elif sort == "recent":
        select_bookmarks_statement = select_bookmarks_statement.order_by(
            Bookmark.updated_at.desc()
        )
    else:
        # TODO: sort by relevance when semantic search is implemented
        select_bookmarks_statement = select_bookmarks_statement.order_by(
            Bookmark.updated_at.desc()
        )

    # select and return a page of bookmarks
    return cast(
        LimitOffsetPage[BookmarkResponse],
        await apaginate(
            session,
            select_bookmarks_statement,
            params=LimitOffsetParams(limit=limit, offset=offset),
            transformer=lambda items: [_to_bookmark_response(b) for b in items],
        ),
    )


@router.post("/{bookmark_id}/load", response_model=BookmarkResponse)
async def load_bookmark(
    bookmark_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> BookmarkResponse:
    user_id: UUID = current_user.id

    # get the bookmark from the database
    select_bookmark_statement = (
        select(Bookmark)
        .where(and_(Bookmark.id == bookmark_id, Bookmark.user_id == user_id))
        .options(selectinload(Bookmark.tags))
    )
    # verify that the bookmark exists
    bookmark = (await session.execute(select_bookmark_statement)).scalar_one_or_none()
    if bookmark is None:
        raise HTTPException(status_code=404, detail="bookmark not found")

    # do nothing for bookmark types that don't require loading
    if bookmark.type != BookmarkType.link and bookmark.type != BookmarkType.file:
        return _to_bookmark_response(bookmark)

    # verify that the bookmark has a URL
    if not bookmark.url or bookmark.url.strip() == "":
        raise HTTPException(status_code=422, detail="bookmark url is missing")

    # TODO: load a bookmark file from an s3 url
    if bookmark.type == BookmarkType.file:
        return _to_bookmark_response(bookmark)  # TODO: _to_file_response(bookmark)

    # delete any existing chunks to be replaced
    # and update the status to loading during extraction
    await session.execute(
        sa.delete(BookmarkChunk).where(BookmarkChunk.bookmark_id == bookmark.id)
    )
    bookmark.status = BookmarkStatus.loading
    bookmark.load_method = LoadMethod.http
    await session.commit()

    # attempt to load the content with http and fallback to playwright if necessary
    try:
        with anyio.fail_after(MAXIMUM_FETCH_SECONDS):
            try:
                # use semaphore to limit concurrent HTTP fetches
                async with CONCURRENT_HTTP_FETCH_LIMIT:
                    fetched_html = await fetch_html(url=bookmark.url)

                # extract the content from the fetched HTML
                extracted_content = extract_content(
                    html=fetched_html.html, url=bookmark.url
                )
                extracted_title = extracted_content.title
                extracted_text = _trim_extracted_text(extracted_content.text)

                # fallback to playwright if the extracted text is less than a threshold
                if _should_fallback_to_playwright(extracted_text=extracted_text):
                    raise FetchError("extracted text too small; likely JS-heavy")

            except FetchError as http_error:
                # retry with playwright if the content is blocked or dynamically rendered
                can_try_playwright_status = http_error.status_code in {401, 403, 429}
                can_try_playwright_message = (
                    "content-type" in str(http_error).lower()
                    or "js-heavy" in str(http_error).lower()
                    or "too small" in str(http_error).lower()
                )
                if not (can_try_playwright_status or can_try_playwright_message):
                    raise

                # use semaphore to aggressively limit resource-heavy concurrent playwright fetches
                async with CONCURRENT_PLAYWRIGHT_FETCH_LIMIT:
                    rendered = await fetch_rendered_html(url=bookmark.url)

                # extract the content from the fetched HTML
                extracted_content = extract_content(
                    html=rendered.html, url=rendered.url
                )
                extracted_title = extracted_content.title
                extracted_text = _trim_extracted_text(extracted_content.text)

                # update the load method to playwright
                bookmark.load_method = LoadMethod.playwright

            # update the title if it is valid
            if extracted_title and extracted_title.strip():
                bookmark.title = extracted_title.strip()

            # save the content and its chunks
            bookmark.content = extracted_text or ""
            chunks = chunk_text(text=bookmark.content)
            for idx, chunk in enumerate(chunks):
                session.add(
                    BookmarkChunk(
                        bookmark_id=bookmark.id,
                        chunk_index=idx,
                        text=chunk,
                        embedding=None,
                    )
                )

        # update the bookmark status
        bookmark.status = BookmarkStatus.ready
        await session.commit()

    except anyio.TimeoutError as error:
        await session.rollback()
        bookmark.status = BookmarkStatus.failed
        await session.commit()
        raise HTTPException(
            status_code=504,
            detail=f"load timed out after {MAXIMUM_FETCH_SECONDS}s",
        ) from error

    except PlaywrightFetchError as error:
        await session.rollback()
        bookmark.status = BookmarkStatus.failed
        await session.commit()
        raise HTTPException(status_code=502, detail=f"load failed: {error}") from error

    except FetchError as error:
        await session.rollback()
        bookmark.status = BookmarkStatus.failed
        await session.commit()
        raise HTTPException(status_code=502, detail=f"fetch failed: {error}") from error

    except Exception as error:
        await session.rollback()
        bookmark.status = BookmarkStatus.failed
        await session.commit()
        raise HTTPException(status_code=500, detail=f"load failed: {error}") from error

    # return the updated bookmark
    updated_bookmark = (await session.execute(select_bookmark_statement)).scalar_one()
    return _to_bookmark_response(updated_bookmark)
