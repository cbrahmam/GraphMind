import json
import math
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY, GRAPH_DATA_DIR

client = Anthropic(api_key=ANTHROPIC_API_KEY)

VECTORS_FILE = Path(GRAPH_DATA_DIR) / "vector_store.json"


def _load_store() -> dict:
    if VECTORS_FILE.exists():
        return json.loads(VECTORS_FILE.read_text())
    return {"vectors": [], "metadata": {"total": 0, "dimension": 0}}


def _save_store(store: dict):
    VECTORS_FILE.parent.mkdir(parents=True, exist_ok=True)
    VECTORS_FILE.write_text(json.dumps(store, default=str))


def generate_embedding_via_claude(text: str) -> list[float]:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[{"role": "user", "content": f"""Generate a 64-dimensional numerical embedding vector for this text.
The vector should capture the semantic meaning of the text.

Text: {text[:500]}

Return ONLY a JSON array of 64 floating point numbers between -1 and 1, like [0.1, -0.3, ...].
No explanation, just the array."""}],
    )

    result = response.content[0].text.strip()
    if result.startswith("```"):
        result = result.split("\n", 1)[1] if "\n" in result else result[3:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()

    try:
        vec = json.loads(result)
        if isinstance(vec, list) and len(vec) > 0:
            return vec[:64]
    except json.JSONDecodeError:
        pass
    return [0.0] * 64


def store_embedding(entity_name: str, text: str, label: str = "", source: str = "") -> dict:
    store = _load_store()
    vec = generate_embedding_via_claude(text)

    entry = {
        "entity": entity_name,
        "label": label,
        "text": text[:500],
        "vector": vec,
        "source": source,
        "stored_at": datetime.now().isoformat(),
    }

    existing = [v for v in store["vectors"] if v["entity"] == entity_name]
    if existing:
        idx = store["vectors"].index(existing[0])
        store["vectors"][idx] = entry
    else:
        store["vectors"].append(entry)

    store["metadata"]["total"] = len(store["vectors"])
    store["metadata"]["dimension"] = len(vec)
    _save_store(store)

    return {"entity": entity_name, "dimension": len(vec), "stored": True}


def search_similar(query: str, top_k: int = 5) -> list[dict]:
    store = _load_store()
    if not store["vectors"]:
        return []

    query_vec = generate_embedding_via_claude(query)
    results = []

    for entry in store["vectors"]:
        sim = _cosine_similarity(query_vec, entry["vector"])
        results.append({
            "entity": entry["entity"],
            "label": entry.get("label", ""),
            "text": entry.get("text", "")[:200],
            "similarity": round(sim, 4),
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


def get_store_stats() -> dict:
    store = _load_store()
    return {
        "total_vectors": store["metadata"]["total"],
        "dimension": store["metadata"]["dimension"],
        "entities": [v["entity"] for v in store["vectors"][:50]],
    }


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
