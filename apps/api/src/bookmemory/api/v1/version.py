from fastapi import APIRouter

router = APIRouter()


@router.get("/version")
def version() -> dict[str, str]:
    """Returns the API version."""
    return {"version": "0.1.0"}
