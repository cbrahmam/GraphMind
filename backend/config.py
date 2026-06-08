import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
GRAPH_DATA_DIR = BASE_DIR / "graph_data"

UPLOAD_DIR.mkdir(exist_ok=True)
GRAPH_DATA_DIR.mkdir(exist_ok=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "graphmind123")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{GRAPH_DATA_DIR / 'graphmind.db'}")

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".html", ".csv", ".json"}
MAX_UPLOAD_SIZE_MB = 50
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200
