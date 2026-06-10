# GraphMind

**Turn unstructured data into connected intelligence.**

GraphMind is an AI-powered knowledge graph builder that extracts entities and relationships from documents, web pages, and structured data, then builds a queryable Neo4j knowledge graph with natural language search, interactive visualization, and automated insights.

## The Problem

Knowledge is trapped in documents, spreadsheets, and web pages. The relationships between people, companies, technologies, and events exist implicitly in text but are invisible to traditional search. Finding connections requires manually reading and cross-referencing dozens of sources.

## The Solution

GraphMind automatically extracts entities and relationships from any data source and builds a queryable knowledge graph in Neo4j. Ask questions in plain English, explore connections visually, discover hidden patterns, and generate insights that would take humans days to uncover.

## Features

- **Multi-format data ingestion** — PDF, DOCX, CSV, web pages, raw text, JSON, HTML, Markdown
- **AI-powered entity extraction** — Two-stage pipeline: spaCy NER pre-filtering + Claude refinement
- **Automatic relationship discovery** — Claude identifies relationships with evidence citations
- **Entity resolution & deduplication** — Exact + fuzzy matching (SequenceMatcher >= 0.85) with property merging
- **Interactive graph visualization** — Force-directed 2D graph with colored nodes, filters, search, and zoom
- **Natural language queries** — Ask questions in English, auto-translated to Cypher via Claude
- **Graph algorithms** — Degree/PageRank/Betweenness centrality, community detection, similarity analysis
- **AI-generated insights** — Pattern discovery, knowledge gaps, hidden connections, exploration suggestions
- **Multiple export formats** — JSON, CSV, GraphML, Cypher statements, Markdown report
- **Schema-driven extraction** — 4 domain presets: General, Tech Industry, Defense & Intelligence, Biomedical

## Architecture

```
Data Sources (PDF, DOCX, CSV, URL, Text)
    |
    v
Document Parser --> Text Chunker (2000 chars, 200 overlap)
    |
    v
Entity Extractor (spaCy NER --> Claude Refinement)
    |
    v
Relationship Extractor (Claude with schema context)
    |
    v
Entity Resolver (exact + fuzzy deduplication)
    |
    v
Neo4j Graph Builder (MERGE-based upsert with metadata)
    |
    v
+-----------------+--------------------+--------------------+
|                 |                    |                    |
Graph Explorer    NL Query Engine      Graph Algorithms
(react-force-     (NL -> Cypher ->     (Centrality,
 graph-2d)         Neo4j -> NL answer)  Communities,
                                        Similarity)
```

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend | FastAPI (Python) | Async, type-safe, auto-docs |
| Frontend | React + Vite + TailwindCSS | Fast dev, utility-first styling |
| Graph DB | Neo4j 5 Community | Native graph storage, Cypher query language, APOC/GDS plugins |
| AI | Claude API (Anthropic SDK) | Best-in-class entity extraction and NL understanding |
| NLP | spaCy (en_core_web_sm) | Fast pre-filtering NER before Claude |
| Visualization | react-force-graph-2d | Interactive force-directed graph rendering |
| State | Zustand | Lightweight React state management |
| App DB | SQLite | Simple persistence for ingestion history and query logs |

## Graph Algorithms

| Algorithm | What it finds | When to use |
|-----------|--------------|-------------|
| Degree Centrality | Most connected entities | "Who has the most relationships?" |
| PageRank | Most influential entities | "Who is referenced by important entities?" |
| Betweenness Centrality | Bridge entities | "Who connects different clusters?" |
| Community Detection | Natural clusters | "What groups exist in the data?" |
| Similarity Analysis | Structurally similar entities | "What's similar to Anthropic?" |

## Getting Started

### Prerequisites

- Docker (for Neo4j)
- Python 3.11+
- Node.js 18+
- Anthropic API key

### Setup

1. **Start Neo4j**:
```bash
docker-compose up -d
```

2. **Backend**:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env  # Add your ANTHROPIC_API_KEY
uvicorn backend.main:app --reload
```

3. **Frontend**:
```bash
cd frontend
npm install
npm run dev
```

4. **Open**: http://localhost:5173

5. **Load demo data**: Click "Load Demo Data" on the dashboard to populate the graph with sample articles about AI companies, defense technology, and cloud computing.

### Environment Variables

```
ANTHROPIC_API_KEY=your_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=graphmind123
```

## Schema Customization

GraphMind supports domain-specific schemas that guide entity extraction:

- **General Purpose** — Person, Organization, Technology, Location, Event, Concept
- **Tech Industry** — Adds Product, Funding Round, Patent, Acquisition
- **Defense & Intelligence** — Adds Military Unit, Weapon System, Operation, Threat Actor
- **Biomedical** — Adds Gene, Protein, Disease, Drug, Clinical Trial

Create custom schemas via the Schema page or API:

```json
{
  "entity_types": [
    { "label": "Company", "description": "A business entity", "properties": ["industry", "revenue"] }
  ],
  "relationship_types": [
    { "type": "ACQUIRED", "description": "One company acquiring another" }
  ]
}
```

## API Endpoints

### Ingestion
- `POST /api/ingest/document` — Upload file (PDF, DOCX, TXT, etc.)
- `POST /api/ingest/url` — Fetch and parse URL
- `POST /api/ingest/text` — Ingest raw text
- `POST /api/ingest/csv` — Upload CSV for structured import

### Extraction
- `POST /api/extract/pipeline/{id}` — Full extraction pipeline
- `POST /api/extract/resolve` — Cross-document entity resolution

### Query
- `POST /api/query` — Natural language question
- `POST /api/query/cypher` — Execute raw Cypher
- `POST /api/query/path` — Find paths between entities
- `GET /api/query/suggestions` — AI-generated query suggestions

### Graph
- `GET /api/graph/full` — Full graph data for visualization
- `GET /api/graph/stats` — Node/relationship counts
- `GET /api/graph/neighbors/{id}` — Neighborhood subgraph

### Insights & Export
- `POST /api/insights/generate` — AI-powered graph analysis
- `GET /api/insights/centrality` — Centrality rankings
- `GET /api/insights/communities` — Community detection
- `GET /api/export/{format}` — Export as JSON, CSV, GraphML, Cypher, or Markdown

## License

MIT
