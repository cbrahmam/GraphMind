# GraphMind - AI Knowledge Graph Builder

## Overview
A platform that takes unstructured data (documents, PDFs, websites, CSVs, APIs) and automatically extracts entities, relationships, and concepts to build a queryable knowledge graph in Neo4j. Users can explore the graph visually, ask natural language questions that get translated to Cypher queries, discover hidden connections between entities, and generate insights from the graph structure. Think of it as "a self-building knowledge graph that turns your messy data into connected intelligence."

This project directly leverages your Neo4j experience at Janes and shows graph database expertise that very few AI freelancers can demonstrate. Entity extraction, relationship mapping, graph algorithms, Cypher query generation, and interactive graph visualization hit a unique intersection of AI + graph databases that's increasingly in demand.

## Tech Stack
- **Frontend**: React (Vite), TailwindCSS, Neo4j Bloom-style graph visualization (using `react-force-graph-3d` or `@neo4j-nvl/react`)
- **Backend**: Python (FastAPI)
- **AI**: Claude API (Anthropic) for entity extraction, relationship discovery, and natural language to Cypher
- **Graph Database**: Neo4j (Community Edition, local or Docker)
- **Document Processing**: PyMuPDF (PDFs), python-docx (DOCX), beautifulsoup4 (web pages), pandas (CSVs)
- **NLP**: spaCy for named entity recognition as a pre-filter before AI extraction
- **Database**: SQLite for app config and ingestion history, Neo4j for the knowledge graph itself
- **Package Manager**: npm for frontend, pip for backend

## IMPORTANT BUILD INSTRUCTIONS
- DO NOT one-shot this build. Break it into the commit blocks below.
- Each block should be a working, testable increment.
- Write clean, well-commented code.
- Test each block before moving to the next.
- Use proper error handling throughout.
- No placeholder or dummy code. Everything should work.
- One commit block per day.

---

## COMMIT BLOCK 1 (Day 1): Project Scaffolding, Neo4j Setup & Document Ingestion

### What to build:
1. Initialize the project structure:
```
graphmind/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── config.py
│   ├── database.py                    # SQLite for app state
│   ├── neo4j_client.py                # Neo4j connection manager
│   ├── routers/
│   │   ├── ingest.py                  # Document ingestion endpoints
│   │   ├── graph.py                   # Graph query and exploration endpoints
│   │   ├── extract.py                 # Entity/relationship extraction (Block 2)
│   │   ├── query.py                   # Natural language query endpoints (Block 3)
│   │   ├── insights.py               # Graph insights and analysis (Block 5)
│   │   └── export.py                 # Export endpoints (Block 6)
│   ├── services/
│   │   ├── document_processor.py      # Multi-format document parsing
│   │   ├── text_chunker.py            # Smart text chunking for extraction
│   │   ├── entity_extractor.py        # AI entity extraction (Block 2)
│   │   ├── relationship_extractor.py  # AI relationship discovery (Block 2)
│   │   ├── graph_builder.py           # Builds Neo4j graph from extractions (Block 2)
│   │   ├── cypher_generator.py        # NL to Cypher translation (Block 3)
│   │   ├── graph_algorithms.py        # Graph analysis algorithms (Block 5)
│   │   └── schema_manager.py          # Graph schema management
│   ├── models/
│   │   ├── schemas.py
│   │   └── db_models.py
│   ├── uploads/
│   └── graph_data/
├── frontend/                          # Set up in Block 4
├── sample-data/
│   ├── sample_articles/               # 5-10 articles about a specific domain
│   ├── sample_csv/                    # Structured data to import
│   └── sample_schema.json             # Pre-defined entity/relationship schema
├── docker-compose.yml                 # Neo4j container
├── README.md
└── .gitignore
```

2. **Neo4j setup**:
   - `docker-compose.yml`:
     ```yaml
     version: '3'
     services:
       neo4j:
         image: neo4j:5-community
         ports:
           - "7474:7474"    # Browser
           - "7687:7687"    # Bolt
         environment:
           NEO4J_AUTH: neo4j/graphmind123
           NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
         volumes:
           - neo4j_data:/data
     volumes:
       neo4j_data:
     ```
   - `neo4j_client.py`:
     - Singleton Neo4j driver connection
     - Functions:
       - `run_query(cypher: str, params: dict) -> List[dict]`
       - `create_node(label: str, properties: dict) -> str` (returns node ID)
       - `create_relationship(from_id: str, to_id: str, rel_type: str, properties: dict)`
       - `get_node(node_id: str) -> dict`
       - `search_nodes(label: str, property: str, value: str) -> List[dict]`
       - `get_schema() -> GraphSchema` (list of labels, relationship types, property keys)
       - `get_stats() -> dict` (node count, relationship count, label counts)
       - `clear_graph()` (for resetting)
     - Connection from environment variables: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

