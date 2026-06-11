from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.services.annotations import (
    add_annotation,
    get_annotations,
    vote_annotation,
    delete_annotation,
    flag_entity,
    correct_entity,
)

router = APIRouter(prefix="/api/annotations", tags=["annotations"])


@router.get("")
async def list_annotations(entity: Optional[str] = None):
    return get_annotations(entity)


@router.post("")
async def create_annotation(
    entity_name: str,
    text: str,
    annotation_type: str = "note",
    user: str = "anonymous",
):
    return add_annotation(entity_name, text, annotation_type, user)


@router.post("/{annotation_id}/vote")
async def vote(annotation_id: str, direction: int = 1):
    if direction not in (-1, 1):
        raise HTTPException(status_code=400, detail="Direction must be 1 or -1")
    result = vote_annotation(annotation_id, direction)
    if not result:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return result


@router.delete("/{annotation_id}")
async def remove(annotation_id: str):
    if delete_annotation(annotation_id):
        return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Annotation not found")


@router.post("/flag")
async def flag(entity_name: str, reason: str, user: str = "anonymous"):
    return flag_entity(entity_name, reason, user)


@router.post("/correct")
async def correct(
    entity_name: str,
    field: str,
    old_value: str,
    new_value: str,
    user: str = "anonymous",
):
    return correct_entity(entity_name, field, old_value, new_value, user)
