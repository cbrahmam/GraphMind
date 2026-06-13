from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.webhook_manager import (
    register_webhook, list_webhooks, delete_webhook, toggle_webhook, test_webhook,
)

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


class RegisterWebhook(BaseModel):
    url: str
    events: list[str] = ["*"]
    name: str = ""
    secret: str = ""


@router.get("/")
async def get_webhooks():
    return {"webhooks": list_webhooks()}


@router.post("/")
async def create_webhook(req: RegisterWebhook):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")
    return register_webhook(req.url, req.events, req.name, req.secret)


@router.delete("/{webhook_id}")
async def remove_webhook(webhook_id: str):
    if delete_webhook(webhook_id):
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="Webhook not found")


@router.put("/{webhook_id}/toggle")
async def toggle(webhook_id: str):
    result = toggle_webhook(webhook_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Webhook not found")


@router.post("/{webhook_id}/test")
async def test(webhook_id: str):
    return test_webhook(webhook_id)
