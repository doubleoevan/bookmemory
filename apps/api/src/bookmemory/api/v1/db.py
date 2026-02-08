from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory.db.session import get_db

router = APIRouter(prefix="/db", tags=["db"])


@router.get("/ping")
async def db_ping(session: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Checks if the database is up and running."""
    result = await session.execute(text("SELECT 1"))
    value = result.scalar_one()
    return {"db": "ok", "value": value}
