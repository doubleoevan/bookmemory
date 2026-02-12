from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory.services.auth.users import get_current_user
from bookmemory.services.bookmarks.get_bookmark import get_user_bookmark
from bookmemory.db.models.bookmark import (
    Bookmark,
    BookmarkStatus,
    BookmarkType,
)
from bookmemory.db.session import get_db
from bookmemory.schemas.bookmarks import (
    BookmarkCreateRequest,
    BookmarkResponse,
    to_bookmark_response,
)
from bookmemory.schemas.users import CurrentUser
from bookmemory.services.tags.get_tags import get_or_create_tags

router = APIRouter()


@router.post("/", response_model=BookmarkResponse)
async def create_bookmark(
    payload: BookmarkCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> BookmarkResponse:
    # add new tags if necessary
    user_id: UUID = current_user.id
    tags = await get_or_create_tags(
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

    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()

        # return a message to display if the url already exists
        error_message = str(getattr(error, "orig", error))
        if "ix_bookmarks_user_id_url_unique_not_null" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="URL already exists"
            )
        raise

    # return the new bookmark from the database
    new_bookmark = await get_user_bookmark(
        bookmark_id=bookmark.id, user_id=user_id, session=session
    )
    return to_bookmark_response(new_bookmark)
