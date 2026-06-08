from fastapi import APIRouter, HTTPException

from backend.services.schema_manager import (
    get_current_schema,
    save_schema,
    get_presets,
    load_preset,
)

router = APIRouter(prefix="/api/schema", tags=["schema"])


@router.get("")
async def get_schema():
    return get_current_schema()


@router.put("")
async def update_schema(schema: dict):
    if "entity_types" not in schema or "relationship_types" not in schema:
        raise HTTPException(
            status_code=400,
            detail="Schema must include 'entity_types' and 'relationship_types'",
        )
    save_schema(schema)
    return {"message": "Schema updated", "schema": schema}


@router.get("/presets")
async def list_presets():
    return get_presets()


@router.post("/presets/{name}")
async def apply_preset(name: str):
    try:
        schema = load_preset(name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f"Loaded preset '{name}'", "schema": schema}
