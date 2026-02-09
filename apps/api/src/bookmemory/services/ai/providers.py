from __future__ import annotations

from typing import Protocol, AsyncIterator, Literal

from bookmemory.db.models.bookmark import Bookmark, PreviewMethod

AIProviderType = Literal["openai"]


class AIProvider(Protocol):
    async def embed_chunks(self, chunks: list[str]) -> list[list[float]]: ...
    async def generate_description(
        self, *, bookmark: Bookmark
    ) -> tuple[str, PreviewMethod]: ...
    def stream_summary(self, *, bookmark: Bookmark) -> AsyncIterator[str]: ...


_providers: dict[AIProviderType, AIProvider] = {}


def get_ai_provider(provider_type: AIProviderType) -> AIProvider:
    """Returns a cached singleton instance of the specified AI provider."""
    # return a cached provider instance if one exists
    if provider_type in _providers:
        return _providers[provider_type]

    # update the cache and return a new provider instance
    if provider_type == "openai":
        from bookmemory.services.ai.openai.provider import OpenAIProvider

        provider = OpenAIProvider()
        _providers[provider_type] = provider
        return provider

    raise ValueError(f"Unsupported AI provider: {provider_type}")
