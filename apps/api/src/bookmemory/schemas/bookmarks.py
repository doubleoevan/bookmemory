from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TypeAlias, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from bookmemory.db.models.bookmark import Bookmark

# shared tag filtering mode for bookmark queries
TagMode: TypeAlias = Literal["any", "all", "ignore"]


def to_bookmark_response(bookmark: Bookmark) -> BookmarkResponse:
    return BookmarkResponse(
        id=bookmark.id,
        user_id=bookmark.user_id,
        title=bookmark.title,
        description=bookmark.description,
        summary=bookmark.summary,
        type=bookmark.type.value,
        url=bookmark.url,
        status=bookmark.status.value,
        load_method=(bookmark.load_method.value if bookmark.load_method else None),
        created_at=bookmark.created_at,
        updated_at=bookmark.updated_at,
        tags=[TagResponse(id=tag.id, name=tag.name) for tag in bookmark.tags],
    )


class BookmarkCreateRequest(BaseModel):
    type: str = Field(default="link", description="bookmark type: link | note | file")
    title: str
    description: str
    url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    # verify that a link bookmark has the url
    @model_validator(mode="after")
    def validate_by_type(self) -> "BookmarkCreateRequest":
        if self.type == "link":
            if not self.url or self.url.strip() == "":
                raise ValueError("url is required when bookmark type is 'link'")
        return self


class TagResponse(BaseModel):
    id: UUID
    name: str


class TagCountResponse(BaseModel):
    name: str
    count: int


class BookmarkResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    summary: Optional[str]
    type: str
    url: Optional[str]
    status: str
    load_method: Optional[str]
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse]


class BookmarkSearchResponse(BaseModel):
    bookmark: BookmarkResponse
    snippet: str
    score: float | None = None  # only for semantic
    chunk_id: UUID | None = (
        None  # optional for debugging: the chunk embedding that matched a semantic query
    )


class BookmarkPreviewRequest(BaseModel):
    type: str = Field(default="link")
    url: str


class BookmarkPreviewResponse(BaseModel):
    type: str
    url: str
    title: str
    description: str | None = None
    load_method: str | None = None
    content_preview: str | None = None  # sample of extracted text for debugging
