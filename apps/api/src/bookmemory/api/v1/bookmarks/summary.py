from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bookmemory.core.settings import settings
from bookmemory.db.session import get_db
from bookmemory.schemas.users import CurrentUser
from bookmemory.services.ai.providers import get_ai_provider
from bookmemory.services.auth.users import get_current_user
from bookmemory.services.bookmarks.get_bookmark import get_user_bookmark

router = APIRouter()


@router.post("/{bookmark_id}/summary")
async def stream_bookmark_summary(
    bookmark_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> StreamingResponse:
    # find the bookmark or throw a 404
    try:
        user_id: UUID = current_user.id
        bookmark = await get_user_bookmark(
            bookmark_id=bookmark_id,
            user_id=user_id,
            session=session,
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="bookmark not found")

    # stream the summary to the client
    async def streamer() -> AsyncIterator[str]:
        try:
            chunks: list[str] = []  # store the chunks to save to the bookmark summary
            provider = get_ai_provider(settings.summary_provider)
            async for chunk in provider.stream_summary(bookmark=bookmark):
                chunks.append(chunk)
                yield json.dumps({"chunk": chunk}) + "\n"  # stream each chunk

            # save the summary to the bookmark
            summary = "".join(chunks).strip()
            bookmark.summary = summary
            await session.commit()

            # stream the done message
            yield json.dumps({"done": "true"}) + "\n"

        except asyncio.CancelledError:
            # there's no way to show an error message if the connection is closed
            await session.rollback()
            raise

        except Exception as error:
            await session.rollback()

            # show an error message for debugging
            error_type = type(error).__name__
            error_message = str(error).strip() or "(no message)"
            yield (
                json.dumps(
                    {
                        "error": {
                            "error": error_type,
                            "message": error_message,
                        },
                    }
                )
                + "\n"
            )
            return

    return StreamingResponse(
        streamer(), media_type="application/x-ndjson; charset=utf-8"
    )
