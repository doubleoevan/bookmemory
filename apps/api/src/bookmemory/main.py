from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from starlette.middleware.sessions import SessionMiddleware

from bookmemory.api.v1.router import router as v1_router
from bookmemory.core.settings import settings


def create_app() -> FastAPI:
    """Creates the FastAPI application instance."""

    app = FastAPI(title="BookMemory API")

    allowed_origins = [
        origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_middleware_secret,
        same_site=settings.cookie_samesite,
        https_only=settings.cookie_secure,
    )

    app.include_router(v1_router, prefix="/api/v1")
    add_pagination(app)
    return app


app = create_app()
