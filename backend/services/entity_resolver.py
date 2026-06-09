from difflib import SequenceMatcher

from backend.models.schemas import ExtractedEntity, ResolvedEntity


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _merge_properties(existing: dict, new: dict) -> dict:
    merged = dict(existing)
    for k, v in new.items():
        if k not in merged or not merged[k]:
            merged[k] = v
        elif v and str(v) not in str(merged[k]):
            if isinstance(merged[k], str) and isinstance(v, str):
                if len(v) > len(merged[k]):
                    merged[k] = v
    return merged


def resolve_entities(
    all_entities: list[ExtractedEntity],
    similarity_threshold: float = 0.85,
) -> tuple[list[ResolvedEntity], list[dict]]:
    groups: dict[str, dict] = {}
    merge_log: list[dict] = []

    for entity in all_entities:
        key = f"{entity.name.lower().strip()}::{entity.label}"
        if key in groups:
            g = groups[key]
            g["properties"] = _merge_properties(g["properties"], entity.properties)
            g["mention_count"] += 1
            for m in entity.mentions:
                if m not in g["mentions"]:
                    g["mentions"].append(m)
            if entity.source_chunk not in g["source_chunks"]:
                g["source_chunks"].append(entity.source_chunk)
            doc = getattr(entity, "source_document", None)
            if doc and doc not in g["source_documents"]:
                g["source_documents"].append(doc)
            if entity.confidence == "high" and g["confidence"] != "high":
                g["confidence"] = "high"
        else:
            groups[key] = {
                "canonical_name": entity.name,
                "label": entity.label,
                "properties": dict(entity.properties),
                "mentions": list(entity.mentions),
                "mention_count": 1,
                "source_chunks": [entity.source_chunk],
                "source_documents": [],
                "merged_from": [entity.name],
                "confidence": entity.confidence,
            }

    keys = list(groups.keys())
    merged_into: dict[str, str] = {}

    for i in range(len(keys)):
        if keys[i] in merged_into:
            continue
        for j in range(i + 1, len(keys)):
            if keys[j] in merged_into:
                continue

            gi = groups[keys[i]]
            gj = groups[keys[j]]

            if gi["label"] != gj["label"]:
                continue

            name_sim = _similarity(gi["canonical_name"], gj["canonical_name"])
            if name_sim < similarity_threshold:
                all_mentions_i = [gi["canonical_name"]] + gi["mentions"]
                all_mentions_j = [gj["canonical_name"]] + gj["mentions"]
                best = max(
                    _similarity(a, b)
                    for a in all_mentions_i
                    for b in all_mentions_j
                )
                if best < similarity_threshold:
                    continue

            target = keys[i]
            source = keys[j]
            if gj["mention_count"] > gi["mention_count"]:
                target, source = source, target

            gt = groups[target]
            gs = groups[source]

            gt["properties"] = _merge_properties(gt["properties"], gs["properties"])
            gt["mention_count"] += gs["mention_count"]
            for m in gs["mentions"]:
                if m not in gt["mentions"]:
                    gt["mentions"].append(m)
            for n in gs["merged_from"]:
                if n not in gt["merged_from"]:
                    gt["merged_from"].append(n)
            for sc in gs["source_chunks"]:
                if sc not in gt["source_chunks"]:
                    gt["source_chunks"].append(sc)
            for sd in gs["source_documents"]:
                if sd not in gt["source_documents"]:
                    gt["source_documents"].append(sd)

            merged_into[source] = target
            merge_log.append({
                "merged": gs["canonical_name"],
                "into": gt["canonical_name"],
                "label": gt["label"],
                "similarity": round(name_sim, 3),
            })

    resolved = []
    for key, g in groups.items():
        if key in merged_into:
            continue
        resolved.append(
            ResolvedEntity(
                canonical_name=g["canonical_name"],
                label=g["label"],
                merged_from=g["merged_from"],
                properties=g["properties"],
                mention_count=g["mention_count"],
                source_documents=g["source_documents"],
                confidence=g["confidence"],
            )
        )

    resolved.sort(key=lambda e: e.mention_count, reverse=True)
    return resolved, merge_log
