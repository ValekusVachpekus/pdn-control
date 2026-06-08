from fastapi import APIRouter

from .. import __version__

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "version": __version__}
