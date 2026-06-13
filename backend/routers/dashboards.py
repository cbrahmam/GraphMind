from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.custom_dashboard import (
    create_dashboard, list_dashboards, get_dashboard, update_dashboard,
    delete_dashboard, add_widget, remove_widget, get_available_widgets,
)

router = APIRouter(prefix="/api/dashboards", tags=["Custom Dashboards"])


class CreateDashboard(BaseModel):
    name: str
    description: str = ""
    widgets: list[dict] | None = None


class UpdateDashboard(BaseModel):
    name: str | None = None
    description: str | None = None
    widgets: list[dict] | None = None
    layout: str | None = None


class AddWidget(BaseModel):
    type: str = "graph_stats"
    title: str = ""
    config: dict = {}
    position: dict = {}


@router.get("/widgets/available")
async def available_widgets():
    return {"widgets": get_available_widgets()}


@router.get("/")
async def get_all():
    return {"dashboards": list_dashboards()}


@router.post("/")
async def create(req: CreateDashboard):
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    return create_dashboard(req.name, req.description, req.widgets)


@router.get("/{dashboard_id}")
async def get_one(dashboard_id: str):
    d = get_dashboard(dashboard_id)
    if not d:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return d


@router.put("/{dashboard_id}")
async def update(dashboard_id: str, req: UpdateDashboard):
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    d = update_dashboard(dashboard_id, updates)
    if not d:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return d


@router.delete("/{dashboard_id}")
async def remove(dashboard_id: str):
    if delete_dashboard(dashboard_id):
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="Dashboard not found")


@router.post("/{dashboard_id}/widgets")
async def add_w(dashboard_id: str, req: AddWidget):
    w = add_widget(dashboard_id, req.model_dump())
    if not w:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return w


@router.delete("/{dashboard_id}/widgets/{widget_id}")
async def remove_w(dashboard_id: str, widget_id: str):
    if remove_widget(dashboard_id, widget_id):
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="Widget not found")
