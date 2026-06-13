from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.whatif_simulator import simulate_remove_entity, simulate_add_relationship

router = APIRouter(prefix="/api/whatif", tags=["What-If Simulation"])


class AddRelSimulation(BaseModel):
    from_entity: str
    to_entity: str
    relationship_type: str


@router.get("/remove/{entity_name}")
async def simulate_remove(entity_name: str):
    try:
        result = simulate_remove_entity(entity_name)
        if not result.get("found"):
            raise HTTPException(status_code=404, detail="Entity not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-relationship")
async def simulate_add(req: AddRelSimulation):
    if not req.from_entity or not req.to_entity or not req.relationship_type:
        raise HTTPException(status_code=400, detail="All fields are required")
    try:
        result = simulate_add_relationship(req.from_entity, req.to_entity, req.relationship_type)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
