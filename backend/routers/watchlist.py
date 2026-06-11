from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.services.watchlist import (
    add_watch,
    list_watches,
    remove_watch,
    get_alerts,
    mark_alert_read,
)

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("")
async def list_all():
    return list_watches()


@router.post("")
async def create(entity_pattern: str, label: Optional[str] = None, notify: str = "log"):
    return add_watch(entity_pattern, label, notify)


@router.delete("/{watch_id}")
async def delete_one(watch_id: str):
    if remove_watch(watch_id):
        return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Watch not found")


@router.get("/alerts")
async def alerts(unread_only: bool = False):
    return get_alerts(unread_only)


@router.post("/alerts/{alert_id}/read")
async def mark_read(alert_id: str):
    if mark_alert_read(alert_id):
        return {"message": "Marked as read"}
    raise HTTPException(status_code=404, detail="Alert not found")
