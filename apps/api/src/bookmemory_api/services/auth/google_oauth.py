from __future__ import annotations

from authlib.integrations.starlette_client import OAuth

from bookmemory_api.core.settings import settings


def build_oauth() -> OAuth:
    """Builds a Google OAuth client using OIDC discovery"""
    oauth = OAuth()

    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    return oauth
