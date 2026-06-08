from pydantic import BaseModel
from typing import Optional


class ProcessedDocument(BaseModel):
    id: str
    filename: str
    file_type: str
    total_characters: int
    total_pages: Optional[int] = None
    text_content: str
    sections: list[dict] = []
    metadata: dict = {}
    csv_columns: Optional[list[dict]] = None


class TextChunk(BaseModel):
    chunk_index: int
    text: str
    start_char: int
    end_char: int
    source_document: str
    source_page: Optional[int] = None


class ExtractedEntity(BaseModel):
    name: str
    label: str
    properties: dict = {}
    mentions: list[str] = []
    source_chunk: int = 0
    confidence: str = "medium"
    extraction_method: str = "claude"


class ExtractedRelationship(BaseModel):
    from_entity: str
    from_label: str
    to_entity: str
    to_label: str
    relationship_type: str
    properties: dict = {}
    evidence: str = ""
    confidence: str = "medium"
    source_chunk: int = 0


class ResolvedEntity(BaseModel):
    canonical_name: str
    label: str
    merged_from: list[str] = []
    properties: dict = {}
    mention_count: int = 1
    source_documents: list[str] = []
    confidence: str = "medium"


class GraphBuildResult(BaseModel):
    nodes_created: int = 0
    nodes_updated: int = 0
    relationships_created: int = 0
    relationships_updated: int = 0
    labels_used: list[str] = []
    relationship_types_used: list[str] = []
    build_time_ms: int = 0
    warnings: list[str] = []


class CypherQuery(BaseModel):
    cypher: str
    explanation: str = ""
    query_type: str = "search"
    parameters: dict = {}
    confidence: str = "medium"


class QueryResult(BaseModel):
    query: CypherQuery
    results: list[dict] = []
    result_count: int = 0
    formatted_answer: str = ""
    visualization_data: Optional[dict] = None
    execution_time_ms: int = 0


class CSVColumnMapping(BaseModel):
    entity_column: str
    entity_label: str
    property_columns: list[str] = []
    relationship_columns: list[dict] = []


class IngestURLRequest(BaseModel):
    url: str


class IngestTextRequest(BaseModel):
    text: str
    title: str = "Pasted Text"


class NLQueryRequest(BaseModel):
    question: str


class CypherQueryRequest(BaseModel):
    cypher: str
    parameters: dict = {}


class PathRequest(BaseModel):
    from_entity: str
    to_entity: str
    max_depth: int = 5
