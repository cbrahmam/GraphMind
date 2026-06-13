from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.fact_verifier import verify_entity, verify_relationship

router = APIRouter(prefix="/api/verify", tags=["Fact Verification"])


class VerifyRelRequest(BaseModel):
    from_entity: str
    relationship_type: str
    to_entity: str


@router.get("/entity/{entity_name}")
async def verify_ent(entity_name: str):
    try:
        return verify_entity(entity_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/relationship")
async def verify_rel(req: VerifyRelRequest):
    try:
        return verify_relationship(req.from_entity, req.relationship_type, req.to_entity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