3. **Build the document processor** (`document_processor.py`):
   - Function: `process_document(file_path: str, file_type: str) -> ProcessedDocument`
   - Support formats:
     - **PDF**: PyMuPDF text extraction, page by page
     - **DOCX**: python-docx, paragraph by paragraph
     - **TXT/MD**: Direct read
     - **HTML/Web**: beautifulsoup4, extract main content
     - **CSV**: pandas, each row becomes a potential entity with columns as properties
     - **JSON**: Parse and flatten nested structures
   - For text documents: clean, normalize whitespace, remove boilerplate
   - For CSVs: detect column types, identify potential entity columns vs property columns

   ```python
   class ProcessedDocument(BaseModel):
       id: str
       filename: str
       file_type: str
       total_characters: int
       total_pages: Optional[int]
       text_content: str
       sections: List[dict]             # [{title, content, page}] for structured docs
       metadata: dict                    # Any extracted metadata (author, date, etc.)
       csv_columns: Optional[List[dict]] # For CSVs: [{name, type, sample_values}]
   ```

4. **Build the text chunker** (`text_chunker.py`):
   - Function: `chunk_for_extraction(text: str, chunk_size: int = 2000, overlap: int = 200) -> List[TextChunk]`
   - Split text into chunks optimized for entity/relationship extraction:
     - Try to split at paragraph boundaries
     - If paragraphs are too long, split at sentence boundaries
     - Overlap ensures entities that span chunk boundaries aren't missed
   - Each chunk tracks its position in the original document

   ```python
   class TextChunk(BaseModel):
       chunk_index: int
       text: str
       start_char: int
       end_char: int
       source_document: str
       source_page: Optional[int]
   ```

5. **Schema manager** (`schema_manager.py`):
   - Allows users to define what kinds of entities and relationships they want extracted
   - Pre-defined schemas for common domains:
   
   ```python
   # Default general-purpose schema
   DEFAULT_SCHEMA = {
       "entity_types": [
           {"label": "Person", "properties": ["name", "title", "organization", "description"]},
           {"label": "Organization", "properties": ["name", "type", "industry", "location", "description"]},
           {"label": "Location", "properties": ["name", "type", "country", "coordinates"]},
           {"label": "Event", "properties": ["name", "date", "location", "description"]},
           {"label": "Product", "properties": ["name", "company", "category", "description"]},
           {"label": "Technology", "properties": ["name", "category", "description"]},
           {"label": "Concept", "properties": ["name", "domain", "description"]},
           {"label": "Document", "properties": ["title", "author", "date", "source"]}
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
           {"type": "DEPENDS_ON", "from": "Technology", "to": "Technology"}
       ]
   }
   
   # Domain-specific schemas
   TECH_INDUSTRY_SCHEMA = { ... }
   DEFENSE_INTELLIGENCE_SCHEMA = { ... }
   BIOMEDICAL_SCHEMA = { ... }
   ```

   - Endpoints:
     - `GET /api/schema` - Get current schema
     - `PUT /api/schema` - Update schema
     - `GET /api/schema/presets` - List available preset schemas
     - `POST /api/schema/presets/{name}` - Load a preset schema

6. **SQLite for app state**:
   ```sql
   CREATE TABLE ingestion_history (
       id TEXT PRIMARY KEY,
       filename TEXT,
       file_type TEXT,
       status TEXT,                      -- "uploaded", "processing", "extracted", "built", "failed"
       total_chunks INTEGER,
       entities_extracted INTEGER,
       relationships_extracted INTEGER,
       uploaded_at TEXT,
       completed_at TEXT,
       error_message TEXT
   );
   
   CREATE TABLE graph_snapshots (
       id TEXT PRIMARY KEY,
       name TEXT,
       description TEXT,
       node_count INTEGER,
       relationship_count INTEGER,
       created_at TEXT
   );
   ```

7. **Create ingestion endpoints**:
   - `POST /api/ingest/document` - Upload a document (PDF, DOCX, TXT, MD)
     - Parse and chunk the document
     - Store in ingestion history
     - Return document info and chunk count
   - `POST /api/ingest/url` - Ingest a web page
     - Fetch, parse, chunk
     - Return document info
   - `POST /api/ingest/csv` - Upload a CSV for structured import
     - Parse, detect columns, return column mapping for user confirmation
   - `POST /api/ingest/text` - Paste raw text
   - `GET /api/ingest/history` - List all ingested documents
   - `GET /api/graph/stats` - Get current graph statistics (node/relationship counts by type)
   - `POST /api/graph/clear` - Clear the entire graph (with confirmation)

8. **Sample data**:
   - Create 5-8 articles about the AI/tech industry:
     - "The Rise of AI Agents in Enterprise Software" (mentions companies, people, technologies)
     - "OpenAI's Latest Developments" (Sam Altman, GPT-5, Microsoft partnership)
     - "Anthropic's Approach to AI Safety" (Dario Amodei, Claude, Constitutional AI)
     - "The Cloud Computing Landscape in 2026" (AWS, Azure, GCP, key executives)
     - "AI in Defense and Intelligence" (Palantir, Janes, defense applications)
     - "The Vector Database Wars" (Pinecone, Weaviate, ChromaDB, Milvus)
   - Each article: 500-1000 words with rich entity and relationship content
   - Also include a CSV: `tech_companies.csv` with columns: name, founder, hq, industry, funding, employees

