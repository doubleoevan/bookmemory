from __future__ import annotations

from datetime import timedelta

from fastapi import Response

from bookmemory.core.settings import settings


def set_session_cookie(response: Response, session_id: str) -> None:
    """Sets the HttpOnly cookie that stores the session id."""
    max_age = int(timedelta(days=settings.session_ttl_days).total_seconds())

    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain or None,
        max_age=max_age,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    """Clears the session cookie."""
    response.delete_cookie(
        key=settings.session_cookie_name,
        domain=settings.cookie_domain or None,
        path="/",
    )
