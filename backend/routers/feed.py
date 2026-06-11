from fastapi import APIRouter, Query
from typing import Optional

from backend.services.change_feed import get_feed, get_timeline

router = APIRouter(prefix="/api/feed", tags=["feed"])


@router.get("")
async def list_feed(
    limit: int = Query(default=100, le=500),
    change_type: Optional[str] = None,
):
    return get_feed(limit, change_type)


@router.get("/timeline")
async def timeline():
    return get_timeline()
