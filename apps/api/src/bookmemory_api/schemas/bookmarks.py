from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class BookmarkCreateRequest(BaseModel):
    type: str = Field(default="link", description="bookmark type: link | note | file")
    title: str
    url: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_by_type(self) -> "BookmarkCreateRequest":
        if self.type == "link":
            if not self.url or self.url.strip() == "":
                raise ValueError("url is required when bookmark type is 'link'")
        return self


class TagResponse(BaseModel):
    id: UUID
    name: str


class BookmarkResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    type: str
    url: Optional[str]
    status: str
    ingest_method: Optional[str]
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse]
