from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.graphql_layer import flexible_query, introspect_schema

router = APIRouter(prefix="/api/flex", tags=["Flexible Query"])


class FlexQuery(BaseModel):
    node_types: list[str] | None = None
    relationship_types: list[str] | None = None
    properties: dict | None = None
    limit: int = 50
    offset: int = 0
    order_by: str | None = None
    include_relationships: bool = True


@router.post("/query")
async def flex_query(req: FlexQuery):
    try:
        return flexible_query(
            node_types=req.node_types,
            relationship_types=req.relationship_types,
            properties=req.properties,
            limit=min(req.limit, 200),
            offset=req.offset,
            order_by=req.order_by,
            include_relationships=req.include_relationships,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema")
async def get_schema():
    try:
        return introspect_schema()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
