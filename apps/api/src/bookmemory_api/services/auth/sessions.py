from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory_api.core.settings import settings
from bookmemory_api.models.session import Session


def _utc_now() -> datetime:
    # always store timestamps in UTC for consistency
    return datetime.now(timezone.utc)


def _expires_at() -> datetime:
    return _utc_now() + timedelta(days=settings.session_ttl_days)


async def create_session(db: AsyncSession, user_id: uuid.UUID) -> Session:
    """Creates and returns a new session row for a logged-in user."""
    session = Session(
        user_id=user_id,
        expires_at=_expires_at(),
        revoked_at=None,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def revoke_session(db: AsyncSession, session_id: uuid.UUID) -> None:
    """Marks a session as revoked when a user logs out, but keeps the row for debugging purposes."""
    await db.execute(
        update(Session).where(Session.id == session_id).values(revoked_at=_utc_now())
    )
    await db.commit()


async def get_valid_session(db: AsyncSession, session_id: uuid.UUID) -> Session | None:
    """Only return a session if it is not revoked or expired."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if session is None:
        return None

    if session.revoked_at is not None:
        return None

    if session.expires_at <= _utc_now():
        return None

    return session
