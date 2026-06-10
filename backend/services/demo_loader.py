import os
from pathlib import Path

from backend.config import BASE_DIR
from backend.services.document_processor import process_document, process_text_content
from backend.services.text_chunker import chunk_for_extraction
from backend.services.extraction_pipeline import process_and_build
from backend.services.schema_manager import get_current_schema
from backend.database import insert_ingestion
from datetime import datetime, timezone


SAMPLE_DIR = BASE_DIR.parent / "sample-data"
ARTICLES_DIR = SAMPLE_DIR / "sample_articles"
CSV_DIR = SAMPLE_DIR / "sample_csv"


def get_demo_status():
    article_files = list(ARTICLES_DIR.glob("*.txt")) if ARTICLES_DIR.exists() else []
    csv_files = list(CSV_DIR.glob("*.csv")) if CSV_DIR.exists() else []
    return {
        "articles_available": len(article_files),
        "csv_available": len(csv_files),
        "article_files": [f.name for f in article_files],
        "csv_files": [f.name for f in csv_files],
    }


def load_demo_data(progress_callback=None):
    def log(msg):
        if progress_callback:
            progress_callback(msg)

    schema = get_current_schema()
    results = {
        "documents_processed": 0,
        "total_entities": 0,
        "total_relationships": 0,
        "errors": [],
        "progress": [],
    }

    article_files = sorted(ARTICLES_DIR.glob("*.txt")) if ARTICLES_DIR.exists() else []
    csv_files = sorted(CSV_DIR.glob("*.csv")) if CSV_DIR.exists() else []

    for article_path in article_files:
        try:
            log(f"Processing {article_path.name}...")
            doc = process_document(str(article_path), "txt")
            chunks = chunk_for_extraction(doc.text_content, doc.id)

            insert_ingestion({
                "id": doc.id,
                "filename": article_path.name,
                "file_type": "txt",
                "status": "uploaded",
                "total_chunks": len(chunks),
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
            })

            result = process_and_build(chunks, schema, doc.id, article_path.name)
            results["documents_processed"] += 1
            results["total_entities"] += len(result.all_entities)
            results["total_relationships"] += len(result.all_relationships)

            log(f"  {article_path.name}: {len(result.all_entities)} entities, {len(result.all_relationships)} relationships")
            results["progress"].append({
                "file": article_path.name,
                "entities": len(result.all_entities),
                "relationships": len(result.all_relationships),
            })
        except Exception as e:
            results["errors"].append(f"{article_path.name}: {e}")
            log(f"  Error: {article_path.name}: {e}")

    for csv_path in csv_files:
        try:
            log(f"Processing {csv_path.name}...")
            doc = process_document(str(csv_path), "csv")
            insert_ingestion({
                "id": doc.id,
                "filename": csv_path.name,
                "file_type": "csv",
                "status": "uploaded",
                "total_chunks": 0,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
            })

            from backend.services.graph_builder import import_csv_to_graph
            mapping = {
                "entity_column": "name",
                "entity_label": "Organization",
                "property_columns": ["hq", "industry", "funding", "employees"],
                "relationship_columns": [
                    {"column": "founder", "target_label": "Person", "relationship": "FOUNDED_BY"},
                    {"column": "hq", "target_label": "Location", "relationship": "HEADQUARTERED_IN"},
                ],
            }
            gr = import_csv_to_graph(str(csv_path), mapping, csv_path.name)
            results["documents_processed"] += 1
            results["total_entities"] += gr.nodes_created
            results["total_relationships"] += gr.relationships_created
            log(f"  {csv_path.name}: {gr.nodes_created} nodes, {gr.relationships_created} relationships")
        except Exception as e:
            results["errors"].append(f"{csv_path.name}: {e}")
            log(f"  Error: {csv_path.name}: {e}")

    log("Demo data loading complete!")
    return results
