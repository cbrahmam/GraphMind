import json
from copy import deepcopy
from pathlib import Path

from backend.config import GRAPH_DATA_DIR

SCHEMA_FILE = GRAPH_DATA_DIR / "current_schema.json"

DEFAULT_SCHEMA = {
    "entity_types": [
        {
            "label": "Person",
            "properties": ["name", "title", "organization", "description"],
        },
        {
            "label": "Organization",
            "properties": ["name", "type", "industry", "location", "description"],
        },
        {
            "label": "Location",
            "properties": ["name", "type", "country", "coordinates"],
        },
        {
            "label": "Event",
            "properties": ["name", "date", "location", "description"],
        },
        {
            "label": "Product",
            "properties": ["name", "company", "category", "description"],
        },
        {
            "label": "Technology",
            "properties": ["name", "category", "description"],
        },
        {"label": "Concept", "properties": ["name", "domain", "description"]},
        {
            "label": "Document",
            "properties": ["title", "author", "date", "source"],
        },
    ],
    "relationship_types": [
        {"type": "WORKS_AT", "from": "Person", "to": "Organization"},
        {"type": "LOCATED_IN", "from": "*", "to": "Location"},
        {"type": "PART_OF", "from": "Organization", "to": "Organization"},
        {"type": "FOUNDED_BY", "from": "Organization", "to": "Person"},
        {"type": "RELATED_TO", "from": "*", "to": "*"},
        {"type": "USES", "from": "*", "to": "Technology"},
        {"type": "PARTICIPATED_IN", "from": "Person", "to": "Event"},
        {"type": "PRODUCED_BY", "from": "Product", "to": "Organization"},
        {"type": "MENTIONED_IN", "from": "*", "to": "Document"},
        {"type": "COMPETES_WITH", "from": "Organization", "to": "Organization"},
        {"type": "ACQUIRED", "from": "Organization", "to": "Organization"},
        {"type": "INVESTED_IN", "from": "*", "to": "Organization"},
        {"type": "CAUSED", "from": "Event", "to": "Event"},
        {"type": "DEPENDS_ON", "from": "Technology", "to": "Technology"},
    ],
}

TECH_INDUSTRY_SCHEMA = {
    "entity_types": [
        {
            "label": "Person",
            "properties": ["name", "title", "company", "role", "description"],
        },
        {
            "label": "Company",
            "properties": [
                "name",
                "industry",
                "founded",
                "hq",
                "valuation",
                "employees",
                "description",
            ],
        },
        {
            "label": "Product",
            "properties": [
                "name",
                "company",
                "category",
                "launch_date",
                "description",
            ],
        },
        {
            "label": "Technology",
            "properties": ["name", "category", "open_source", "description"],
        },
        {
            "label": "FundingRound",
            "properties": ["name", "amount", "date", "series", "lead_investor"],
        },
        {
            "label": "Location",
            "properties": ["name", "type", "country"],
        },
    ],
    "relationship_types": [
        {"type": "CEO_OF", "from": "Person", "to": "Company"},
        {"type": "FOUNDED", "from": "Person", "to": "Company"},
        {"type": "WORKS_AT", "from": "Person", "to": "Company"},
        {"type": "BUILDS", "from": "Company", "to": "Product"},
        {"type": "USES", "from": "Company", "to": "Technology"},
        {"type": "COMPETES_WITH", "from": "Company", "to": "Company"},
        {"type": "ACQUIRED", "from": "Company", "to": "Company"},
        {"type": "INVESTED_IN", "from": "Company", "to": "Company"},
        {"type": "RAISED", "from": "Company", "to": "FundingRound"},
        {"type": "HEADQUARTERED_IN", "from": "Company", "to": "Location"},
        {"type": "PARTNER_OF", "from": "Company", "to": "Company"},
        {"type": "DEPENDS_ON", "from": "Technology", "to": "Technology"},
    ],
}

