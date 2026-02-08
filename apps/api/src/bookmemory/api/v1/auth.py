from __future__ import annotations

from typing import cast

import uuid
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.starlette_client import OAuth

from bookmemory.core.cookies import clear_session_cookie, set_session_cookie
from bookmemory.core.settings import settings
from bookmemory.db.session import get_db
from bookmemory.services.auth.google_oauth import build_oauth
from bookmemory.services.auth.sessions import create_session, revoke_session
from bookmemory.services.auth.users import get_or_create_user_from_oauth

router = APIRouter(prefix="/auth", tags=["auth"])


def _is_google_oauth_configured() -> bool:
    return bool(
        settings.google_client_id
        and settings.google_client_secret
        and settings.google_redirect_uri
    )


@lru_cache(maxsize=1)
def _get_oauth() -> OAuth:
    # built lazily and cached
    return build_oauth()


@router.get("/google/start")
async def google_start(request: Request) -> Response:
    """Redirects user to Google for login."""
    if not _is_google_oauth_configured():
        raise HTTPException(status_code=501, detail="Google OAuth is not configured")

    oauth = _get_oauth()
    response = await oauth.google.authorize_redirect(
        request, settings.google_redirect_uri
    )
    return cast(Response, response)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Logs the user in with Google and starts a session."""
    if not _is_google_oauth_configured():
        raise HTTPException(status_code=501, detail="Google OAuth is not configured")

    # some providers require a separate call to get user info
    # Google often includes it, but just in case...
    oauth = _get_oauth()
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")
    if userinfo is None:
        userinfo = await oauth.google.userinfo(token=token)

    # check for a valid profile
    auth_subject = userinfo.get("sub")
    email = userinfo.get("email")
    if not auth_subject or not email:
        return RedirectResponse(
            url=f"{settings.web_base_url}/login?error=missing_profile"
        )

    # retrieve or add the user to the database
    user = await get_or_create_user_from_oauth(
        db,
        auth_provider="google",
        auth_subject=auth_subject,
        email=email,
        name=userinfo.get("name"),
        picture_url=userinfo.get("picture"),
    )

    # create a new session, set the cookie and redirect to the home page
    session = await create_session(db, user.id)
    response = RedirectResponse(url=f"{settings.web_base_url}/")
    set_session_cookie(response, str(session.id))
    return response


@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Revokes the session in the DB and clears the session cookie."""
    cookie_value = request.cookies.get(settings.session_cookie_name)
    if cookie_value:
        try:
            session_id = uuid.UUID(cookie_value)
            await revoke_session(db, session_id)
        except ValueError:
            # cookie existed but wasn't a UUID; ignore
            pass

    response = Response(status_code=204)
    clear_session_cookie(response)
    return response
