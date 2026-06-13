from fastapi import APIRouter, HTTPException
from backend.services.causal_chains import find_causal_paths, discover_causal_chains

router = APIRouter(prefix="/api/causal", tags=["Causal Chains"])


@router.get("/path")
async def get_causal_path(from_entity: str, to_entity: str, max_depth: int = 5):
    if not from_entity or not to_entity:
        raise HTTPException(status_code=400, detail="from_entity and to_entity are required")
    try:
        return find_causal_paths(from_entity, to_entity, max_depth=min(max_depth, 8))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discover")
async def discover_chains(limit: int = 10):
    try:
        return {"chains": discover_causal_chains(max_chains=min(limit, 30))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
