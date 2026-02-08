from __future__ import annotations

from typing import List

import anyio
from openai import AsyncOpenAI

from bookmemory.core.settings import settings


_client: AsyncOpenAI | None = None

# embedding calls can get rate-limited. keep concurrent requests low.
_EMBED_SEMAPHORE = anyio.Semaphore(settings.embed_max_concurrency)


def _get_api_client() -> AsyncOpenAI:
    """Returns an OpenAI API client instance."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


def _batch_chunks(chunks: list[str], batch_size: int) -> list[list[str]]:
    """Groups chunks together into batches to send to the OpenAI API."""
    batches: list[list[str]] = []
    batch_start = 0
    while batch_start < len(chunks):
        batches.append(chunks[batch_start : batch_start + batch_size])
        batch_start += batch_size
    return batches


async def embed_chunks(chunks: List[str]) -> List[list[float]]:
    # require the OPENAI_API_KEY to be set
    if settings.openai_api_key.strip() == "":
        raise RuntimeError("OPENAI_API_KEY is not set")

    # normalize chunks but keep the original order
    normalized_chunks: list[str] = []
    for chunk in chunks:
        if chunk is None:
            normalized_chunks.append("")
        else:
            normalized_chunks.append(str(chunk))

    # return an empty list if there are no chunks to embed
    if len(normalized_chunks) == 0:
        return []

    # batch chunks together so that multiple embeddings can be made with a single api request
    # but be conservative with the batch size to avoid making the request too slow
    batch_size = max(1, settings.embed_batch_size)

    # embed chunks into vectors
    client = _get_api_client()
    vectors: list[list[float]] = []
    async with _EMBED_SEMAPHORE:  # use a semaphore to limit concurrent requests
        for batch in _batch_chunks(normalized_chunks, batch_size=batch_size):
            api_response = await client.embeddings.create(
                model=settings.openai_embedding_model,
                input=batch,
            )
            # preserve the original order
            api_response.data.sort(key=lambda datum: datum.index)
            for item in api_response.data:
                vectors.append(item.embedding)

    return vectors
