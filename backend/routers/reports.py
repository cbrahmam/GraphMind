from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse
from backend.services.pdf_reporter import generate_text_report, generate_json_report, generate_html_report

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/text")
async def get_text_report():
    try:
        report = generate_text_report()
        return PlainTextResponse(content=report, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/json")
async def get_json_report():
    try:
        return generate_json_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/html")
async def get_html_report():
    try:
        html = generate_html_report()
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
