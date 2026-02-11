from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import anyio
from fastapi import APIRouter, Depends, HTTPException

from bookmemory.core.settings import settings
from bookmemory.db.models.bookmark import (
    Bookmark,
    LoadMethod,
    PreviewMethod,
)
from bookmemory.schemas.bookmarks import BookmarkPreviewRequest, BookmarkPreviewResponse
from bookmemory.schemas.users import CurrentUser
from bookmemory.services.auth.users import get_current_user
from bookmemory.services.ai.providers import get_ai_provider
from bookmemory.services.extraction.content_extract import extract_content
from bookmemory.services.extraction.http_fetch import FetchError
from bookmemory.services.extraction.playwright_fetch import PlaywrightFetchError

router = APIRouter()

MAXIMUM_FETCH_SECONDS = 35.0
MAXIMUM_PREVIEW_CHARS = 1200


@router.post("/preview", response_model=BookmarkPreviewResponse)
async def preview_bookmark(
    payload: BookmarkPreviewRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> BookmarkPreviewResponse:
    # require the url for a link or file bookmark
    url = (payload.url or "").strip()
    if url == "":
        raise HTTPException(status_code=422, detail="url is required")

    # provide defaults in case extraction fails
    content = ""
    title = ""
    load_method = LoadMethod.http
    preview_method = PreviewMethod.content

    # extract the content from a bookmark url
    try:
        with anyio.fail_after(MAXIMUM_FETCH_SECONDS):
            extracted_content = await extract_content(url=url)
            content = (extracted_content.content or "").strip()
            title = (extracted_content.title or "").strip()
            load_method = extracted_content.load_method or load_method
    except TimeoutError as error:
        raise HTTPException(
            status_code=504,
            detail=f"preview timed out after {MAXIMUM_FETCH_SECONDS}s",
        ) from error
    except (FetchError, PlaywrightFetchError):
        pass

    # provide an AI description of the bookmark's content
    provider = get_ai_provider(settings.description_provider)
    try:
        bookmark = Bookmark(
            type=payload.type,
            user_id=current_user.id,
            title=title,
            content=content,
            url=url,
        )
        description, preview_method = await provider.generate_description(
            bookmark=bookmark
        )
        description = (description or "").strip()
    except anyio.get_cancelled_exc_class():
        raise
    except Exception:
        description = None

    # return the bookmark preview with a snippet of content for debugging
    content_preview = content[:MAXIMUM_PREVIEW_CHARS] if content else None
    return BookmarkPreviewResponse(
        id=uuid4(),
        user_id=current_user.id,
        summary=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        status="preview",
        tags=[],
        type=payload.type,
        url=url,
        title=title,
        description=description,
        load_method=load_method,
        preview_method=preview_method,
        content_preview=content_preview,
    )
