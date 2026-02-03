from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bookmemory_api.api.v1.router import router as v1_router
from bookmemory_api.core.settings import settings


def create_app() -> FastAPI:
    """Create the FastAPI application instance."""

    app = FastAPI(title="BookMemory API")

    allowed_origins = [
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(v1_router)
    return app


app = create_app()
