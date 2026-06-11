from fastapi import APIRouter, HTTPException

from backend.services.workspaces import (
    create_workspace,
    list_workspaces,
    get_workspace,
    delete_workspace,
    get_active_workspace,
    set_active_workspace,
)

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])


@router.get("")
async def list_all():
    return list_workspaces()


@router.post("")
async def create(name: str, description: str = ""):
    return create_workspace(name, description)


@router.get("/active")
async def active():
    return {"workspace_id": get_active_workspace()}


@router.post("/active/{workspace_id}")
async def set_active(workspace_id: str):
    if set_active_workspace(workspace_id):
        return {"message": f"Switched to workspace '{workspace_id}'"}
    raise HTTPException(status_code=404, detail="Workspace not found")


@router.delete("/{workspace_id}")
async def remove(workspace_id: str):
    if delete_workspace(workspace_id):
        return {"message": "Deleted"}
    raise HTTPException(status_code=400, detail="Cannot delete (default or not found)")
