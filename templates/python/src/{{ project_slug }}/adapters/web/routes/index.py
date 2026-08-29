"""Index routes for the web application adapter.

Routes own URL paths and HTTP response types. Rendering details live in view
helpers so they can be tested directly.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from {{ project_slug }}.adapters.web.views import render_index


router = APIRouter(tags=["web"])


@router.get("/", response_class=HTMLResponse)
def index() -> str:
    """Render the application landing page.

    Returns
    -------
    str
        HTML landing page.
    """
    return render_index()
