from __future__ import annotations

from typing import List

from bookmemory.services.ai.providers import get_ai_provider, AIProviderType


async def embed_chunks(chunks: List[str]) -> List[list[float]]:
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

    # return embedding vectors for each chunk
    provider = get_ai_provider(provider_type=AIProviderType.openai)
    return await provider.embed_chunks(normalized_chunks)
