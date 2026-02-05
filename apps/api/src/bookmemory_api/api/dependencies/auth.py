from __future__ import annotations

import uuid

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory_api.core.settings import settings
from bookmemory_api.db.session import get_db
from bookmemory_api.db.models.user import User
from bookmemory_api.services.auth.sessions import get_valid_session

_UNAUTHENTICATED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    session_cookie: str | None = Cookie(
        default=None, alias=settings.session_cookie_name
    ),
) -> User:
    """Returns the logged-in user from the HttpOnly session cookie."""
    if not session_cookie:
        raise _UNAUTHENTICATED

    try:
        session_id = uuid.UUID(session_cookie)
    except ValueError:
        raise _UNAUTHENTICATED

    session = await get_valid_session(db, session_id)
    if session is None:
        raise _UNAUTHENTICATED

    result = await db.execute(select(User).where(User.id == session.user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise _UNAUTHENTICATED

    return user
