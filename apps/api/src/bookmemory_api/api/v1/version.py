from fastapi import APIRouter

router = APIRouter()

@router.get("/version")
def version() -> dict:
    return {"version": "0.1.0"}
