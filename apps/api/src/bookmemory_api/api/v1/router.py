from fastapi import APIRouter

from bookmemory_api.api.v1.health import router as health_router
from bookmemory_api.api.v1.version import router as version_router
from bookmemory_api.api.v1.db import router as db_router

router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(version_router, tags=["version"])
router.include_router(db_router, tags=["db"])
