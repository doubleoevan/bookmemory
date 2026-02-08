from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bookmemory.db.models import Bookmark


async def get_user_bookmark(
    *,
    bookmark_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> Bookmark:
    """Returns a user's bookmark for an ID"""
    select_bookmark_statement = (
        select(Bookmark)
        .where(and_(Bookmark.id == bookmark_id, Bookmark.user_id == user_id))
        .options(selectinload(Bookmark.tags))
    )
    bookmark_result = await session.execute(select_bookmark_statement)
    return bookmark_result.scalar_one()
