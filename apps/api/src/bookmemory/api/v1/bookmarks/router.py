from fastapi import APIRouter

from . import preview, create, detail, list, load, related, search, summary

# register all bookmark subroutes
router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])
router.include_router(preview.router)
router.include_router(create.router)
router.include_router(detail.router)
router.include_router(list.router)
router.include_router(load.router)
router.include_router(related.router)
router.include_router(search.router)
router.include_router(summary.router)
