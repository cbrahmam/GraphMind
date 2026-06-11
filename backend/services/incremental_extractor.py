import json
from backend.config import GRAPH_DATA_DIR
from backend.neo4j_client import neo4j_client
from backend.services.schema_manager import get_current_schema
from backend.services.entity_extractor import extract_entities
from backend.services.relationship_extractor import extract_relationships
from backend.services.entity_resolver import resolve_entities
from backend.services.graph_builder import build_graph
from backend.database import list_ingestions, get_ingestion, update_ingestion

SCHEMA_HASH_FILE = GRAPH_DATA_DIR / "schema_hash.json"


def _schema_hash(schema: dict) -> str:
    return json.dumps(sorted(schema.items()) if isinstance(schema, dict) else schema, sort_keys=True)


def _get_stored_hash() -> str | None:
    if SCHEMA_HASH_FILE.exists():
        data = json.loads(SCHEMA_HASH_FILE.read_text())
        return data.get("hash")
    return None


def _store_hash(h: str):
    SCHEMA_HASH_FILE.write_text(json.dumps({"hash": h}))


def schema_changed() -> bool:
    current = _schema_hash(get_current_schema())
    stored = _get_stored_hash()
    return stored is not None and current != stored


def get_affected_documents() -> list[dict]:
    if not schema_changed():
        return []
    ingestions = list_ingestions(limit=200)
    return [i for i in ingestions if i.get("status") in ("extracted", "built")]


def re_extract_document(document_id: str, chunks: list) -> dict:
    schema = get_current_schema()

    all_entities = []
    all_relationships = []

    for chunk in chunks:
        try:
            entities = extract_entities(chunk, schema)
            all_entities.extend(entities)
            rels = extract_relationships(chunk, entities, schema)
            all_relationships.extend(rels)
        except Exception as e:
            return {"error": str(e), "document_id": document_id}

    resolved, merge_log = resolve_entities(all_entities)

    record = get_ingestion(document_id)
    source = record["filename"] if record else document_id

    try:
        result = build_graph(resolved, all_relationships, source)
    except Exception as e:
        return {"error": f"Graph build failed: {e}", "document_id": document_id}

    update_ingestion(document_id, {
        "status": "built",
        "entities_extracted": len(all_entities),
        "relationships_extracted": len(all_relationships),
    })

    _store_hash(_schema_hash(schema))

    return {
        "document_id": document_id,
        "entities": len(all_entities),
        "relationships": len(all_relationships),
        "resolved": len(resolved),
        "merges": len(merge_log),
        "graph_result": result.model_dump(),
    }


def update_schema_hash():
    current = _schema_hash(get_current_schema())
    _store_hash(current)
