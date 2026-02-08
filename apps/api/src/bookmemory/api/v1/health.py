from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Checks if the API is up and running."""
    return {"status": "ok"}
