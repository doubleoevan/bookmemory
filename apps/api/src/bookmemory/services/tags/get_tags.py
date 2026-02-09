from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory.services.tags.normalize_tags import normalize_tags
from bookmemory.db.models.tag import Tag

router = APIRouter()


async def get_or_create_tags(
    *,
    session: AsyncSession,
    user_id: UUID,
    tag_names: List[str],
) -> List[Tag]:
    """Returns a user's existing tags and persists new tags as necessary."""
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
