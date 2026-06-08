from pydantic import BaseModel
from typing import Optional


class IngestionRecord(BaseModel):
    id: str
    filename: str
    file_type: str
    status: str = "uploaded"
    total_chunks: int = 0
    entities_extracted: int = 0
    relationships_extracted: int = 0
    uploaded_at: str = ""
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class GraphSnapshot(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    node_count: int = 0
    relationship_count: int = 0
    created_at: str = ""


class QueryHistoryRecord(BaseModel):
    id: str
    question: str
    cypher: Optional[str] = None
    result_count: int = 0
    execution_time_ms: int = 0
    queried_at: str = ""
