from fastapi import APIRouter

from bookmemory_api.api.v1 import auth, db, health, users, version

router = APIRouter()
router.include_router(health.router)
router.include_router(version.router)
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(db.router)