DEFENSE_INTELLIGENCE_SCHEMA = {
    "entity_types": [
        {
            "label": "Person",
            "properties": ["name", "title", "affiliation", "nationality", "description"],
        },
        {
            "label": "Organization",
            "properties": ["name", "type", "country", "sector", "description"],
        },
        {
            "label": "MilitaryAsset",
            "properties": ["name", "type", "operator", "status", "description"],
        },
        {
            "label": "Location",
            "properties": ["name", "type", "country", "coordinates", "strategic_value"],
        },
        {
            "label": "Event",
            "properties": ["name", "date", "location", "type", "casualties", "description"],
        },
        {
            "label": "Technology",
            "properties": ["name", "category", "developer", "status", "description"],
        },
        {
            "label": "Treaty",
            "properties": ["name", "date_signed", "signatories", "status"],
        },
    ],
    "relationship_types": [
        {"type": "COMMANDS", "from": "Person", "to": "Organization"},
        {"type": "ALLIED_WITH", "from": "Organization", "to": "Organization"},
        {"type": "OPERATES", "from": "Organization", "to": "MilitaryAsset"},
        {"type": "DEPLOYED_AT", "from": "MilitaryAsset", "to": "Location"},
        {"type": "OCCURRED_AT", "from": "Event", "to": "Location"},
        {"type": "INVOLVED_IN", "from": "Organization", "to": "Event"},
        {"type": "DEVELOPS", "from": "Organization", "to": "Technology"},
        {"type": "SIGNATORY_OF", "from": "Organization", "to": "Treaty"},
        {"type": "SUPPLIES", "from": "Organization", "to": "Organization"},
        {"type": "OPPOSES", "from": "Organization", "to": "Organization"},
    ],
}

BIOMEDICAL_SCHEMA = {
    "entity_types": [
        {
            "label": "Disease",
            "properties": ["name", "icd_code", "category", "description"],
        },
        {
            "label": "Drug",
            "properties": ["name", "brand_name", "manufacturer", "approval_status", "description"],
        },
        {
            "label": "Gene",
            "properties": ["name", "symbol", "chromosome", "function"],
        },
        {
            "label": "Protein",
            "properties": ["name", "gene", "function"],
        },
        {
            "label": "ClinicalTrial",
            "properties": ["name", "phase", "status", "sponsor", "start_date"],
        },
        {
            "label": "Researcher",
            "properties": ["name", "institution", "specialization"],
        },
        {
            "label": "Institution",
            "properties": ["name", "type", "location"],
        },
    ],
    "relationship_types": [
        {"type": "TREATS", "from": "Drug", "to": "Disease"},
        {"type": "TARGETS", "from": "Drug", "to": "Protein"},
        {"type": "ENCODES", "from": "Gene", "to": "Protein"},
        {"type": "ASSOCIATED_WITH", "from": "Gene", "to": "Disease"},
        {"type": "TESTED_IN", "from": "Drug", "to": "ClinicalTrial"},
        {"type": "CONDUCTED_BY", "from": "ClinicalTrial", "to": "Institution"},
        {"type": "RESEARCHES", "from": "Researcher", "to": "Disease"},
        {"type": "AFFILIATED_WITH", "from": "Researcher", "to": "Institution"},
        {"type": "INTERACTS_WITH", "from": "Protein", "to": "Protein"},
        {"type": "CAUSES", "from": "Drug", "to": "Disease"},
    ],
}

PRESETS = {
    "default": {"name": "General Purpose", "schema": DEFAULT_SCHEMA},
    "tech_industry": {"name": "Tech Industry", "schema": TECH_INDUSTRY_SCHEMA},
    "defense_intelligence": {
        "name": "Defense & Intelligence",
        "schema": DEFENSE_INTELLIGENCE_SCHEMA,
    },
    "biomedical": {"name": "Biomedical", "schema": BIOMEDICAL_SCHEMA},
}


def get_current_schema() -> dict:
    if SCHEMA_FILE.exists():
        return json.loads(SCHEMA_FILE.read_text())
    save_schema(DEFAULT_SCHEMA)
    return deepcopy(DEFAULT_SCHEMA)


def save_schema(schema: dict):
    SCHEMA_FILE.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_FILE.write_text(json.dumps(schema, indent=2))


def get_presets() -> dict:
    return {k: v["name"] for k, v in PRESETS.items()}


def load_preset(name: str) -> dict:
    if name not in PRESETS:
        raise ValueError(f"Unknown preset: {name}. Available: {list(PRESETS.keys())}")
    schema = deepcopy(PRESETS[name]["schema"])
    save_schema(schema)
    return schema
