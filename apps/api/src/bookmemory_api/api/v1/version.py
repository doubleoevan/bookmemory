from fastapi import APIRouter

router = APIRouter()

@router.get("/api/v1/version")
def version() -> dict:
    return {"version": "0.1.0"}