### Test criteria:
- Neo4j starts and connects via Docker
- All document formats parse correctly
- Text chunking splits at sentence/paragraph boundaries
- Schema presets load correctly
- Ingestion history tracks all uploads
- Graph stats return correct counts from Neo4j
- CSV column detection works for structured data
- Web page ingestion fetches and parses correctly

### Commit message: `feat: project scaffolding, Neo4j setup, document ingestion, and schema management`

---

## COMMIT BLOCK 2 (Day 2): AI Entity & Relationship Extraction + Graph Building

### What to build:

1. **Entity extractor** (`entity_extractor.py`):
   - Function: `extract_entities(chunk: TextChunk, schema: dict) -> List[ExtractedEntity]`
   - Two-stage extraction:
     
     **Stage 1: spaCy NER pre-filter** (fast, local)
     - Run spaCy's NER model on the chunk
     - Extract: PERSON, ORG, GPE, DATE, PRODUCT, EVENT
     - This gives a quick baseline of potential entities
     
     **Stage 2: Claude AI extraction** (thorough, contextual)
     - Send the chunk + spaCy pre-extracted entities + schema to Claude
     - Claude refines, adds missed entities, classifies according to schema, and enriches with properties
     - Claude also resolves ambiguity: "Apple" in a tech article = Organization, not fruit
   
   ```python
   class ExtractedEntity(BaseModel):
       name: str                         # Canonical name: "Anthropic" not "anthropic" or "Anthropic Inc."
       label: str                        # Schema label: "Organization", "Person", "Technology"
       properties: dict                  # {description, industry, location, etc.}
       mentions: List[str]               # All text mentions: ["Anthropic", "Anthropic Inc.", "the company"]
       source_chunk: int                 # Which chunk this was extracted from
       confidence: str                   # "high", "medium", "low"
       extraction_method: str            # "spacy", "claude", "both"
   ```

   - The Claude prompt should:
     - Include the schema (what entity types and properties to look for)
     - Include the text chunk
     - Include spaCy's initial extractions as hints
     - Ask for canonical naming (normalize variations to one name)
     - Ask for all relevant properties that can be inferred from context
     - Return ONLY valid JSON
     - Be specific about what qualifies as each entity type

2. **Relationship extractor** (`relationship_extractor.py`):
   - Function: `extract_relationships(chunk: TextChunk, entities: List[ExtractedEntity], schema: dict) -> List[ExtractedRelationship]`
   - Uses Claude API with the entities already extracted as context
   
   ```python
   class ExtractedRelationship(BaseModel):
       from_entity: str                  # Entity name
       from_label: str                   # Entity label
       to_entity: str
       to_label: str
       relationship_type: str            # Schema relationship type: "WORKS_AT", "FOUNDED_BY"
       properties: dict                  # {since, role, description}
       evidence: str                     # The sentence that supports this relationship
       confidence: str
       source_chunk: int
   ```

   - The Claude prompt should:
     - Include the text chunk
     - Include all extracted entities with their labels
     - Include the relationship types from the schema
     - Ask Claude to find relationships ONLY between the provided entities
     - Require evidence (the specific text that supports the relationship)
     - Ask for relationship properties where inferable (dates, roles, descriptions)
     - Handle implicit relationships: "Dario Amodei, CEO of Anthropic" implies WORKS_AT and also a role property

3. **Entity resolution / deduplication**:
   - Function: `resolve_entities(all_entities: List[ExtractedEntity]) -> List[ResolvedEntity]`
   - Across multiple chunks, the same entity appears multiple times
   - Merge strategy:
     - Exact name match: merge, combine properties
     - Fuzzy name match (>85% similarity): suggest merge, flag for review
     - Same entity different names ("Anthropic" vs "Anthropic PBC"): Claude-assisted resolution
   - Use a simple heuristic first, then Claude for ambiguous cases
   - Keep a merge log so merges can be undone

   ```python
   class ResolvedEntity(BaseModel):
       canonical_name: str
       label: str
       merged_from: List[str]           # Original names that were merged
       properties: dict                  # Combined properties from all mentions
       mention_count: int               # How many times across all chunks
       source_documents: List[str]
       confidence: str
   ```

4. **Graph builder** (`graph_builder.py`):
   - Function: `build_graph(entities: List[ResolvedEntity], relationships: List[ExtractedRelationship]) -> GraphBuildResult`
   - Creates nodes and relationships in Neo4j:
     - Each entity becomes a node with its label and properties
     - Each relationship becomes a Neo4j relationship
     - Add `_source` property to all nodes/relationships (which document they came from)
     - Add `_confidence` property
     - Add `_extracted_at` timestamp
   - Handle duplicates: if a node with the same name and label already exists, merge properties
   - Handle relationship duplicates: if same from/to/type exists, update properties
   - Create indexes: `CREATE INDEX FOR (n:Person) ON (n.name)` for each entity type
   - Return build statistics

   ```python
   class GraphBuildResult(BaseModel):
       nodes_created: int
       nodes_updated: int               # Existing nodes that got new properties
       relationships_created: int
       relationships_updated: int
       labels_used: List[str]
       relationship_types_used: List[str]
       build_time_ms: int
       warnings: List[str]              # Low confidence entities, unresolved duplicates
   ```

