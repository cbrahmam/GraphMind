from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.hypothesis_tester import test_connection, test_hypothesis_nl

router = APIRouter(prefix="/api/hypothesis", tags=["Hypothesis Testing"])


class NLHypothesis(BaseModel):
    question: str


@router.get("/test")
async def test_entity_connection(entity_a: str, entity_b: str, via: str | None = None):
    if not entity_a or not entity_b:
        raise HTTPException(status_code=400, detail="entity_a and entity_b are required")
    try:
        return test_connection(entity_a, entity_b, via_entity=via)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/natural")
async def test_nl_hypothesis(req: NLHypothesis):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")
    try:
        return test_hypothesis_nl(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
