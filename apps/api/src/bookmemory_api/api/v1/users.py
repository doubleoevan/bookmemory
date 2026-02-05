from __future__ import annotations

from fastapi import APIRouter, Depends

from bookmemory_api.api.dependencies.auth import get_current_user
from bookmemory_api.db.models.user import User
from bookmemory_api.schemas.users import CurrentUser

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=CurrentUser)
async def me(
    user: User = Depends(get_current_user),
) -> CurrentUser:
    """Returns the logged-in user's profile."""
    return CurrentUser(
        id=user.id,
        email=user.email,
        name=user.name,
        picture_url=user.picture_url,
        created_at=user.created_at,
    )