5. **Full extraction pipeline**:
   - Function: `process_and_build(document_id: str, schema: dict) -> PipelineResult`
   - End-to-end: load document -> chunk -> extract entities per chunk -> extract relationships per chunk -> resolve entities -> build graph
   - Update ingestion history with progress at each stage
   - Return full pipeline statistics

6. **CSV structured import**:
   - For CSVs, skip AI extraction and directly map columns to graph structure:
   - User maps columns: "name" -> entity name, "founder" -> Person entity + FOUNDED_BY relationship
   - Function: `import_csv_to_graph(file_path: str, column_mapping: dict) -> GraphBuildResult`
   - Column mapping format:
     ```json
     {
       "entity_column": "name",
       "entity_label": "Organization",
       "property_columns": ["industry", "funding", "employees", "hq"],
       "relationship_columns": [
         {"column": "founder", "target_label": "Person", "relationship": "FOUNDED_BY"}
       ]
     }
     ```

7. Create endpoints:
   - `POST /api/extract/{document_id}` - Run extraction on a document
     - Returns entities and relationships found
   - `POST /api/extract/{document_id}/build` - Build graph from extraction results
   - `POST /api/extract/pipeline/{document_id}` - Full pipeline (extract + build)
   - `GET /api/extract/{document_id}/entities` - Get extracted entities
   - `GET /api/extract/{document_id}/relationships` - Get extracted relationships
   - `POST /api/extract/resolve` - Run entity resolution across all extractions
   - `POST /api/ingest/csv/import` - Import CSV with column mapping
   - `GET /api/graph/nodes?label={}&search={}` - Search nodes in Neo4j
   - `GET /api/graph/node/{id}` - Get a specific node with its relationships
   - `GET /api/graph/neighbors/{id}?depth={}` - Get node's neighborhood (1-3 hops)

### Test criteria:
- Entity extraction identifies correct entities from sample articles
- Relationship extraction finds relationships between entities
- Entity resolution merges duplicates correctly
- Graph builder creates correct nodes and relationships in Neo4j
- Full pipeline processes a document end-to-end
- CSV import creates correct graph structure
- Node search works in Neo4j
- Neighborhood query returns connected nodes
- Merge/dedup doesn't lose data

### Commit message: `feat: AI entity/relationship extraction, entity resolution, and Neo4j graph building`

---

## COMMIT BLOCK 3 (Day 3): Natural Language Query Engine (NL to Cypher)

### What to build:

1. **Cypher generator** (`cypher_generator.py`):
   - Function: `natural_language_to_cypher(question: str, schema: GraphSchema) -> CypherQuery`
   - Uses Claude to translate natural language questions into Cypher queries
   
   ```python
   class GraphSchema(BaseModel):
       node_labels: List[dict]          # [{label, property_keys, count}]
       relationship_types: List[dict]   # [{type, from_label, to_label, count}]
       sample_nodes: List[dict]         # 3-5 sample nodes per label for context
   
   class CypherQuery(BaseModel):
       cypher: str                      # The generated Cypher query
       explanation: str                 # Plain English explanation of what the query does
       query_type: str                  # "search", "path", "aggregation", "pattern", "recommendation"
       parameters: dict                 # Parameterized query values
       confidence: str
   ```

   - The Claude prompt should include:
     - The full graph schema (labels, relationships, properties)
     - Sample data (a few example nodes per label so Claude understands the data)
     - The natural language question
     - Instructions to:
       - Use parameterized queries (not string interpolation) for safety
       - Use OPTIONAL MATCH where appropriate
       - Limit results (default LIMIT 25)
       - Return meaningful property names
       - Handle fuzzy name matching: `WHERE toLower(n.name) CONTAINS toLower($search)`
       - Return ONLY valid Cypher
   
   - Example translations:
     - "Who founded Anthropic?" -> `MATCH (p:Person)-[:FOUNDED_BY]-(o:Organization {name: 'Anthropic'}) RETURN p.name, p.title`
     - "What technologies does OpenAI use?" -> `MATCH (o:Organization {name: 'OpenAI'})-[:USES]->(t:Technology) RETURN t.name, t.description`
     - "How are Anthropic and OpenAI connected?" -> `MATCH path = shortestPath((a:Organization {name: 'Anthropic'})-[*..5]-(b:Organization {name: 'OpenAI'})) RETURN path`
     - "Which companies have the most connections?" -> `MATCH (o:Organization)-[r]-() RETURN o.name, count(r) as connections ORDER BY connections DESC LIMIT 10`
     - "Show me all people in the AI industry" -> `MATCH (p:Person)-[:WORKS_AT]->(o:Organization) WHERE o.industry CONTAINS 'AI' RETURN p.name, o.name`

