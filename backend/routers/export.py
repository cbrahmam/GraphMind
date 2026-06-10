from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

from backend.services.graph_exporter import (
    export_json,
    export_csv,
    export_graphml,
    export_cypher,
    export_markdown,
)

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/{format}")
async def export_graph(format: str):
    try:
        if format == "json":
            data = export_json()
            return PlainTextResponse(data, media_type="application/json", headers={
                "Content-Disposition": "attachment; filename=graphmind_export.json"
            })
        elif format == "csv":
            data = export_csv()
            return JSONResponse({
                "nodes_csv": data["nodes_csv"],
                "relationships_csv": data["relationships_csv"],
            })
        elif format == "graphml":
            data = export_graphml()
            return PlainTextResponse(data, media_type="application/xml", headers={
                "Content-Disposition": "attachment; filename=graphmind_export.graphml"
            })
        elif format == "cypher":
            data = export_cypher()
            return PlainTextResponse(data, media_type="text/plain", headers={
                "Content-Disposition": "attachment; filename=graphmind_export.cypher"
            })
        elif format == "markdown":
            data = export_markdown()
            return PlainTextResponse(data, media_type="text/markdown", headers={
                "Content-Disposition": "attachment; filename=graphmind_report.md"
            })
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}. Use json, csv, graphml, cypher, or markdown.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")
