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

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
exclude_patterns = ["_build"]

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

html_theme = "sphinx_book_theme"
html_title = project
html_theme_options = {
    # Show nested headings in the right-hand page table of contents.
    "show_toc_level": 2,
    "navigation_with_keys": False,
    # Keep the starter theme focused on the documentation.
    "use_download_button": False,
    "use_fullscreen_button": False,
}
{% if urls.repository %}
# Add a repository button when a public source URL is available.
html_theme_options["repository_url"] = {{ urls.repository | tojson }}
html_theme_options["repository_branch"] = "main"
html_theme_options["path_to_docs"] = "docs"
html_theme_options["use_repository_button"] = True
html_theme_options["use_issues_button"] = True
html_theme_options["use_edit_page_button"] = True
html_theme_options["use_source_button"] = True
{% endif %}
