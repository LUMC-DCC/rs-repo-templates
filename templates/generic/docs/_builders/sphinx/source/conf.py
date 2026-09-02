"""Configure language-neutral Sphinx documentation.

The configuration uses rendered project context directly, so documentation
does not depend on a package manifest or an importable implementation.
"""

from datetime import date

project = {{ (project_name or project_slug) | tojson }}
author = {{ ((project_name or project_slug) ~ " contributors") | tojson }}
copyright = f"{date.today().year}, {author}"
release = {{ (versioning.version or "0.1.0") | tojson }}

extensions = [
    # Allow documentation pages to be written in Markdown.
    "myst_parser",
]

exclude_patterns = ["build"]
html_theme = "sphinx_book_theme"
html_title = project
html_theme_options = {
    # Show nested headings in the right-hand page table of contents.
    "show_toc_level": 2,
    # Keep the starter theme focused on the documentation.
    "use_download_button": False,
    "use_fullscreen_button": False,
}
{% if urls.repository %}
# Add a repository button when a public source URL is available.
html_theme_options["repository_url"] = {{ urls.repository | tojson }}
html_theme_options["use_repository_button"] = True
{% endif %}
