from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

here = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(here / "templates"))
router = APIRouter(tags=["admin"])


@router.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request) -> HTMLResponse:
    # Starlette ≥0.45: TemplateResponse(request, name, context=...)
    return templates.TemplateResponse(request, "admin.html")
