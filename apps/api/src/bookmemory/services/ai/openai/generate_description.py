from __future__ import annotations

from typing import cast, Any

import anyio

from bookmemory.core.settings import settings
from bookmemory.db.models.bookmark import (
    Bookmark,
    PreviewMethod,
)  # or wherever it lives
from bookmemory.services.ai.openai.client import get_openai_client

# description generation is non-streaming and uses already-extracted content.
# these calls are cheaper and shorter-lived. we can allow more concurrency.
_DESCRIPTION_LIMITER = anyio.CapacityLimiter(
    settings.openai_description_max_concurrency
)

# limit the number of characters to pass to the AI provider
MAXIMUM_DESCRIPTION_CONTENT = 8_000
MINIMUM_DESCRIPTION_CONTENT = 300  # any less and we will fall back to web_search

# ai prompts
DESCRIPTION_SYSTEM_PROMPT_CONTENT = (
    "You are helping a user save a bookmark. "
    "Write a clear, neutral description of what this page is about. "
    "Write 3 to 5 sentences. "
    "Use only the provided content. "
    "Be clear and concise. "
    "Plain text only: no markdown, no quotes, no emojis. "
    "Do not provide safety advice or checklists. "
    "Do not include links or URLs. "
    "Do not include citations or parentheses source notes. "
)

DESCRIPTION_SYSTEM_PROMPT_WEB = (
    "You are helping a user save a bookmark. "
    "Write a clear, neutral description of what this page is about. "
    "Write 3 to 5 sentences. "
    "Use web search to read the page and fill in missing context; "
    "use the provided extracted content as a fallback if the page cannot be retrieved. "
    "Be clear and concise. "
    "If the extracted content conflicts with the page, prefer the page. "
    "Plain text only: no markdown, no quotes, no emojis. "
    "Do not provide safety advice or checklists. "
    "Do not include links or URLs. "
    "Do not include citations or parentheses source notes. "
)


def _to_text(response: object) -> str:
    """Returns the text content from an AI response."""
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    chunks: list[str] = []
    for output_block in getattr(response, "output", []) or []:
        for content in getattr(output_block, "content", []) or []:
            if getattr(content, "type", None) == "output_text":
                chunks.append(getattr(content, "text", ""))
    return ("".join(chunks) or "").strip()


async def generate_description(bookmark: Bookmark) -> tuple[str, PreviewMethod]:
    """
    Returns an AI description from the bookmark content.
    Uses web_search if the content is too short.
    """
    # create a user prompt from the bookmark title and content
    title = (bookmark.title or "").strip()
    content = (bookmark.content or "").strip()
    if len(content) > MAXIMUM_DESCRIPTION_CONTENT:
        content = content[:MAXIMUM_DESCRIPTION_CONTENT]
    user_prompt = (
        f"URL: {bookmark.url}\nTitle: {title}\nContent (may be incomplete):\n{content}"
    )

    # use AI to generate a description
    client = get_openai_client()
    async with _DESCRIPTION_LIMITER:
        # try to generate a description from the content
        if len(content) >= MINIMUM_DESCRIPTION_CONTENT:
            description_response = await client.responses.create(
                model=settings.openai_chat_model,
                input=cast(
                    Any,
                    [
                        {
                            "role": "system",
                            "content": DESCRIPTION_SYSTEM_PROMPT_CONTENT,
                        },
                        {"role": "user", "content": user_prompt},
                    ],
                ),
            )
            description = _to_text(description_response)
            return description, PreviewMethod.content

        # generate a description from the web if the content is too short
        description_response = await client.responses.create(
            model=settings.openai_chat_model,
            tools=cast(Any, [{"type": "web_search"}]),
            input=cast(
                Any,
                [
                    {"role": "system", "content": DESCRIPTION_SYSTEM_PROMPT_WEB},
                    {"role": "user", "content": user_prompt},
                ],
            ),
        )
        description = _to_text(description_response)
        return description, PreviewMethod.web
