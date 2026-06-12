from fastapi import APIRouter, HTTPException
from backend.services.schema_evolution import suggest_schema_changes, auto_evolve_schema

router = APIRouter(prefix="/api/schema-evolution", tags=["Schema Evolution"])


@router.get("/suggest")
async def get_suggestions():
    try:
        return suggest_schema_changes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evolve")
async def evolve_schema():
    try:
        return auto_evolve_schema()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
