from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from bookmemory.services.auth.users import get_current_user
from bookmemory.services.bookmarks.get_bookmark import get_user_bookmark
from bookmemory.db.session import get_db
from bookmemory.schemas.bookmarks import BookmarkResponse
from bookmemory.schemas.users import CurrentUser

router = APIRouter()


@router.delete("/{bookmark_id}", response_model=BookmarkResponse)
async def delete_bookmark(
    bookmark_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
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

    await session.delete(bookmark)
    await session.commit()
    return None
