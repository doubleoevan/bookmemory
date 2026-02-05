from __future__ import annotations

from typing import cast, List, Optional, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.limit_offset import LimitOffsetParams
from fastapi_pagination.ext.sqlalchemy import apaginate

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bookmemory_api.db.models.bookmark import Bookmark, BookmarkStatus, BookmarkType
from bookmemory_api.db.models.tag import Tag
from bookmemory_api.db.session import get_db
from bookmemory_api.schemas.users import CurrentUser
from bookmemory_api.schemas.bookmarks import (
    BookmarkCreateRequest,
    BookmarkResponse,
    TagResponse,
)

from bookmemory_api.api.dependencies.auth import get_current_user


router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


def _normalize_tag_names(tag_names: list[str]) -> list[str]:
    # trim whitespace from tag names
    trimmed_tags = [name.strip() for name in tag_names if name.strip()]

    # remove duplicate tags
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
        ingest_method=(
            bookmark.ingest_method.value if bookmark.ingest_method else None
        ),
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
    # add the bookmark to be saved
    user_id: UUID = current_user.id
    bookmark = Bookmark(
        user_id=user_id,
        title=payload.title.strip(),
        description=(payload.description.strip() if payload.description else None),
        type=BookmarkType(payload.type),
        url=(payload.url.strip() if payload.url else None),
        status=BookmarkStatus.pending,
    )
    session.add(bookmark)

    # add the tags to the bookmark
    tags = await _get_or_create_tags(
        session=session,
        user_id=user_id,
        tag_names=payload.tags,
    )
    bookmark.tags = tags

    # save the bookmark and tags to get a bookmark ID
    await session.commit()

    # return the newly created bookmark
    select_bookmark_statment = (
        select(Bookmark)
        .where(and_(Bookmark.id == bookmark.id, Bookmark.user_id == user_id))
        .options(selectinload(Bookmark.tags))
    )
    new_bookmark = (await session.execute(select_bookmark_statment)).scalar_one()
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
