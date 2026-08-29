"""Index routes for the portal adapter.

The index route renders the main human-facing portal page from a summary
payload.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from {{ project_slug }}.adapters.portal.summary import portal_summary
from {{ project_slug }}.adapters.portal.views import render_index


router = APIRouter(tags=["portal"])


@router.get("/", response_class=HTMLResponse)
def index() -> str:
    """Render the portal landing page.

    Returns
    -------
    str
        HTML portal page.
    """
    return render_index(portal_summary())