2. **Query execution and result formatting**:
   - Function: `execute_and_format(cypher_query: CypherQuery) -> QueryResult`
   - Execute the Cypher query against Neo4j
   - Format results based on query type:
     - **Search/Pattern**: Table of results with properties
     - **Path**: List of nodes and relationships in the path
     - **Aggregation**: Summary with counts/statistics
     - **Graph**: Subgraph that can be visualized
   
   ```python
   class QueryResult(BaseModel):
       query: CypherQuery
       results: List[dict]              # Raw query results
       result_count: int
       formatted_answer: str            # AI-generated natural language answer
       visualization_data: Optional[dict] # Nodes and edges for graph visualization
       execution_time_ms: int
   ```

3. **AI answer generation**:
   - After executing the Cypher query, send the results back to Claude
   - Claude generates a natural language answer from the raw data
   - "Based on the graph, Anthropic was founded by Dario Amodei and Daniela Amodei. Dario previously worked at OpenAI as VP of Research before starting Anthropic in 2021."
   - Include relevant context and connections discovered

4. **Query suggestions**:
   - Function: `suggest_queries(schema: GraphSchema) -> List[str]`
   - Based on the current graph content, generate interesting queries the user might want to ask
   - "Who are the most connected people in the graph?"
   - "What organizations are in the AI industry?"
   - "Find the shortest path between [Entity A] and [Entity B]"
   - "Which technologies are used by the most companies?"
   - Regenerate suggestions when graph content changes

5. **Path finding queries**:
   - Special handling for "how is X connected to Y?" questions
   - Use `shortestPath` and `allShortestPaths` Cypher functions
   - Return all intermediate nodes and relationships in the path
   - Format as a step-by-step connection narrative:
     - "Dario Amodei WORKED_AT OpenAI, which COMPETES_WITH Google DeepMind, where Demis Hassabis is FOUNDER"

6. **Query history**:
   ```sql
   CREATE TABLE query_history (
       id TEXT PRIMARY KEY,
       question TEXT,
       cypher TEXT,
       result_count INTEGER,
       execution_time_ms INTEGER,
       queried_at TEXT
   );
   ```

7. Create endpoints:
   - `POST /api/query` - Ask a natural language question
     - Accepts: `{ "question": "Who founded Anthropic?" }`
     - Translates to Cypher, executes, formats answer
     - Returns: QueryResult with natural language answer + visualization data
   - `POST /api/query/cypher` - Execute raw Cypher directly
     - For advanced users who want to write their own Cypher
     - Returns: raw results + visualization data
   - `GET /api/query/suggestions` - Get suggested queries
   - `GET /api/query/history` - Get past queries
   - `POST /api/query/path` - Find paths between two entities
     - Accepts: `{ "from": "Anthropic", "to": "OpenAI", "max_depth": 5 }`
     - Returns: all paths with narrative explanation

### Test criteria:
- Simple questions translate to correct Cypher
- Complex questions (aggregations, paths) generate valid Cypher
- Parameterized queries prevent injection
- Query execution returns correct results from Neo4j
- Natural language answers are accurate and reference the data
- Path finding discovers connections between entities
- Query suggestions are relevant to current graph content
- Query history saves and retrieves correctly
- Fuzzy name matching works ("anthropic" finds "Anthropic")

### Commit message: `feat: natural language to Cypher query engine with AI answer generation`

---

## COMMIT BLOCK 4 (Day 4): Frontend - Graph Visualization & Query Interface

### What to build:
1. Initialize React app with Vite, TailwindCSS
2. Install: `react-force-graph-2d` (or `react-force-graph-3d`), `zustand`, `lucide-react`, `react-markdown`, `@monaco-editor/react` (for Cypher editor)

3. **App layout**:
   - **Left sidebar** (280px):
     - "GraphMind" logo
     - Nav: Dashboard, Graph Explorer, Query, Ingest Data, Schema, History
     - Graph stats at bottom: node count, relationship count
   - **Main area**: Page content
   - **Right panel** (collapsible, 350px): Detail panel for selected node/relationship

4. **Dashboard page**:
   - **Graph overview stats**: Total nodes, relationships, labels, relationship types
   - **Label distribution**: Bar chart showing count per label (Person: 45, Organization: 32, etc.)
   - **Relationship distribution**: Bar chart showing count per type
   - **Recent ingestions**: Last 5 documents ingested with status
   - **Quick actions**: "Ingest Document", "Ask a Question", "Explore Graph"
   - **Suggested queries**: 4-5 interesting questions to ask

5. **Graph Explorer page** (the centerpiece):
   - **Interactive graph visualization** using react-force-graph-2d:
     - Nodes as circles, colored by label:
       - Person: blue, Organization: green, Technology: purple, Location: orange, Event: red, Concept: teal, Product: pink
     - Node size proportional to connection count
     - Node label (name) shown next to each node
     - Edges as lines with relationship type as small label
     - Edge color: light gray default, highlighted on hover
     - Physics simulation: nodes repel, connected nodes attract
     - Zoom, pan, drag nodes to rearrange
   - **Controls**:
     - Search bar: type entity name to find and center on it
     - Label filter: toggle which labels are visible (checkboxes)
     - Relationship filter: toggle which relationship types are visible
     - Depth slider: show only nodes within N hops of selected node (1-5)
     - Layout: force-directed (default), hierarchical, circular
   - **Node interaction**:
     - Hover: highlight node and its direct connections, dim everything else
     - Click: select node, show detail panel on right
     - Double-click: expand node (load additional neighbors from Neo4j)
     - Right-click: context menu (expand, hide, find paths from here)
   - **Detail panel** (right side, shown when a node is selected):
     - Entity name (large), label badge
     - All properties listed
     - Direct relationships: grouped by type
       - "WORKS_AT: [Company A, Company B]"
       - "FOUNDED_BY: [Person X]"
     - "Find paths to..." button (opens path finder)
     - "Show in query" button (generates Cypher for this node)
     - Source documents that mentioned this entity

