from __future__ import annotations

import anyio

from openai import AsyncOpenAI

from bookmemory.core.settings import settings

# embedding calls can get rate-limited. keep concurrent requests low.
_EMBED_LIMITER = anyio.CapacityLimiter(settings.openai_embed_max_concurrency)

_openai_client: AsyncOpenAI | None = None


def _get_openai_client() -> AsyncOpenAI:
    """Returns a singleton OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        api_key = (settings.openai_api_key or "").strip()
        if api_key == "":
            raise RuntimeError("OPENAI_API_KEY is not set")
        _openai_client = AsyncOpenAI(api_key=api_key)
    return _openai_client


def _batch_chunks(chunks: list[str], batch_size: int) -> list[list[str]]:
    """Groups chunks together into batches to send to the AI API client with one request."""
    batches: list[list[str]] = []
    batch_start = 0
    while batch_start < len(chunks):
        batches.append(chunks[batch_start : batch_start + batch_size])
        batch_start += batch_size
    return batches


class OpenAIProvider:
    async def embed_chunks(self, chunks: list[str]) -> list[list[float]]:
        # batch chunks together so that multiple embeddings can be made with a single api request
        # but be conservative with the batch size to avoid making the request too slow
        batch_size = max(1, settings.openai_embed_batch_size)

        # embed chunks into vectors
        client = _get_openai_client()
        vectors: list[list[float]] = []
        for batch in _batch_chunks(chunks, batch_size=batch_size):
            api_response = await client.embeddings.create(
                model=settings.openai_embedding_model,
                input=batch,
            )

            # preserve the original order
            api_response.data.sort(key=lambda datum: datum.index)
            for item in api_response.data:
                vectors.append(item.embedding)

        return vectors
