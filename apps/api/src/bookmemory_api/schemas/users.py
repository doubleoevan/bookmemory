from __future__ import annotations

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: UUID
    email: str
    name: str | None = None
    picture_url: str | None = None
    created_at: datetime
