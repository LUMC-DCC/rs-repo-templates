"""Record routes for the portal adapter.

Record routes expose structured portal data for clients that need JSON instead
of the rendered HTML page.
"""

from fastapi import APIRouter

from {{ project_slug }}.adapters.portal.summary import portal_summary


router = APIRouter(tags=["portal"])


@router.get("/records")
def records() -> list[dict[str, str]]:
    """Return portal records.

    Returns
    -------
    list[dict[str, str]]
        Portal records.
    """
    # Reuse the same summary builder as the HTML page so both views stay in
    # sync.
    return portal_summary()["records"]
