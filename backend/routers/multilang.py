from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.multilang import detect_language, extract_entities_multilang
from backend.services.schema_manager import get_current_schema

router = APIRouter(prefix="/api/multilang", tags=["Multi-Language"])


class DetectRequest(BaseModel):
    text: str


class ExtractRequest(BaseModel):
    text: str
    language: str | None = None


@router.post("/detect")
async def detect_lang(req: DetectRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    try:
        lang = detect_language(req.text)
        return {"language": lang}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract")
async def extract_multilang(req: ExtractRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    try:
        lang = req.language or detect_language(req.text)
        schema = get_current_schema()
        entities = extract_entities_multilang(req.text, lang, schema)
        return {"language": lang, "entities": entities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
