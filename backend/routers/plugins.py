from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.plugin_system import (
    create_plugin, list_plugins, get_plugin, delete_plugin,
    toggle_plugin, run_plugin, run_all_plugins,
)

router = APIRouter(prefix="/api/plugins", tags=["Plugins"])


class CreatePlugin(BaseModel):
    name: str
    description: str = ""
    rules: list[dict] = []
    entity_label: str = "Entity"


class RunPluginRequest(BaseModel):
    text: str


@router.get("/")
async def get_plugins():
    return {"plugins": list_plugins()}


@router.post("/")
async def add_plugin(req: CreatePlugin):
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    return create_plugin(req.name, req.description, req.rules, req.entity_label)


@router.get("/{plugin_id}")
async def get_one(plugin_id: str):
    plugin = get_plugin(plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin


@router.delete("/{plugin_id}")
async def remove_plugin(plugin_id: str):
    if delete_plugin(plugin_id):
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="Plugin not found")


@router.put("/{plugin_id}/toggle")
async def toggle(plugin_id: str):
    result = toggle_plugin(plugin_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Plugin not found")


@router.post("/{plugin_id}/run")
async def run_one(plugin_id: str, req: RunPluginRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    result = run_plugin(plugin_id, req.text)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/run-all")
async def run_all(req: RunPluginRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    return run_all_plugins(req.text)
