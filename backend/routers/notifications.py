from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.notification_center import (
    create_notification, get_notifications, mark_read, mark_all_read,
    get_unread_count, delete_notification, clear_all,
)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


class CreateNotification(BaseModel):
    title: str
    message: str
    category: str = "info"
    source: str = ""
    entity: str = ""


@router.get("/")
async def list_notifications(limit: int = 50, unread_only: bool = False, category: str | None = None):
    return {"notifications": get_notifications(limit, unread_only, category)}


@router.get("/unread-count")
async def unread_count():
    return {"count": get_unread_count()}


@router.post("/")
async def add_notification(req: CreateNotification):
    return create_notification(req.title, req.message, req.category, req.source, req.entity)


@router.put("/{notification_id}/read")
async def read_notification(notification_id: str):
    if mark_read(notification_id):
        return {"read": True}
    raise HTTPException(status_code=404, detail="Notification not found")


@router.put("/read-all")
async def read_all():
    count = mark_all_read()
    return {"marked_read": count}


@router.delete("/{notification_id}")
async def remove_notification(notification_id: str):
    if delete_notification(notification_id):
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="Notification not found")


@router.delete("/")
async def clear_notifications():
    count = clear_all()
    return {"cleared": count}
