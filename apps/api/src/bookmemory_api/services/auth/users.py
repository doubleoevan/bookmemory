from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory_api.models.user import User


async def get_or_create_user_from_oauth(
    db: AsyncSession,
    *,
    auth_provider: str,
    auth_subject: str,
    email: str,
    name: str | None,
    picture_url: str | None,
) -> User:
    """Creates or retrieves a user from an OAuth identity."""
    result = await db.execute(
        select(User).where(
            User.auth_provider == auth_provider,
            User.auth_subject == auth_subject,
        )
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            auth_provider=auth_provider,
            auth_subject=auth_subject,
            email=email,
            name=name,
            picture_url=picture_url,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    # keep profile fields up to date on each login
    user.email = email
    user.name = name
    user.picture_url = picture_url
    await db.commit()
    await db.refresh(user)
    return user
