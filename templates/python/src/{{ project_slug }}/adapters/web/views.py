"""View helpers for the web application adapter.

View helpers prepare HTML responses for human-facing pages. They are separated
from routes so rendering can be tested without running an HTTP server.
"""

from html import escape

from {{ project_slug }}.services.processing import process_text


def render_index(text: str = "{{ (project_name or project_slug) }}") -> str:
    """Render the application landing page.

    Parameters
    ----------
    text : str, default="{{ (project_name or project_slug) }}"
        Text to process for display.

    Returns
    -------
    str
        HTML landing page.
    """
    # Escape dynamic text before inserting it into HTML.
    result = process_text(text)
    return (
        "<!doctype html>"
        "<html lang=\"en\">"
        "<head><title>{{ (project_name or project_slug) }}</title></head>"
        "<body>"
        "<main>"
        "<h1>{{ (project_name or project_slug) }}</h1>"
        f"<p>{escape(result.output_text)}</p>"
        "</main>"
        "</body>"
        "</html>"
    )
