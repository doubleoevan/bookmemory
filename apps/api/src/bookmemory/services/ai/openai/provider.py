from __future__ import annotations

from typing import AsyncIterator

from bookmemory.db.models.bookmark import (
    Bookmark,
    PreviewMethod,
)  # or wherever it lives

from .embed_chunks import embed_chunks as _embed_chunks
from .generate_description import generate_description as _generate_description
from .stream_summary import stream_summary as _stream_summary


class OpenAIProvider:
    """Implements the AIProvider interface using OpenAI."""

    async def embed_chunks(self, chunks: list[str]) -> list[list[float]]:
        return await _embed_chunks(chunks)

    async def generate_description(
        self, *, bookmark: Bookmark
    ) -> tuple[str, PreviewMethod]:
        return await _generate_description(bookmark)

    def stream_summary(self, *, bookmark: Bookmark) -> AsyncIterator[str]:
        return _stream_summary(bookmark)