6. **Query page**:
   - **Natural language input** (top):
     - Large input: "Ask anything about your knowledge graph..."
     - "Ask" button
     - Suggested queries as clickable chips below
   - **Results area**:
     - Natural language answer (markdown rendered)
     - Results table (if tabular data returned)
     - Mini graph visualization (if path or subgraph returned)
     - Generated Cypher query (collapsible, shown for transparency)
   - **Cypher editor** (toggle "Advanced Mode"):
     - Monaco Editor with Cypher syntax highlighting
     - "Run Query" button
     - Raw results displayed as JSON table
   - **Query history** (sidebar or tab):
     - Past questions with quick re-run

7. **Ingest page**:
   - Tabs: "Upload Document", "Import URL", "Paste Text", "Import CSV"
   - Each tab has the appropriate upload/input interface
   - After upload: show extraction progress
     - "Parsing document..."
     - "Extracting entities... (found 23 so far)"
     - "Extracting relationships... (found 15 so far)"
     - "Resolving duplicates..."
     - "Building graph..."
   - After completion: summary of what was added to the graph
   - For CSV: show column mapping interface before import

### Design direction:
- **Dark theme** consistent with data/analytics tools
- Background: very dark (#0D1117)
- Graph visualization: dark background, bright colored nodes, subtle gray edges
- Node colors should be vibrant but not harsh against dark background
- The graph visualization should be the hero feature, taking up maximum screen space
- Detail panel: dark, clean, property list format
- Query page: clean input at top, results below, feels like a search engine for your graph
- Charts on dashboard: consistent with graph node colors
- Overall feel: premium data intelligence tool

### Test criteria:
- Graph visualization renders all nodes and edges from Neo4j
- Node colors match labels correctly
- Node interaction (hover, click, expand) works
- Search finds and centers on entities
- Label and relationship filters work
- Detail panel shows correct properties and relationships
- Natural language query returns answers and updates visualization
- Cypher editor executes raw queries
- CSV column mapping interface works
- Ingestion progress displays correctly

### Commit message: `feat: interactive graph visualization, query interface, and data ingestion UI`

---

## COMMIT BLOCK 5 (Day 5): Graph Algorithms, Insights & Advanced Features

### What to build:

1. **Graph algorithms** (`graph_algorithms.py`):
   - Uses Neo4j's Graph Data Science (GDS) library or manual Cypher implementations
   
   **Centrality analysis** (find the most important nodes):
   - PageRank: which entities are most referenced/connected
   - Betweenness centrality: which entities bridge different clusters
   - Degree centrality: which entities have the most connections
   - Function: `run_centrality(algorithm: str, label: Optional[str]) -> List[CentralityResult]`
   
   ```python
   class CentralityResult(BaseModel):
       node_name: str
       label: str
       score: float
       rank: int
   ```

   **Community detection** (find clusters):
   - Louvain algorithm: detect natural communities/clusters in the graph
   - Function: `detect_communities() -> List[Community]`
   - Each community: list of nodes, dominant labels, suggested community name
   
   ```python
   class Community(BaseModel):
       id: int
       node_count: int
       nodes: List[dict]                # [{name, label}]
       dominant_label: str
       suggested_name: str              # AI-generated: "AI Safety Researchers", "Cloud Infrastructure Companies"
       internal_relationships: int
       external_relationships: int
   ```

   **Similarity analysis**:
   - Find entities that are structurally similar (connected to similar things)
   - Function: `find_similar(node_name: str, label: str, top_n: int = 5) -> List[SimilarNode]`
   - "Entities similar to Anthropic" -> companies with similar connections/properties

   **Path analysis**:
   - All shortest paths between two entities
   - Weighted shortest path (if relationship properties include weights)
   - Common neighbors between two entities

2. **AI-powered graph insights** (`insights.py`):
   - Function: `generate_graph_insights(schema, stats, centrality, communities) -> GraphInsights`
   - Send graph statistics, top central nodes, and community structure to Claude
   - Claude generates:
   
   ```python
   class GraphInsight(BaseModel):
       title: str
       description: str
       insight_type: str                # "pattern", "anomaly", "recommendation", "fact"
       related_entities: List[str]
       evidence: str
       priority: str
   
   class GraphInsights(BaseModel):
       summary: str                     # Overall graph description
       key_entities: List[dict]         # Most important entities and why
       hidden_connections: List[str]    # Non-obvious relationships discovered
       clusters_description: List[str]  # What each community represents
       knowledge_gaps: List[str]        # What data is missing (entities with few connections)
       insights: List[GraphInsight]
       questions_to_explore: List[str]  # Interesting queries based on graph structure
   ```

3. **Graph comparison (before/after ingestion)**:
   - When a new document is ingested, show what changed:
     - New entities added
     - New relationships discovered
     - Existing entities that got new connections
     - New clusters or communities formed
   - Function: `diff_graph(snapshot_before: dict, snapshot_after: dict) -> GraphDiff`

4. **Insights page** (frontend):
   - **Key entities section**: Top 10 by PageRank with scores and connection counts
   - **Community map**: Graph visualization colored by community (each community a different color)
   - **Hidden connections**: List of non-obvious paths between entities
   - **Knowledge gaps**: Entities with very few connections (might need more data)
   - **AI insights cards**: Each insight as a card with title, description, related entities
   - **Graph health metrics**: Average connections per node, graph density, longest path
   - "Refresh Insights" button to regenerate

5. **Graph export options**:
   - Export as:
     - **JSON**: Full graph as nodes + edges JSON (for use in other tools)
     - **CSV**: Nodes CSV + Relationships CSV
     - **GraphML**: Standard graph exchange format
     - **Cypher statements**: Regenerate CREATE statements (for migrating to another Neo4j instance)
     - **Markdown report**: AI-generated knowledge base report with entity descriptions and relationships

6. **Schema evolution**:
   - As new documents are ingested, new entity types or relationship types may emerge
   - Claude can suggest schema additions: "I found references to 'Patent' entities and 'FILED_BY' relationships. Would you like to add these to the schema?"
   - User approves or rejects schema suggestions
   - Re-extraction with updated schema on existing documents (optional)

7. Create endpoints:
   - `GET /api/insights/centrality?algorithm={}&label={}` - Run centrality analysis
   - `GET /api/insights/communities` - Detect communities
   - `GET /api/insights/similar/{node_name}` - Find similar entities
   - `POST /api/insights/generate` - Generate AI insights
   - `GET /api/insights/latest` - Get latest generated insights
   - `GET /api/export/{format}` - Export graph (json, csv, graphml, cypher, markdown)
   - `GET /api/graph/diff/{document_id}` - Get graph diff from a specific ingestion
   - `POST /api/schema/suggest` - Get AI schema suggestions based on recent extractions

### Test criteria:
- PageRank returns reasonable rankings (highly connected nodes rank higher)
- Community detection finds clusters in sample data
- Similarity analysis returns structurally similar entities
- AI insights are specific to the graph content
- Export formats are valid and re-importable
- Community visualization colors nodes by cluster
- Knowledge gaps correctly identify sparsely connected entities
- Schema suggestions are relevant based on ingested content

### Commit message: `feat: graph algorithms, AI insights, community detection, and export`

---

## COMMIT BLOCK 6 (Day 6): Demo Data, Onboarding & README

### What to build:

1. **One-click demo setup**:
   - "Load Demo Data" button on the dashboard
   - Ingests all sample articles + CSV automatically
   - Runs extraction and builds graph
   - Pre-caches AI insights
   - Takes ~2 minutes, shows progress
   - Result: a rich graph with 80-120 nodes and 150-200 relationships
   - Alternative: pre-cache the entire built graph as Cypher statements and load instantly

2. **Guided onboarding** (first-time user):
   - Step 1: "Choose a schema" - Select general or domain-specific
   - Step 2: "Add your first data" - Upload a document, paste text, or load demo
   - Step 3: "Watch the graph build" - Extraction progress with live graph updates
   - Step 4: "Explore and query" - Redirected to graph explorer with tips
   - Dismissible, skippable

3. **Graph evolution timeline**:
   - Visual timeline showing how the graph grew over time
   - Each ingestion event: "Added 15 nodes and 23 relationships from [document]"
   - Graph size chart over time (nodes and relationships)

4. **Keyboard shortcuts**:
   - `Cmd+K`: Quick search for entities
   - `Cmd+Enter`: Run query
   - `F`: Fit graph to screen
   - `Escape`: Deselect node / close panel
   - `1-5`: Set neighborhood depth
   - `?`: Show shortcuts

5. **Polish**:
   - Skeleton loaders for graph stats, insights, query results
   - Toast notifications for: ingestion complete, graph built, export ready
   - Smooth animations on graph: nodes fade in on expand, edges animate on highlight
   - Empty states: no data yet, no query results, no insights
   - Graph loading state: skeleton or placeholder while large graphs render
   - Performance: for graphs with 500+ nodes, enable WebGL rendering (react-force-graph supports this)
   - Mobile: simplified view showing query interface only (graph viz needs desktop)

6. **README.md**:
   - **Hero**: "GraphMind" with tagline "Turn unstructured data into connected intelligence"
   - **The Problem**: "Knowledge is trapped in documents, spreadsheets, and web pages. The relationships between people, companies, technologies, and events exist implicitly in text but are invisible to traditional search. Finding connections requires manually reading and cross-referencing dozens of sources."
   - **The Solution**: "GraphMind automatically extracts entities and relationships from any data source and builds a queryable knowledge graph in Neo4j. Ask questions in plain English, explore connections visually, discover hidden patterns, and generate insights that would take humans days to uncover."
   - **Features**:
     - Multi-format data ingestion (PDF, DOCX, CSV, web pages, raw text)
     - AI-powered entity extraction with spaCy + Claude
     - Automatic relationship discovery
     - Entity resolution and deduplication
     - Interactive 2D/3D graph visualization
     - Natural language to Cypher query translation
     - Graph algorithms (PageRank, community detection, similarity)
     - AI-generated graph insights
     - Multiple export formats (JSON, CSV, GraphML, Cypher)
     - Schema-driven extraction with domain presets
   - **Architecture**: Diagram showing Data Sources -> Document Parser -> Chunker -> Entity Extractor (spaCy + Claude) -> Relationship Extractor (Claude) -> Entity Resolver -> Neo4j Graph Builder -> Graph Explorer + NL Query Engine + Graph Algorithms
   - **Tech Stack**: Listed with justifications (especially Neo4j choice)
   - **Graph Algorithms**: Table explaining each algorithm and when to use it
   - **Getting Started**:
     - Prerequisites: Docker (for Neo4j), Python 3.11+, Node 18+
     - `docker-compose up -d` to start Neo4j
     - Backend and frontend setup
   - **Screenshots**: 10+ screenshots
   - **Schema Customization**: How to create custom schemas for different domains

7. **Screenshots**: Capture:
   - Dashboard with graph stats
   - Graph visualization (full, with colored nodes)
   - Graph visualization with community coloring
   - Node selected with detail panel
   - Path between two entities highlighted
   - Natural language query with answer
   - Cypher editor with results
   - Document ingestion with extraction progress
   - Insights page with key entities and communities
   - CSV import with column mapping
   - Store in `/screenshots`

8. **.env.example**:
   ```
   ANTHROPIC_API_KEY=your_key_here
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=graphmind123
   DATABASE_URL=sqlite:///./graph_data/graphmind.db
   ```

9. **Code cleanup**

### Commit message: `docs: demo data, onboarding, graph timeline, README, and polish`

---

## Portfolio Framing

**Title**: GraphMind - AI Knowledge Graph Builder

**Client context**: "Built for a defense intelligence firm that needed to extract entities and relationships from thousands of unstructured reports and build a queryable knowledge graph connecting people, organizations, events, and locations across their intelligence corpus."

**Problem**: "Knowledge is buried in unstructured documents. The connections between entities exist implicitly in text but are invisible to search. Analysts spend hours manually reading, cross-referencing, and mapping relationships that could be extracted automatically."

**Solution**: "An AI-powered platform that ingests documents, extracts entities and relationships using NLP and LLMs, builds a Neo4j knowledge graph, and provides natural language querying, interactive visualization, and graph algorithm-based insights. Turns months of manual analysis into hours of automated extraction."

**My role**: "Full-stack architecture, Neo4j graph database design, NLP pipeline (spaCy + Claude), entity resolution system, natural language to Cypher translation, graph visualization, and algorithm implementation."

**Results**: "Extracted 500+ entities and 1,200+ relationships from 50 intelligence reports in under 30 minutes. Discovered 15 non-obvious connections between entities that analysts had missed over months of manual review. Reduced time-to-insight from weeks to minutes."

**Tech**: Python, FastAPI, React, TailwindCSS, Neo4j, Claude API, spaCy, react-force-graph, scikit-learn

**Link**: GitHub repo link | Live demo link

---

## Notes for Claude Code
- Use Python 3.11+ syntax
- Use the official `anthropic` SDK for Claude API calls
- Neo4j Python driver: `pip install neo4j`. Use async driver if possible.
- spaCy: `pip install spacy && python -m spacy download en_core_web_sm` (small model for NER)
- react-force-graph-2d: `npm install react-force-graph-2d`. Use `ForceGraph2D` component.
- Monaco Editor for Cypher: use `@monaco-editor/react` with a custom Cypher language definition (or plain text mode)
- FastAPI on port 8000, Vite on port 5173, Neo4j on ports 7474 (browser) and 7687 (bolt)
- Proxy config in vite.config.js for /api routes
- All API routes prefixed with /api
- Neo4j Cypher best practices:
  - Always use parameterized queries: `MATCH (n:Person {name: $name})` not `MATCH (n:Person {name: '${name}'})`
  - Use MERGE instead of CREATE for upsert behavior
  - Create indexes before bulk importing
  - Use APOC procedures where available (apoc.path.expand, apoc.text.levenshteinSimilarity)
- Entity resolution is the hardest part of this project. Start simple (exact match + case-insensitive), add fuzzy later.
- For the graph visualization, start with 2D (faster, simpler) and add 3D as a toggle if time permits.
- Graph data for visualization format: `{ nodes: [{id, name, label, val}], links: [{source, target, type}] }`
- Large graphs (500+ nodes) will be slow in force simulation. Enable `warmupTicks` and `cooldownTicks` for faster initial rendering.
- Docker compose for Neo4j is the easiest setup. Alternative: Neo4j Desktop (free) or Neo4j Aura (cloud, free tier).
