import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def detect_contradictions() -> list[dict]:
    contradictions = []

    dupes = neo4j_client.run_query(
        "MATCH (a)-[r1]->(b), (a)-[r2]->(b) "
        "WHERE type(r1) <> type(r2) AND id(r1) < id(r2) "
        "RETURN a.name AS from_name, type(r1) AS type1, type(r2) AS type2, b.name AS to_name "
        "LIMIT 20"
    )
    for d in dupes:
        contradictions.append({
            "type": "conflicting_relationships",
            "description": f"{d['from_name']} has both [{d['type1']}] and [{d['type2']}] to {d['to_name']}",
            "entities": [d["from_name"], d["to_name"]],
            "severity": "medium",
        })

    return contradictions


def detect_confidence_outliers() -> list[dict]:
    outliers = []
    low_conf = neo4j_client.run_query(
        "MATCH (n) WHERE n._confidence = 'low' "
        "RETURN n.name AS name, labels(n)[0] AS label, n._source AS source "
        "LIMIT 20"
    )
    for n in low_conf:
        outliers.append({
            "type": "low_confidence_entity",
            "description": f"{n['name']} ({n['label']}) has low extraction confidence",
            "entity": n["name"],
            "source": n.get("source", ""),
            "severity": "low",
        })
    return outliers


def detect_structural_anomalies() -> list[dict]:
    anomalies = []

    hubs = neo4j_client.run_query(
        "MATCH (n)-[r]-() "
        "WITH n, count(r) AS degree, labels(n)[0] AS label "
        "WHERE degree > 20 "
        "RETURN n.name AS name, label, degree "
        "ORDER BY degree DESC LIMIT 10"
    )
    for h in hubs:
        anomalies.append({
            "type": "super_hub",
            "description": f"{h['name']} ({h['label']}) has {h['degree']} connections — may be over-extracted",
            "entity": h["name"],
            "severity": "medium",
        })

    isolated = neo4j_client.run_query(
        "MATCH (n) WHERE NOT (n)-[]-() "
        "RETURN n.name AS name, labels(n)[0] AS label LIMIT 20"
    )
    for i in isolated:
        anomalies.append({
            "type": "isolated_entity",
            "description": f"{i['name']} ({i['label']}) has no relationships",
            "entity": i["name"],
            "severity": "low",
        })

    self_loops = neo4j_client.run_query(
        "MATCH (n)-[r]->(n) RETURN n.name AS name, type(r) AS type LIMIT 10"
    )
    for s in self_loops:
        anomalies.append({
            "type": "self_loop",
            "description": f"{s['name']} has a self-referencing [{s['type']}] relationship",
            "entity": s["name"],
            "severity": "high",
        })

    return anomalies


def run_full_audit() -> dict:
    contradictions = detect_contradictions()
    outliers = detect_confidence_outliers()
    structural = detect_structural_anomalies()

    all_anomalies = contradictions + outliers + structural
    all_anomalies.sort(key=lambda a: {"high": 0, "medium": 1, "low": 2}.get(a["severity"], 3))

    return {
        "total_anomalies": len(all_anomalies),
        "by_severity": {
            "high": len([a for a in all_anomalies if a["severity"] == "high"]),
            "medium": len([a for a in all_anomalies if a["severity"] == "medium"]),
            "low": len([a for a in all_anomalies if a["severity"] == "low"]),
        },
        "contradictions": contradictions,
        "confidence_outliers": outliers,
        "structural_anomalies": structural,
        "anomalies": all_anomalies,
    }
