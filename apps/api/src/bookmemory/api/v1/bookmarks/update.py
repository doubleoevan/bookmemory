from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from bookmemory.db.models.bookmark import BookmarkType
from bookmemory.services.auth.users import get_current_user
from bookmemory.services.bookmarks.get_bookmark import get_user_bookmark
from bookmemory.db.session import get_db
from bookmemory.schemas.bookmarks import (
    BookmarkResponse,
    to_bookmark_response,
    BookmarkUpdateRequest,
)
from bookmemory.schemas.users import CurrentUser
from bookmemory.services.tags.get_tags import get_or_create_tags

router = APIRouter()


@router.patch("/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: UUID,
    payload: BookmarkUpdateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> BookmarkResponse:
    try:
        user_id: UUID = current_user.id
        bookmark = await get_user_bookmark(
            bookmark_id=bookmark_id,
            user_id=user_id,
            session=session,
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="bookmark not found")

    update_fields = payload.model_dump(exclude_unset=True)

    # update tags if provided
    if "tags" in update_fields:
        tag_names = update_fields.pop("tags") or []
        tags = await get_or_create_tags(
            session=session,
            user_id=user_id,
            tag_names=tag_names,
        )
        bookmark.tags = tags

    # update title if provided
    if "title" in update_fields:
        title = (update_fields.pop("title") or "").strip()
        if title == "":
            raise HTTPException(status_code=422, detail="title is required")
        bookmark.title = title

    # update description if provided
    if "description" in update_fields:
        description = (update_fields.pop("description") or "").strip()
        if description == "":
            raise HTTPException(status_code=422, detail="description is required")
        bookmark.description = description

    # update url if provided and enforce rules
    if "url" in update_fields:
        url = (update_fields.pop("url") or "").strip()
        if bookmark.type in (BookmarkType.link, BookmarkType.file):
            if url == "":
                bookmark_type = "link" if bookmark.type == BookmarkType.link else "file"
                raise HTTPException(
                    status_code=422,
                    detail=f"url is required for {bookmark_type} bookmarks",
                )
            bookmark.url = url
        else:
            bookmark.url = None

    # save and return the updated bookmark
    session.add(bookmark)
    await session.commit()
    updated_bookmark = await get_user_bookmark(
        bookmark_id=bookmark.id,
        user_id=user_id,
        session=session,
    )
    return to_bookmark_response(updated_bookmark)
