from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.neo4j_client import neo4j_client
from backend.routers import (
    ingest, graph, extract, query, insights, export, demo,
    advanced_query, annotations, feed, ws, diff,
    entity_timeline, anomaly, multilang, rss, wikipedia,
    email_ingest, temporal, influence, predictions, gaps,
    views, reports, vectors, audit,
)
from backend.routers import scheduler as scheduler_router
from backend.routers import watchlist as watchlist_router
from backend.routers import workspaces as workspaces_router
from backend.routers import auth as auth_router
from backend.routers import schema as schema_router
from backend.routers import schema_evolution as schema_evolution_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        neo4j_client.connect()
    except Exception as e:
        print(f"Warning: Could not connect to Neo4j: {e}")
        print("Neo4j features will be unavailable until the database is started.")
    yield
    neo4j_client.close()


app = FastAPI(
    title="GraphMind",
    description="AI Knowledge Graph Builder - Turn unstructured data into connected intelligence",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(graph.router)
app.include_router(schema_router.router)
app.include_router(extract.router)
app.include_router(query.router)
app.include_router(advanced_query.router)
app.include_router(insights.router)
app.include_router(export.router)
app.include_router(demo.router)
app.include_router(annotations.router)
app.include_router(feed.router)
app.include_router(scheduler_router.router)
app.include_router(watchlist_router.router)
app.include_router(workspaces_router.router)
app.include_router(auth_router.router)
app.include_router(diff.router)
app.include_router(ws.router)
app.include_router(entity_timeline.router)
app.include_router(anomaly.router)
app.include_router(schema_evolution_router.router)
app.include_router(multilang.router)
app.include_router(rss.router)
app.include_router(wikipedia.router)
app.include_router(email_ingest.router)
app.include_router(temporal.router)
app.include_router(influence.router)
app.include_router(predictions.router)
app.include_router(gaps.router)
app.include_router(views.router)
app.include_router(reports.router)
app.include_router(vectors.router)
app.include_router(audit.router)


@app.get("/api/health")
async def health_check():
    neo4j_status = "disconnected"
    try:
        neo4j_client.get_stats()
        neo4j_status = "connected"
    except Exception:
        pass

    return {
        "status": "ok",
        "neo4j": neo4j_status,
        "version": "0.3.0",
    }
