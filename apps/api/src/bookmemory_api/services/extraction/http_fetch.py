from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import httpx

USER_AGENT = "BookMemoryBot/0.1 (+https://bookmemory.io)"

SUPPORTED_CONTENT_TYPES = frozenset(
    {"text/html", "application/xhtml+xml", "text/plain"}
)

DEFAULT_FETCH_TIMEOUT_SECONDS = 20.0
DEFAULT_CONNECT_TIMEOUT_SECONDS = 10.0
DEFAULT_MAX_BYTES = 2_000_000  # 2MB


@dataclass(frozen=True)  # fields are immutable
class FetchResult:
    url: str
    content_type: str
    html: str


class FetchError(Exception):
    """Custom error with an optional HTTP status code."""

    def __init__(self, message: str, *, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

    def __str__(self) -> str:
        if self.status_code is None:
            return super().__str__()
        return f"{super().__str__()} (status={self.status_code})"


def _has_html(content: bytes) -> bool:
    # check if content looks like HTML
    head = content[:2048].lstrip().lower()
    return (
        head.startswith(b"<!doctype html")
        or head.startswith(b"<html")
        or b"<head" in head
    )


async def fetch_html(
    *,
    url: str,
    timeout_seconds: float = DEFAULT_FETCH_TIMEOUT_SECONDS,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> FetchResult:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    timeout = httpx.Timeout(timeout_seconds, connect=DEFAULT_CONNECT_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(
        follow_redirects=True,
        headers=headers,
        timeout=timeout,
    ) as client:
        # fetch the url
        try:
            response = await client.get(url)
        except httpx.HTTPError as error:
            raise FetchError(f"request failed: {error}") from error

        # validate the response
        if response.status_code >= 400:
            raise FetchError(
                f"bad status: {response.status_code}",
                status_code=response.status_code,
            )

        # validate the content length
        content = response.content
        if not content:
            raise FetchError("empty response body")

        # validate the content type
        content_type = (
            (response.headers.get("content-type") or "").split(";")[0].strip().lower()
        )
        if content_type and content_type not in SUPPORTED_CONTENT_TYPES:
            if not _has_html(content):
                raise FetchError(f"unsupported content-type: {content_type}")

        if len(content) > max_bytes:
            raise FetchError(
                f"response too large: {len(content)} bytes (max {max_bytes})"
            )

        # validate the decoded body
        html = response.text or ""
        if html.strip() == "":
            raise FetchError("decoded body is empty")

        # return the result
        return FetchResult(
            url=str(response.url),  # the final url after following the redirects
            content_type=content_type or "unknown",
            html=html,
        )
