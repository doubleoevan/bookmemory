from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bookmemory.db.engine import engine


async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yields a database AsyncSession for each request."""
    async with async_session_factory() as session:
        yield session
