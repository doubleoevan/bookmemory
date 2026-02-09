from __future__ import annotations

from enum import Enum
from typing import Protocol


class AIProviderType(str, Enum):
    openai = "openai"


class AIProvider(Protocol):
    async def embed_chunks(self, chunks: list[str]) -> list[list[float]]: ...


_providers: dict[AIProviderType, AIProvider] = {}


def get_ai_provider(provider_type: AIProviderType) -> AIProvider:
    """Returns a cached singleton instance of the specified AI provider."""
    # return a cached provider instance if one exists
    if provider_type in _providers:
        return _providers[provider_type]

    # update the cache and return a new provider instance
    if provider_type == AIProviderType.openai:
        from bookmemory.services.ai.openai import OpenAIProvider

        provider = OpenAIProvider()
        _providers[provider_type] = provider
        return provider
