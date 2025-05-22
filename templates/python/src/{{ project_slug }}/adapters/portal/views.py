"""View helpers for the portal adapter.

Portal views convert summary payloads into HTML pages. Keeping rendering in this
module keeps HTTP routes small and makes page output easier to test.
"""

from html import escape


def render_index(summary: dict[str, object]) -> str:
    """Render the portal landing page.

    Parameters
    ----------
    summary : dict[str, object]
        Portal summary payload.

    Returns
    -------
    str
        HTML portal page.
    """
    # Escape dynamic record content before inserting it into HTML.
    records = "".join(
        "<li>"
        f"<strong>{escape(record['label'])}</strong>: "
        f"{escape(record['description'])}"
        "</li>"
        for record in summary["records"]
    )
    return (
        "<!doctype html>"
        "<html lang=\"en\">"
        "<head><title>{{ (project_name or project_slug) }} portal</title></head>"
        "<body>"
        "<main>"
        f"<h1>{escape(str(summary['title']))}</h1>"
        f"<p>{escape(str(summary['output_text']))}</p>"
        f"<ul>{records}</ul>"
        "</main>"
        "</body>"
        "</html>"
    )
