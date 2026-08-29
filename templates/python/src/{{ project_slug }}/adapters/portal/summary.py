"""Portal-facing summary helpers for {{ (project_name or project_slug) }}.

Summary helpers combine service output and repository records into payloads
that routes or views can render.
"""

from {{ project_slug }}.adapters.portal.repository import PortalRepository
from {{ project_slug }}.services.processing import process_text


def portal_summary(
    text: str = "{{ (project_name or project_slug) }}",
    repository: PortalRepository | None = None,
) -> dict[str, object]:
    """Build a portal summary payload.

    Parameters
    ----------
    text : str, default="{{ (project_name or project_slug) }}"
        Text to process for display.
    repository : PortalRepository | None, optional
        Repository that provides portal records.

    Returns
    -------
    dict[str, object]
        Portal summary payload.
    """
    # Create a default repository only when one is not supplied, which keeps the
    # function easy to test with custom records.
    result = process_text(text)
    records = (repository or PortalRepository()).list_records()
    return {
        "title": "{{ (project_name or project_slug) }}",
        "input_text": result.input_text,
        "output_text": result.output_text,
        "records": [record.__dict__ for record in records],
    }
