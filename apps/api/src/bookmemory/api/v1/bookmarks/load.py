# apps/api/src/bookmemory/api/v1/bookmarks/load.py
from __future__ import annotations

from uuid import UUID

import anyio
from fastapi import APIRouter, Depends, HTTPException
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory.services.auth.users import get_current_user
from bookmemory.services.bookmarks.get_bookmark import get_user_bookmark
from bookmemory.db.models.bookmark import (
    BookmarkStatus,
    BookmarkType,
    LoadMethod,
)
from bookmemory.db.models.bookmark_chunk import BookmarkChunk
from bookmemory.db.session import get_db
from bookmemory.schemas.bookmarks import (
    BookmarkResponse,
    to_bookmark_response,
)
from bookmemory.schemas.users import CurrentUser
from bookmemory.services.embedding.chunk_embed import embed_chunks
from bookmemory.services.extraction.content_extract import extract_content
from bookmemory.services.extraction.playwright_fetch import PlaywrightFetchError
from bookmemory.services.extraction.http_fetch import FetchError
from bookmemory.services.extraction.text_chunk import chunk_text

MINIMUM_TEXT_LENGTH = (
    60  # set the status to no_content if the text is below this threshold
)
MAXIMUM_FETCH_SECONDS = 35.0

router = APIRouter()


def _is_content_low(content: str) -> bool:
    """Returns True if the content is empty or too short."""
    trimmed_content = (content or "").strip()
    if trimmed_content == "":
        return True
    if len(trimmed_content) < MINIMUM_TEXT_LENGTH:
        return True
    return False


@router.post("/{bookmark_id}/load", response_model=BookmarkResponse)
async def load_bookmark(
    bookmark_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> BookmarkResponse:
    # find the bookmark or throw a 404 if not found
    user_id: UUID = current_user.id
    try:
        bookmark = await get_user_bookmark(
            bookmark_id=bookmark_id,
            user_id=user_id,
            session=session,
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="bookmark not found")

    # require the url for a link or file bookmark
    if bookmark.type in {BookmarkType.link, BookmarkType.file}:
        if bookmark.url is None:
            raise HTTPException(status_code=422, detail="bookmark url is missing")
        if bookmark.url.strip() == "":
            raise HTTPException(status_code=422, detail="bookmark url is missing")

    # delete existing chunks and update the bookmark status and initial load method
    await session.execute(
        sa.delete(BookmarkChunk).where(BookmarkChunk.bookmark_id == bookmark.id)
    )
    bookmark.status = BookmarkStatus.loading
    bookmark.load_method = LoadMethod.http
    await session.commit()

    try:
        # extract content from the url for a bookmark link
        if bookmark.type == BookmarkType.link:
            assert bookmark.url is not None
            with anyio.fail_after(MAXIMUM_FETCH_SECONDS):
                extracted_text, method_used = await extract_content(url=bookmark.url)
        # TODO: extract file content from the s3 url for a bookmark file
        elif bookmark.type == BookmarkType.file:
            assert bookmark.url is not None
            extracted_text = bookmark.description or bookmark.title
            method_used = LoadMethod.read
        # use manually provided content for a bookmark note
        elif bookmark.type == BookmarkType.note:
            extracted_text = bookmark.content or bookmark.description or bookmark.title
            method_used = LoadMethod.manual
        else:
            raise HTTPException(
                status_code=422, detail="unsupported bookmark type for load"
            )

        # set the bookmark content and load method
        content = extracted_text or ""
        bookmark.content = content
        bookmark.load_method = method_used

        # return the bookmark with a status to no_content if the content was empty or too short
        if _is_content_low(content):
            bookmark.status = BookmarkStatus.no_content
            await session.commit()
            await session.refresh(bookmark)
            return to_bookmark_response(bookmark)

        # chunk the content and return the bookmark with status no_content if there are no chunks
        chunks = chunk_text(text=content)
        if len(chunks) == 0:
            bookmark.status = BookmarkStatus.no_content
            await session.commit()
            await session.refresh(bookmark)
            return to_bookmark_response(bookmark)

        # persist new chunks to the database
        for chunk_index, chunk in enumerate(chunks):
            session.add(
                BookmarkChunk(
                    bookmark_id=bookmark.id,
                    chunk_index=chunk_index,
                    text=chunk,
                    embedding=None,
                )
            )

        # update the bookmark status to processing and embed the chunks into vectors
        bookmark.status = BookmarkStatus.processing
        await session.commit()
        vectors = await embed_chunks(chunks)
        if len(vectors) != len(chunks):
            raise RuntimeError("embedding count mismatch")

        # verify that the chunk count matches the vector count
        select_chunks_statement = (
            select(BookmarkChunk)
            .where(BookmarkChunk.bookmark_id == bookmark.id)
            .order_by(BookmarkChunk.chunk_index.asc())
        )
        bookmark_chunks = (
            (await session.execute(select_chunks_statement)).scalars().all()
        )
        if len(bookmark_chunks) != len(vectors):
            raise RuntimeError("vector chunk count mismatch")

        # map each vector to its bookmark chunk embedding and update the bookmark status to ready
        for chunk_index, bookmark_chunk in enumerate(bookmark_chunks):
            bookmark_chunk.embedding = vectors[chunk_index]
        bookmark.status = BookmarkStatus.ready
        await session.commit()

    except TimeoutError as error:
        await session.rollback()
        bookmark.status = BookmarkStatus.failed
        await session.commit()
        raise HTTPException(
            status_code=504,
            detail=f"load timed out after {MAXIMUM_FETCH_SECONDS}s",
        ) from error

    except PlaywrightFetchError as error:
        await session.rollback()
        bookmark.status = BookmarkStatus.failed
        await session.commit()
        raise HTTPException(status_code=502, detail=f"load failed: {error}") from error

    except FetchError as error:
        await session.rollback()
        bookmark.status = BookmarkStatus.failed
        await session.commit()
        raise HTTPException(status_code=502, detail=f"fetch failed: {error}") from error

    except Exception as error:
        await session.rollback()
        bookmark.status = BookmarkStatus.failed
        await session.commit()
        raise HTTPException(status_code=500, detail=f"load failed: {error}") from error

    # return the updated bookmark
    await session.refresh(bookmark)
    return to_bookmark_response(bookmark)
