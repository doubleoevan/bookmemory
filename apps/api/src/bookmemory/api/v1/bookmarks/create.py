from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory.services.auth.users import get_current_user
from bookmemory.services.bookmarks.get_bookmark import get_user_bookmark
from bookmemory.core.tags import normalize_tags
from bookmemory.db.models.bookmark import (
    Bookmark,
    BookmarkStatus,
    BookmarkType,
)
from bookmemory.db.models.tag import Tag
from bookmemory.db.session import get_db
from bookmemory.schemas.bookmarks import (
    BookmarkCreateRequest,
    BookmarkResponse,
    to_bookmark_response,
)
from bookmemory.schemas.users import CurrentUser

router = APIRouter()


async def _get_or_create_tags(
    *,
    session: AsyncSession,
    user_id: UUID,
    tag_names: List[str],
) -> List[Tag]:
    # normalize tags
    normalized_tags = normalize_tags(tag_names)
    if not normalized_tags:
        return []

    # find existing tags
    select_tags_statement = select(Tag).where(
        and_(Tag.user_id == user_id, Tag.name.in_(normalized_tags))
    )
    existing_tags = (await session.execute(select_tags_statement)).scalars().all()
    existing_tags_by_name = {tag.name: tag for tag in existing_tags}

    # create new tags and map them to their names
    new_tags: list[Tag] = []
    new_tags_by_name: dict[str, Tag] = {}
    for tag_name in normalized_tags:
        if tag_name in existing_tags_by_name:
            continue
        new_tag = Tag(user_id=user_id, name=tag_name)
        session.add(new_tag)
        new_tags.append(new_tag)
        new_tags_by_name[tag_name] = new_tag
    if new_tags:
        await session.flush()

    # return the tags with existing tags first
    tags: List[Tag] = []
    for tag in normalized_tags:
        if tag in existing_tags_by_name:
            tags.append(existing_tags_by_name[tag])
        else:
            tags.append(new_tags_by_name[tag])
    return tags


@router.post("/", response_model=BookmarkResponse)
async def create_bookmark(
    payload: BookmarkCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> BookmarkResponse:
    # add new tags if necessary
    user_id: UUID = current_user.id
    tags = await _get_or_create_tags(
        session=session,
        user_id=user_id,
        tag_names=payload.tags,
    )

    # require the title
    title = (payload.title or "").strip()
    if title == "":
        raise HTTPException(status_code=422, detail="title is required")

    # require the description
    description = (payload.description or "").strip()
    if description == "":
        raise HTTPException(status_code=422, detail="description is required")

    # require the url for a link bookmark
    bookmark_type = BookmarkType(payload.type)
    if bookmark_type == BookmarkType.link:
        url = (payload.url or "").strip()
        if url == "":
            raise HTTPException(
                status_code=422,
                detail="url is required for link bookmarks",
            )
    else:
        url = None

    # save the bookmark to set an ID
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

    # return the new bookmark from the database
    new_bookmark = await get_user_bookmark(
        bookmark_id=bookmark.id, user_id=user_id, session=session
    )
    return to_bookmark_response(new_bookmark)
