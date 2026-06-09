from fastapi import APIRouter, HTTPException

from backend.database import get_ingestion
from backend.models.schemas import CSVColumnMapping
from backend.routers.ingest import get_processed_doc, get_chunks, get_file_path
from backend.services.schema_manager import get_current_schema
from backend.services.entity_extractor import extract_entities
from backend.services.relationship_extractor import extract_relationships
from backend.services.entity_resolver import resolve_entities
from backend.services.graph_builder import build_graph, import_csv_to_graph
from backend.services.extraction_pipeline import (
    run_extraction,
    process_and_build,
)

router = APIRouter(prefix="/api/extract", tags=["extraction"])

_extraction_cache: dict[str, dict] = {}


@router.post("/resolve")
async def resolve_all_entities():
    all_entities = []
    for doc_id, cached in _extraction_cache.items():
        all_entities.extend(cached["entities"])

    if not all_entities:
        raise HTTPException(status_code=400, detail="No extractions to resolve")

    resolved, merge_log = resolve_entities(all_entities)

    return {
        "total_entities": len(all_entities),
        "resolved_count": len(resolved),
        "merges": len(merge_log),
        "merge_log": merge_log,
        "resolved": [e.model_dump() for e in resolved],
    }


@router.post("/csv/import")
async def csv_import(document_id: str, mapping: CSVColumnMapping):
    doc = get_processed_doc(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.file_type != "csv":
        raise HTTPException(status_code=400, detail="Document is not a CSV")

    csv_path = get_file_path(document_id)
    if not csv_path:
        raise HTTPException(status_code=404, detail="CSV file not found on disk")

    try:
        result = import_csv_to_graph(
            csv_path,
            mapping.model_dump(),
            doc.filename,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV import failed: {e}")

    return {
        "document_id": document_id,
        "graph_result": result.model_dump(),
    }


@router.post("/pipeline/{document_id}")
async def run_full_pipeline(document_id: str):
    record = get_ingestion(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    chunks = get_chunks(document_id)
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks found. Re-upload the document.")

    schema = get_current_schema()
    source = record["filename"]

    try:
        result = process_and_build(chunks, schema, document_id, source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    _extraction_cache[document_id] = {
        "entities": result.all_entities,
        "relationships": result.all_relationships,
    }

    return result.to_dict()


@router.post("/{document_id}")
async def extract_document(document_id: str):
    record = get_ingestion(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    chunks = get_chunks(document_id)
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks found. Re-upload the document.")

    schema = get_current_schema()

    try:
        entities, relationships = run_extraction(chunks, schema, document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")

    _extraction_cache[document_id] = {
        "entities": entities,
        "relationships": relationships,
    }

    return {
        "document_id": document_id,
        "entities_count": len(entities),
        "relationships_count": len(relationships),
        "entities": [e.model_dump() for e in entities],
        "relationships": [r.model_dump() for r in relationships],
    }


@router.post("/{document_id}/build")
async def build_from_extraction(document_id: str):
    cached = _extraction_cache.get(document_id)
    if not cached:
        raise HTTPException(
            status_code=400,
            detail="No extraction results found. Run extraction first.",
        )

    record = get_ingestion(document_id)
    source = record["filename"] if record else document_id

    entities = cached["entities"]
    relationships = cached["relationships"]

    resolved, merge_log = resolve_entities(entities)

    try:
        result = build_graph(resolved, relationships, source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph build failed: {e}")

    return {
        "document_id": document_id,
        "resolved_entities": len(resolved),
        "merges": len(merge_log),
        "merge_log": merge_log,
        "graph_result": result.model_dump(),
    }


@router.get("/{document_id}/entities")
async def get_entities(document_id: str):
    cached = _extraction_cache.get(document_id)
    if not cached:
        raise HTTPException(status_code=404, detail="No extraction results found for this document")
    return [e.model_dump() for e in cached["entities"]]


@router.get("/{document_id}/relationships")
async def get_relationships(document_id: str):
    cached = _extraction_cache.get(document_id)
    if not cached:
        raise HTTPException(status_code=404, detail="No extraction results found for this document")
    return [r.model_dump() for r in cached["relationships"]]
