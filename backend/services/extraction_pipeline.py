from datetime import datetime, timezone

from backend.database import update_ingestion
from backend.models.schemas import (
    TextChunk,
    ExtractedEntity,
    ExtractedRelationship,
    ResolvedEntity,
    GraphBuildResult,
)
from backend.services.entity_extractor import extract_entities
from backend.services.relationship_extractor import extract_relationships
from backend.services.entity_resolver import resolve_entities
from backend.services.graph_builder import build_graph


class PipelineResult:
    def __init__(self):
        self.all_entities: list[ExtractedEntity] = []
        self.all_relationships: list[ExtractedRelationship] = []
        self.resolved_entities: list[ResolvedEntity] = []
        self.merge_log: list[dict] = []
        self.graph_result: GraphBuildResult | None = None
        self.chunks_processed: int = 0
        self.errors: list[str] = []

    def to_dict(self) -> dict:
        return {
            "chunks_processed": self.chunks_processed,
            "entities_extracted": len(self.all_entities),
            "relationships_extracted": len(self.all_relationships),
            "resolved_entities": len(self.resolved_entities),
            "merges": len(self.merge_log),
            "merge_log": self.merge_log,
            "graph_result": self.graph_result.model_dump() if self.graph_result else None,
            "errors": self.errors,
        }


def run_extraction(
    chunks: list[TextChunk],
    schema: dict,
    document_id: str,
) -> tuple[list[ExtractedEntity], list[ExtractedRelationship]]:
    all_entities = []
    all_relationships = []

    update_ingestion(document_id, {"status": "processing"})

    for chunk in chunks:
        try:
            entities = extract_entities(chunk, schema)
            all_entities.extend(entities)

            rels = extract_relationships(chunk, entities, schema)
            all_relationships.extend(rels)
        except Exception as e:
            update_ingestion(document_id, {
                "status": "failed",
                "error_message": f"Extraction failed on chunk {chunk.chunk_index}: {e}",
            })
            raise

    update_ingestion(document_id, {
        "status": "extracted",
        "entities_extracted": len(all_entities),
        "relationships_extracted": len(all_relationships),
    })

    return all_entities, all_relationships


def process_and_build(
    chunks: list[TextChunk],
    schema: dict,
    document_id: str,
    source_filename: str = "",
) -> PipelineResult:
    result = PipelineResult()

    try:
        entities, relationships = run_extraction(chunks, schema, document_id)
        result.all_entities = entities
        result.all_relationships = relationships
        result.chunks_processed = len(chunks)
    except Exception as e:
        result.errors.append(str(e))
        return result

    resolved, merge_log = resolve_entities(entities)
    result.resolved_entities = resolved
    result.merge_log = merge_log

    try:
        graph_result = build_graph(resolved, relationships, source_filename)
        result.graph_result = graph_result

        update_ingestion(document_id, {
            "status": "built",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        result.errors.append(f"Graph build failed: {e}")
        update_ingestion(document_id, {
            "status": "failed",
            "error_message": f"Graph build failed: {e}",
        })

    return result
