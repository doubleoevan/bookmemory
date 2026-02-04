from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: str
    email: str
    name: str | None = None
    picture_url: str | None = None
    created_at: datetime
