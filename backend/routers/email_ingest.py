from fastapi import APIRouter, HTTPException, UploadFile, File
from backend.services.email_parser import parse_eml, parse_mbox, extract_email_entities
import tempfile
import os

router = APIRouter(prefix="/api/email", tags=["Email Ingestion"])


@router.post("/parse/eml")
async def parse_eml_file(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".eml"):
        raise HTTPException(status_code=400, detail="File must be .eml format")
    try:
        content = await file.read()
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".eml", delete=False) as f:
            f.write(content)
            tmp_path = f.name
        try:
            parsed = parse_eml(tmp_path)
            entities = extract_email_entities(parsed)
            return {"parsed": parsed, "entities": entities}
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse/mbox")
async def parse_mbox_file(file: UploadFile = File(...), max_messages: int = 50):
    try:
        content = await file.read()
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".mbox", delete=False) as f:
            f.write(content)
            tmp_path = f.name
        try:
            messages = parse_mbox(tmp_path, max_messages)
            all_entities = []
            all_relationships = []
            for msg in messages:
                extracted = extract_email_entities(msg)
                all_entities.extend(extracted["entities"])
                all_relationships.extend(extracted["relationships"])
            return {
                "message_count": len(messages),
                "entities": all_entities,
                "relationships": all_relationships,
            }
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
