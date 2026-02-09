from __future__ import annotations

from typing import AsyncIterator, Any, cast

import anyio

from bookmemory.core.settings import settings
from bookmemory.db.models.bookmark import Bookmark  # or wherever it lives
from bookmemory.services.ai.openai.client import get_openai_client

# summary generation is streamed and invokes web search.
# these requests are long-lived, user-facing, and expensive. keep concurrent requests low.
_SUMMARY_LIMITER = anyio.CapacityLimiter(settings.openai_summary_max_concurrency)

# limit the number of characters to pass to the AI provider
MAXIMUM_SUMMARY_CONTENT = 60_000

# ai prompt
SUMMARY_SYSTEM_PROMPT = (
    "You summarize webpages for a personal bookmark library. "
    "Write a 3–5 sentence summary of what the page is about. "
    "Use web search to read the page and fill in missing context; "
    "use the provided extracted content as a fallback if the page cannot be retrieved. "
    "If the extracted content conflicts with the page, prefer the page. "
    "Plain text only (no markdown, no quotes, no emojis). "
    "Do not provide safety advice or checklists."
    "Do not include links or URLs. "
    "Do not include citations or parentheses source notes."
)


async def stream_summary(bookmark: Bookmark) -> AsyncIterator[str]:
    """
    Streams a summary of the bookmark using web search.
    Uses bookmark content if the web search fails.
    """
    # create a user prompt from the bookmark title and content
    title = (bookmark.title or "").strip()
    content = (bookmark.content or "").strip()
    if len(content) > MAXIMUM_SUMMARY_CONTENT:
        content = content[:MAXIMUM_SUMMARY_CONTENT]
    user_prompt = (
        f"URL: {bookmark.url}\n"
        f"Title: {title}\n"
        f"Extracted content (may be partial):\n{content}"
    )

    # use AI to generate a summary
    client = get_openai_client()
    async with _SUMMARY_LIMITER:
        # try to generate a summary from the web
        try:
            async with client.responses.stream(
                model=settings.openai_chat_model,
                tools=cast(Any, [{"type": "web_search"}]),
                input=cast(
                    Any,
                    [
                        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                ),
            ) as stream:
                async for event in stream:
                    if event.type == "response.output_text.delta" and event.delta:
                        yield event.delta
            return
        except anyio.get_cancelled_exc_class():
            raise
        except Exception:
            # generate a summary from the content if the web search failed
            async with client.responses.stream(
                model=settings.openai_chat_model,
                input=cast(
                    Any,
                    [
                        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                ),
            ) as stream:
                async for event in stream:
                    if event.type == "response.output_text.delta" and event.delta:
                        yield event.delta
