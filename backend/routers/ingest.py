import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.config import UPLOAD_DIR, ALLOWED_EXTENSIONS
from backend.database import insert_ingestion, list_ingestions, get_ingestion
from backend.models.schemas import (
    ProcessedDocument,
    IngestURLRequest,
    IngestTextRequest,
    CSVColumnMapping,
)
from backend.services.document_processor import (
    process_document,
    process_text_content,
    process_html_content,
)
from backend.services.text_chunker import chunk_for_extraction

router = APIRouter(prefix="/api/ingest", tags=["ingestion"])

_processed_docs: dict[str, ProcessedDocument] = {}
_doc_chunks: dict[str, list] = {}


@router.post("/document")
async def ingest_document(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {ALLOWED_EXTENSIONS}",
        )

    file_type = ext.lstrip(".")
    file_path = UPLOAD_DIR / f"{uuid.uuid4()}{ext}"
    content = await file.read()
    file_path.write_bytes(content)

    try:
        doc = process_document(str(file_path), file_type)
    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")

    chunks = chunk_for_extraction(doc.text_content, doc.id)
    _processed_docs[doc.id] = doc
    _doc_chunks[doc.id] = chunks

    record = {
        "id": doc.id,
        "filename": file.filename,
        "file_type": file_type,
        "status": "uploaded",
        "total_chunks": len(chunks),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    insert_ingestion(record)

    return {
        "document_id": doc.id,
        "filename": file.filename,
        "file_type": file_type,
        "total_characters": doc.total_characters,
        "total_pages": doc.total_pages,
        "total_chunks": len(chunks),
        "sections": len(doc.sections),
        "status": "uploaded",
    }


@router.post("/url")
async def ingest_url(request: IngestURLRequest):
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(request.url)
            resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

    doc = process_html_content(resp.text, request.url)
    chunks = chunk_for_extraction(doc.text_content, doc.id)
    _processed_docs[doc.id] = doc
    _doc_chunks[doc.id] = chunks

    record = {
        "id": doc.id,
        "filename": doc.filename,
        "file_type": "html",
        "status": "uploaded",
        "total_chunks": len(chunks),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    insert_ingestion(record)

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "file_type": "html",
        "total_characters": doc.total_characters,
        "total_chunks": len(chunks),
        "status": "uploaded",
    }


@router.post("/text")
async def ingest_text(request: IngestTextRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    doc = process_text_content(request.text, request.title)
    chunks = chunk_for_extraction(doc.text_content, doc.id)
    _processed_docs[doc.id] = doc
    _doc_chunks[doc.id] = chunks

    record = {
        "id": doc.id,
        "filename": request.title,
        "file_type": "txt",
        "status": "uploaded",
        "total_chunks": len(chunks),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    insert_ingestion(record)

    return {
        "document_id": doc.id,
        "filename": request.title,
        "file_type": "txt",
        "total_characters": doc.total_characters,
        "total_chunks": len(chunks),
        "status": "uploaded",
    }


@router.post("/csv")
async def ingest_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    file_path = UPLOAD_DIR / f"{uuid.uuid4()}.csv"
    content = await file.read()
    file_path.write_bytes(content)

    try:
        doc = process_document(str(file_path), "csv")
    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {e}")

    _processed_docs[doc.id] = doc

    record = {
        "id": doc.id,
        "filename": file.filename,
        "file_type": "csv",
        "status": "uploaded",
        "total_chunks": 0,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    insert_ingestion(record)

    return {
        "document_id": doc.id,
        "filename": file.filename,
        "file_type": "csv",
        "columns": doc.csv_columns,
        "metadata": doc.metadata,
        "status": "uploaded",
    }


@router.get("/history")
async def get_history():
    return list_ingestions()


@router.get("/document/{document_id}")
async def get_document_info(document_id: str):
    record = get_ingestion(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    result = dict(record)
    if document_id in _processed_docs:
        doc = _processed_docs[document_id]
        result["total_characters"] = doc.total_characters
        result["sections"] = len(doc.sections)
        result["csv_columns"] = doc.csv_columns
    if document_id in _doc_chunks:
        result["chunks"] = len(_doc_chunks[document_id])

    return result


def get_processed_doc(doc_id: str) -> ProcessedDocument | None:
    return _processed_docs.get(doc_id)


def get_chunks(doc_id: str) -> list | None:
    return _doc_chunks.get(doc_id)
