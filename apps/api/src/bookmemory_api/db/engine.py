from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from bookmemory_api.core.settings import settings


def create_engine() -> AsyncEngine:
    """Creates the global async SQLAlchemy engine."""
    return create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
    )


engine = create_engine()
