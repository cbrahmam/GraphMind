from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.api_key_manager import generate_key, list_keys, revoke_key, delete_key, get_key_stats

router = APIRouter(prefix="/api/keys", tags=["API Keys"])


class GenerateKey(BaseModel):
    name: str
    scopes: list[str] = ["read"]
    rate_limit: int = 60
    owner: str = "anonymous"


@router.get("/")
async def get_keys():
    return {"keys": list_keys()}


@router.post("/")
async def create_key(req: GenerateKey):
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    return generate_key(req.name, req.scopes, req.rate_limit, req.owner)


@router.put("/{key_id}/revoke")
async def revoke(key_id: str):
    if revoke_key(key_id):
        return {"revoked": True}
    raise HTTPException(status_code=404, detail="Key not found")


@router.delete("/{key_id}")
async def remove_key(key_id: str):
    if delete_key(key_id):
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="Key not found")


@router.get("/stats")
async def key_stats():
    return get_key_stats()
