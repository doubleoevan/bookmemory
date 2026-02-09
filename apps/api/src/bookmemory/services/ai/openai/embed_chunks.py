from __future__ import annotations

import anyio

from bookmemory.core.settings import settings
from bookmemory.services.ai.openai.client import get_openai_client

# embedding requests are relatively fast but can still hit provider rate limits. limit concurrent requests.
_EMBED_LIMITER = anyio.CapacityLimiter(settings.openai_embed_max_concurrency)


def _batch_chunks(chunks: list[str], batch_size: int) -> list[list[str]]:
    """Groups chunks together into batches to send to the AI API client with one request."""
    batches: list[list[str]] = []
    batch_start = 0
    while batch_start < len(chunks):
        batches.append(chunks[batch_start : batch_start + batch_size])
        batch_start += batch_size
    return batches


async def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Returns a list of embedding vectors for the text chunks."""
    # batch chunks together so that multiple embeddings can be made with a single api request
    # but be conservative with the batch size to avoid making the request too slow
    batch_size = max(1, settings.openai_embed_batch_size)

    # embed chunks into vectors
    client = get_openai_client()
    vectors: list[list[float]] = []
    async with _EMBED_LIMITER:
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
