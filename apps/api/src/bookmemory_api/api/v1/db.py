from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory_api.db.session import get_db_session

router = APIRouter()


@router.get("/api/v1/db/ping")
async def db_ping(session: AsyncSession = Depends(get_db_session)) -> dict:
    result = await session.execute(text("SELECT 1"))
    value = result.scalar_one()
    return {"db": "ok", "value": value}
