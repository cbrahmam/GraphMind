import json
from backend.config import GRAPH_DATA_DIR

TRACKER_FILE = GRAPH_DATA_DIR / "confidence_stats.json"


def _load_stats() -> dict:
    if TRACKER_FILE.exists():
        return json.loads(TRACKER_FILE.read_text())
    return {
        "total_extractions": 0,
        "by_confidence": {"high": 0, "medium": 0, "low": 0},
        "by_method": {"claude": 0, "spacy": 0, "spacy_fallback": 0},
        "user_corrections": 0,
        "accuracy_estimates": {},
    }


def _save_stats(stats: dict):
    TRACKER_FILE.write_text(json.dumps(stats, indent=2))


def record_extraction(entities: list, method: str = "claude"):
    stats = _load_stats()
    stats["total_extractions"] += len(entities)
    stats["by_method"][method] = stats["by_method"].get(method, 0) + len(entities)
    for e in entities:
        conf = getattr(e, "confidence", "medium") if hasattr(e, "confidence") else e.get("confidence", "medium")
        stats["by_confidence"][conf] = stats["by_confidence"].get(conf, 0) + 1
    _save_stats(stats)


def record_correction(entity_name: str, field: str, old_value: str, new_value: str):
    stats = _load_stats()
    stats["user_corrections"] += 1
    _save_stats(stats)


def get_stats() -> dict:
    stats = _load_stats()
    total = stats["total_extractions"]
    if total > 0:
        stats["confidence_distribution"] = {
            k: round(v / total * 100, 1)
            for k, v in stats["by_confidence"].items()
        }
        stats["method_distribution"] = {
            k: round(v / total * 100, 1)
            for k, v in stats["by_method"].items()
        }
    return stats


def get_suggested_threshold() -> float:
    stats = _load_stats()
    total = stats["total_extractions"]
    if total < 50:
        return 0.85

    high_pct = stats["by_confidence"].get("high", 0) / max(total, 1)
    corrections_pct = stats["user_corrections"] / max(total, 1)

    if corrections_pct > 0.1:
        return min(0.95, 0.85 + corrections_pct)
    if high_pct > 0.7:
        return 0.80
    return 0.85
