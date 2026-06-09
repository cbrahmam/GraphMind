import time
from datetime import datetime, timezone

from backend.models.schemas import (
    ResolvedEntity,
    ExtractedRelationship,
    GraphBuildResult,
)
from backend.neo4j_client import neo4j_client


def _ensure_indexes(labels: set[str]):
    for label in labels:
        try:
            neo4j_client.run_query(
                f"CREATE INDEX IF NOT EXISTS FOR (n:{label}) ON (n.name)"
            )
        except Exception:
            pass


def build_graph(
    entities: list[ResolvedEntity],
    relationships: list[ExtractedRelationship],
    source_document: str = "",
) -> GraphBuildResult:
    start = time.time()
    warnings = []

    labels_used = set()
    for e in entities:
        labels_used.add(e.label)

    _ensure_indexes(labels_used)

    nodes_created = 0
    nodes_updated = 0
    now = datetime.now(timezone.utc).isoformat()

    for entity in entities:
        props = dict(entity.properties)
        props["_source"] = source_document
        props["_confidence"] = entity.confidence
        props["_extracted_at"] = now
        props["_mention_count"] = entity.mention_count
        props["_label"] = entity.label

        if entity.merged_from:
            props["_aliases"] = ", ".join(entity.merged_from)

        existing = neo4j_client.run_query(
            f"MATCH (n:{entity.label} {{name: $name}}) RETURN n.id AS id",
            {"name": entity.canonical_name},
        )

        if existing:
            nodes_updated += 1
        else:
            nodes_created += 1

        neo4j_client.merge_node(entity.label, entity.canonical_name, props)

        if entity.confidence == "low":
            warnings.append(f"Low confidence entity: {entity.canonical_name} ({entity.label})")

    rel_types_used = set()
    rels_created = 0
    rels_updated = 0

    entity_lookup = {e.canonical_name.lower(): e for e in entities}

    for rel in relationships:
        from_entity = entity_lookup.get(rel.from_entity.lower())
        to_entity = entity_lookup.get(rel.to_entity.lower())

        from_label = from_entity.label if from_entity else rel.from_label
        to_label = to_entity.label if to_entity else rel.to_label
        from_name = from_entity.canonical_name if from_entity else rel.from_entity
        to_name = to_entity.canonical_name if to_entity else rel.to_entity

        if not from_label or not to_label:
            warnings.append(f"Skipped relationship: {rel.from_entity} -[{rel.relationship_type}]-> {rel.to_entity} (missing labels)")
            continue

        from_exists = neo4j_client.run_query(
            f"MATCH (n:{from_label} {{name: $name}}) RETURN count(n) AS c",
            {"name": from_name},
        )
        to_exists = neo4j_client.run_query(
            f"MATCH (n:{to_label} {{name: $name}}) RETURN count(n) AS c",
            {"name": to_name},
        )

        if not from_exists or from_exists[0]["c"] == 0 or not to_exists or to_exists[0]["c"] == 0:
            warnings.append(f"Skipped relationship: {from_name} -[{rel.relationship_type}]-> {to_name} (node not found)")
            continue

        props = dict(rel.properties)
        props["_source"] = source_document
        props["_confidence"] = rel.confidence
        props["_extracted_at"] = now
        if rel.evidence:
            props["_evidence"] = rel.evidence

        existing_rel = neo4j_client.run_query(
            f"MATCH (a:{from_label} {{name: $from}})-[r:{rel.relationship_type}]->(b:{to_label} {{name: $to}}) RETURN count(r) AS c",
            {"from": from_name, "to": to_name},
        )

        if existing_rel and existing_rel[0]["c"] > 0:
            rels_updated += 1
        else:
            rels_created += 1

        rel_types_used.add(rel.relationship_type)
        neo4j_client.create_relationship(
            from_name, from_label, to_name, to_label,
            rel.relationship_type, props,
        )

    elapsed = int((time.time() - start) * 1000)

    return GraphBuildResult(
        nodes_created=nodes_created,
        nodes_updated=nodes_updated,
        relationships_created=rels_created,
        relationships_updated=rels_updated,
        labels_used=sorted(labels_used),
        relationship_types_used=sorted(rel_types_used),
        build_time_ms=elapsed,
        warnings=warnings,
    )


def import_csv_to_graph(
    csv_path: str,
    column_mapping: dict,
    source_document: str = "",
) -> GraphBuildResult:
    import pandas as pd

    df = pd.read_csv(csv_path)
    start = time.time()

    entity_col = column_mapping["entity_column"]
    entity_label = column_mapping["entity_label"]
    prop_cols = column_mapping.get("property_columns", [])
    rel_cols = column_mapping.get("relationship_columns", [])

    labels_used = {entity_label}
    rel_types_used = set()
    nodes_created = 0
    nodes_updated = 0
    rels_created = 0
    warnings = []
    now = datetime.now(timezone.utc).isoformat()

    _ensure_indexes({entity_label})

    for _, row in df.iterrows():
        name = str(row.get(entity_col, "")).strip()
        if not name:
            continue

        props = {"_source": source_document, "_extracted_at": now, "_label": entity_label}
        for col in prop_cols:
            val = row.get(col)
            if pd.notna(val):
                props[col] = str(val) if not isinstance(val, (int, float)) else val

        existing = neo4j_client.run_query(
            f"MATCH (n:{entity_label} {{name: $name}}) RETURN n.id AS id",
            {"name": name},
        )
        if existing:
            nodes_updated += 1
        else:
            nodes_created += 1

        neo4j_client.merge_node(entity_label, name, props)

        for rel_map in rel_cols:
            target_value = str(row.get(rel_map["column"], "")).strip()
            if not target_value:
                continue

            target_label = rel_map["target_label"]
            rel_type = rel_map["relationship"]
            labels_used.add(target_label)
            rel_types_used.add(rel_type)

            _ensure_indexes({target_label})
            neo4j_client.merge_node(
                target_label, target_value,
                {"_source": source_document, "_extracted_at": now, "_label": target_label},
            )

            neo4j_client.create_relationship(
                name, entity_label, target_value, target_label,
                rel_type,
                {"_source": source_document, "_extracted_at": now},
            )
            rels_created += 1

    elapsed = int((time.time() - start) * 1000)

    return GraphBuildResult(
        nodes_created=nodes_created,
        nodes_updated=nodes_updated,
        relationships_created=rels_created,
        labels_used=sorted(labels_used),
        relationship_types_used=sorted(rel_types_used),
        build_time_ms=elapsed,
        warnings=warnings,
    )
