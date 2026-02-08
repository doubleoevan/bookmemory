from __future__ import annotations

import uuid

from fastapi import Depends, Cookie, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory.core.settings import settings

from bookmemory.db.models.user import User
from bookmemory.db.session import get_db
from bookmemory.services.auth.sessions import get_valid_session

_UNAUTHENTICATED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
)


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

    # try to find an existing user
    user_result = await db.execute(
        select(User).where(
            User.auth_provider == auth_provider,
            User.auth_subject == auth_subject,
        )
    )
    user = user_result.scalar_one_or_none()

    # create a new user if necessary
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

    # keep profile fields up to date for each login
    user.email = email
    user.name = name
    user.picture_url = picture_url
    await db.commit()
    await db.refresh(user)
    return user


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    session_cookie: str | None = Cookie(
        default=None, alias=settings.session_cookie_name
    ),
) -> User:
    """Returns the logged-in user from the HttpOnly session cookie."""

    # verify the session cookie
    if not session_cookie:
        raise _UNAUTHENTICATED

    # get the session id from the cookie
    try:
        session_id = uuid.UUID(session_cookie)
    except ValueError:
        raise _UNAUTHENTICATED

    # find the session from the database
    session = await get_valid_session(db, session_id)
    if session is None:
        raise _UNAUTHENTICATED

    # return the user for the session user ID
    user_result = await db.execute(select(User).where(User.id == session.user_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise _UNAUTHENTICATED

    return user
