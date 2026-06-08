from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.neo4j_client import neo4j_client

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/stats")
async def get_graph_stats():
    try:
        return neo4j_client.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {e}")


@router.get("/schema")
async def get_graph_schema():
    try:
        return neo4j_client.get_schema()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {e}")


@router.get("/full")
async def get_full_graph(limit: int = Query(default=500, le=2000)):
    try:
        return neo4j_client.get_full_graph(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {e}")


@router.get("/nodes")
async def search_nodes(
    label: Optional[str] = None,
    search: str = Query(default=""),
):
    try:
        return neo4j_client.search_nodes(label, search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {e}")


@router.get("/node/{node_id}")
async def get_node(node_id: str):
    try:
        node = neo4j_client.get_node_with_relationships(node_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {e}")
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.get("/neighbors/{node_id}")
async def get_neighbors(node_id: str, depth: int = Query(default=1, ge=1, le=5)):
    try:
        return neo4j_client.get_neighbors(node_id, depth)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {e}")


@router.post("/clear")
async def clear_graph():
    try:
        neo4j_client.clear_graph()
        return {"message": "Graph cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {e}")
