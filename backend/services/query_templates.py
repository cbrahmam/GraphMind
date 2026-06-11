import json
from backend.config import GRAPH_DATA_DIR

TEMPLATES_FILE = GRAPH_DATA_DIR / "query_templates.json"

_builtin_templates = [
    {
        "id": "find-role-at-company",
        "name": "Find role at company",
        "description": "Find people with a specific role at a company",
        "cypher": "MATCH (p:Person)-[:WORKS_AT]->(o:Organization) WHERE toLower(o.name) CONTAINS toLower($company) RETURN p.name AS person, p.title AS title, o.name AS company",
        "parameters": {"company": ""},
        "category": "people",
    },
    {
        "id": "company-connections",
        "name": "Company connections",
        "description": "All entities connected to a company",
        "cypher": "MATCH (o:Organization)-[r]-(n) WHERE toLower(o.name) CONTAINS toLower($company) RETURN o.name AS company, type(r) AS relationship, n.name AS connected_to, labels(n)[0] AS type LIMIT 50",
        "parameters": {"company": ""},
        "category": "exploration",
    },
    {
        "id": "technology-users",
        "name": "Technology users",
        "description": "Who uses a specific technology",
        "cypher": "MATCH (n)-[:USES]->(t:Technology) WHERE toLower(t.name) CONTAINS toLower($tech) RETURN n.name AS user, labels(n)[0] AS type, t.name AS technology",
        "parameters": {"tech": ""},
        "category": "technology",
    },
    {
        "id": "most-connected",
        "name": "Most connected entities",
        "description": "Entities with the most relationships",
        "cypher": "MATCH (n)-[r]-() WITH n, count(r) AS connections, labels(n)[0] AS label RETURN n.name AS entity, label, connections ORDER BY connections DESC LIMIT $limit",
        "parameters": {"limit": 20},
        "category": "analysis",
    },
    {
        "id": "orphan-nodes",
        "name": "Isolated entities",
        "description": "Entities with no relationships",
        "cypher": "MATCH (n) WHERE NOT (n)-[]-() RETURN n.name AS entity, labels(n)[0] AS label ORDER BY label, n.name",
        "parameters": {},
        "category": "analysis",
    },
    {
        "id": "recent-entities",
        "name": "Recently added entities",
        "description": "Entities sorted by extraction time",
        "cypher": "MATCH (n) WHERE n._extracted_at IS NOT NULL RETURN n.name AS entity, labels(n)[0] AS label, n._source AS source, n._extracted_at AS added ORDER BY added DESC LIMIT $limit",
        "parameters": {"limit": 25},
        "category": "history",
    },
]


def get_templates() -> list[dict]:
    custom = _load_custom()
    return _builtin_templates + custom


def get_template(template_id: str) -> dict | None:
    for t in get_templates():
        if t["id"] == template_id:
            return t
    return None


def save_template(template: dict) -> dict:
    custom = _load_custom()
    existing = next((i for i, t in enumerate(custom) if t["id"] == template["id"]), None)
    if existing is not None:
        custom[existing] = template
    else:
        custom.append(template)
    _save_custom(custom)
    return template


def delete_template(template_id: str) -> bool:
    custom = _load_custom()
    before = len(custom)
    custom = [t for t in custom if t["id"] != template_id]
    if len(custom) < before:
        _save_custom(custom)
        return True
    return False


def _load_custom() -> list[dict]:
    if TEMPLATES_FILE.exists():
        return json.loads(TEMPLATES_FILE.read_text())
    return []


def _save_custom(templates: list[dict]):
    TEMPLATES_FILE.write_text(json.dumps(templates, indent=2))
