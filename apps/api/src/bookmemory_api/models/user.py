from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from bookmemory_api.db.base import Base


class User(Base):
    """Holds a user authenticated by an external OAuth provider."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    auth_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    auth_subject: Mapped[str] = mapped_column(String(255), nullable=False)

    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    picture_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("auth_provider", "auth_subject"),
    )

    def _to_user_dict(self) -> dict:
        """Returns data shared by all users."""
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "picture_url": self.picture_url,
            "created_at": self.created_at,
        }

    def to_current_user_dict(self) -> dict:
        """Returns current user data."""
        return self._to_user_dict()

    def to_admin_user_dict(self) -> dict:
        """Returns admin user data."""
        return {
            **self._to_user_dict(),
            # TODO: add admin-only fields
        }
