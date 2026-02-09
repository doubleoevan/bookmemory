from __future__ import annotations

from openai import AsyncOpenAI

from bookmemory.core.settings import settings

_openai_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    """Returns a singleton OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        api_key = (settings.openai_api_key or "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _openai_client = AsyncOpenAI(api_key=api_key)
    return _openai_client
