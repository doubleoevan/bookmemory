from __future__ import annotations

from typing import cast, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_pagination.limit_offset import LimitOffsetParams
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bookmemory.services.auth.users import get_current_user
from bookmemory.services.tags.normalize_tags import normalize_tags
from bookmemory.db.models.bookmark import Bookmark
from bookmemory.schemas.bookmarks import to_bookmark_response, TagMode
from bookmemory.db.models.tag import Tag
from bookmemory.db.session import get_db
from bookmemory.schemas.bookmarks import BookmarkResponse
from bookmemory.schemas.users import CurrentUser

router = APIRouter()


@router.get("/", response_model=LimitOffsetPage[BookmarkResponse])
async def get_bookmarks(
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    tags: list[str] = Query(default_factory=list, alias="tag"),
    tag_mode: TagMode = Query(default="ignore"),
    sort: Literal["alphabetical", "recent"] = Query(default="recent"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> LimitOffsetPage[BookmarkResponse]:
    # filter bookmarks by user
    user_id: UUID = current_user.id
    select_bookmarks_statement = (
        select(Bookmark)
        .where(Bookmark.user_id == user_id)
        .options(selectinload(Bookmark.tags))
    )

    # filter by tags
    normalized_tags = normalize_tags(tags)
    if normalized_tags and tag_mode != "ignore":
        if tag_mode == "all":
            tag_ids_subquery = (
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
                .having(func.count(func.distinct(Tag.name)) == len(normalized_tags))
                .subquery()
            )
        else:
            tag_ids_subquery = (
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
                .subquery()
            )

        # add bookmarks with matching tags to the query
        tagged_bookmark_ids = select(tag_ids_subquery.c.bookmark_id)
        select_bookmarks_statement = select_bookmarks_statement.where(
            Bookmark.id.in_(tagged_bookmark_ids)
        )

    # apply sorting
    if sort == "alphabetical":
        select_bookmarks_statement = select_bookmarks_statement.order_by(
            func.lower(Bookmark.title).asc(),
            Bookmark.created_at.desc(),
            Bookmark.id.desc(),
        )
    else:
        select_bookmarks_statement = select_bookmarks_statement.order_by(
            Bookmark.updated_at.desc(),
            Bookmark.id.desc(),
        )

    # return a paginated list of bookmarks
    return cast(
        LimitOffsetPage[BookmarkResponse],
        await apaginate(
            session,
            select_bookmarks_statement,
            params=LimitOffsetParams(limit=limit, offset=offset),
            transformer=lambda items: [to_bookmark_response(b) for b in items],
        ),
    )
