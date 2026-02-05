from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory_api.api.dependencies.auth import get_current_user
from bookmemory_api.db.models.bookmark import Bookmark
from bookmemory_api.db.models.tag import Tag
from bookmemory_api.db.session import get_db
from bookmemory_api.schemas.bookmarks import TagCountResponse
from bookmemory_api.schemas.users import CurrentUser


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagCountResponse])
async def get_tags(
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[TagCountResponse]:
    user_id: UUID = current_user.id

    # select tags with their bookmarks count
    select_tag_counts_statement = (
        select(
            Tag.name.label("name"),
            func.count(func.distinct(Bookmark.id)).label("count"),
        )
        .select_from(Tag)
        .outerjoin(Tag.bookmarks)
        .where(Tag.user_id == user_id)
        .where((Bookmark.user_id == user_id) | (Bookmark.id.is_(None)))
        .group_by(Tag.name)
        .order_by(func.lower(Tag.name).asc())
    )

    tag_counts = (await session.execute(select_tag_counts_statement)).mappings().all()
    return [
        TagCountResponse(name=tag_count.name, count=int(tag_count.count))
        for tag_count in tag_counts
    ]
