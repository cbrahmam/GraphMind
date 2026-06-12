from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.shareable_views import (
    create_shared_view,
    get_shared_view,
    list_shared_views,
    delete_shared_view,
    update_shared_view,
)

router = APIRouter(prefix="/api/views", tags=["Shareable Views"])


class CreateViewRequest(BaseModel):
    name: str
    description: str = ""
    query: str
    filters: dict | None = None
    layout: dict | None = None


class UpdateViewRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    query: str | None = None
    filters: dict | None = None
    layout: dict | None = None
    is_public: bool | None = None


@router.get("/")
async def get_views():
    return {"views": list_shared_views()}


@router.post("/")
async def create_view(req: CreateViewRequest):
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    view = create_shared_view(
        name=req.name,
        description=req.description,
        query=req.query,
        filters=req.filters,
        layout=req.layout,
    )
    return view


@router.get("/{view_id}")
async def get_view(view_id: str):
    view = get_shared_view(view_id)
    if not view:
        raise HTTPException(status_code=404, detail="View not found")
    return view


@router.put("/{view_id}")
async def modify_view(view_id: str, req: UpdateViewRequest):
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    view = update_shared_view(view_id, updates)
    if not view:
        raise HTTPException(status_code=404, detail="View not found")
    return view


@router.delete("/{view_id}")
async def remove_view(view_id: str):
    if delete_shared_view(view_id):
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="View not found")
