from fastapi import APIRouter, HTTPException

from backend.services.graph_diff import snapshot_graph, compute_diff

router = APIRouter(prefix="/api/graph", tags=["diff"])

_snapshots: dict[str, dict] = {}


@router.post("/snapshot")
async def take_snapshot(name: str = "latest"):
    snapshot = snapshot_graph()
    _snapshots[name] = snapshot
    return {
        "name": name,
        "nodes": len(snapshot["nodes"]),
        "relationships": len(snapshot["relationships"]),
    }


@router.get("/snapshot/{name}")
async def get_snapshot(name: str):
    if name not in _snapshots:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    s = _snapshots[name]
    return {"name": name, "nodes": len(s["nodes"]), "relationships": len(s["relationships"])}


@router.get("/diff/{before_name}/{after_name}")
async def get_diff(before_name: str, after_name: str):
    if before_name not in _snapshots:
        raise HTTPException(status_code=404, detail=f"Snapshot '{before_name}' not found")
    if after_name not in _snapshots:
        raise HTTPException(status_code=404, detail=f"Snapshot '{after_name}' not found")
    return compute_diff(_snapshots[before_name], _snapshots[after_name])
