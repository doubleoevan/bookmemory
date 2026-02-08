from fastapi import APIRouter

from bookmemory.api.v1 import (
    health,
    version,
    db,
    auth,
    users,
    bookmarks,
    tags,
)

# register all top-level routes
router = APIRouter()
router.include_router(health.router)
router.include_router(version.router)
router.include_router(db.router)
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(bookmarks.router)
router.include_router(tags.router)
