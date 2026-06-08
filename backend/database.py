import sqlite3
from pathlib import Path
from contextlib import contextmanager

from backend.config import GRAPH_DATA_DIR

DB_PATH = GRAPH_DATA_DIR / "graphmind.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS ingestion_history (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'uploaded',
    total_chunks INTEGER DEFAULT 0,
    entities_extracted INTEGER DEFAULT 0,
    relationships_extracted INTEGER DEFAULT 0,
    uploaded_at TEXT NOT NULL,
    completed_at TEXT,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS graph_snapshots (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    node_count INTEGER DEFAULT 0,
    relationship_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS query_history (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    cypher TEXT,
    result_count INTEGER DEFAULT 0,
    execution_time_ms INTEGER DEFAULT 0,
    queried_at TEXT NOT NULL
);
"""


def get_db_path() -> Path:
    return DB_PATH


@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript(SCHEMA_SQL)


def insert_ingestion(record: dict):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO ingestion_history
               (id, filename, file_type, status, total_chunks, uploaded_at)
               VALUES (:id, :filename, :file_type, :status, :total_chunks, :uploaded_at)""",
            record,
        )


def update_ingestion(doc_id: str, updates: dict):
    set_clause = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = doc_id
    with get_db() as conn:
        conn.execute(
            f"UPDATE ingestion_history SET {set_clause} WHERE id = :id",
            updates,
        )


def get_ingestion(doc_id: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM ingestion_history WHERE id = ?", (doc_id,)
        ).fetchone()
        return dict(row) if row else None


def list_ingestions(limit: int = 50) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM ingestion_history ORDER BY uploaded_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def insert_query_history(record: dict):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO query_history
               (id, question, cypher, result_count, execution_time_ms, queried_at)
               VALUES (:id, :question, :cypher, :result_count, :execution_time_ms, :queried_at)""",
            record,
        )


def list_query_history(limit: int = 50) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM query_history ORDER BY queried_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
