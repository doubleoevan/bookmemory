from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from bookmemory.services.auth.users import get_current_user
from bookmemory.services.bookmarks.get_bookmark import get_user_bookmark
from bookmemory.db.session import get_db
from bookmemory.schemas.bookmarks import BookmarkResponse, to_bookmark_response
from bookmemory.schemas.users import CurrentUser

router = APIRouter()


@router.get("/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark(
    bookmark_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> BookmarkResponse:
    # find and return the bookmark or throw a 404 if not found
    try:
        user_id: UUID = current_user.id
        bookmark = await get_user_bookmark(
            bookmark_id=bookmark_id,
            user_id=user_id,
            session=session,
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="bookmark not found")

    return to_bookmark_response(bookmark)
