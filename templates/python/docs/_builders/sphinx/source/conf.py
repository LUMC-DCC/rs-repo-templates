"""Configure Sphinx from generated project metadata.

CodeMeta is preferred when selected. PEP 621 package metadata provides the
same core values when the optional metadata files are absent.
"""

import json
import sys
import tomllib
from datetime import date
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODEMETA_PATH = ROOT / "codemeta.json"
PYPROJECT_PATH = ROOT / "pyproject.toml"

{% set interface_types = namespace(values=[]) -%}
{% for interface in interfaces.entries -%}
{% if interface.type is defined and interface.type -%}
{% set _ = interface_types.values.append(interface.type) -%}
{% endif -%}
{% endfor -%}
{% set mocked_imports = [] -%}
{% if "Command-line tool" in interface_types.values -%}
{% set _ = mocked_imports.append("typer") -%}
{% endif -%}
{% if "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values or "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values or "Web application" in interface_types.values or "Workbench" in interface_types.values or "Web service" in interface_types.values -%}
{% set _ = mocked_imports.append("fastapi") -%}
{% endif -%}
{% if "Ontology" in interface_types.values or "SPARQL endpoint" in interface_types.values -%}
{% set _ = mocked_imports.append("rdflib") -%}
{% endif -%}
{% if "Web service" in interface_types.values -%}
{% set _ = mocked_imports.append("a2wsgi") -%}
{% set _ = mocked_imports.append("lxml") -%}
{% set _ = mocked_imports.append("spyne") -%}
{% endif -%}


def load_project_metadata():
    """Load normalized public metadata for Sphinx.

    Returns
    -------
    dict
        Project name, version, authors, and repository URL.
    """
    if CODEMETA_PATH.exists():
        codemeta = json.loads(CODEMETA_PATH.read_text(encoding="utf-8"))
        authors = [
            entry.get("name", "")
            for entry in codemeta.get("author", [])
            if isinstance(entry, dict) and entry.get("name")
        ]
        return {
            "name": codemeta["name"],
            "version": codemeta["version"],
            "authors": authors,
            "repository": codemeta.get("codeRepository", ""),
        }

    pyproject = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    project_data = pyproject["project"]
    return {
        "name": project_data["name"],
        "version": project_data["version"],
        "authors": [author["name"] for author in project_data.get("authors", [])],
        "repository": project_data.get("urls", {}).get("Source Code", ""),
    }


PROJECT_METADATA = load_project_metadata()

# Allow autodoc to import the package from an editable source checkout.
sys.path.insert(0, str(ROOT / "src"))

project = PROJECT_METADATA["name"]
author = ", ".join(PROJECT_METADATA["authors"])
copyright = f"{date.today().year}, {author}"
try:
    release = metadata.version("{{ project_slug | replace('_', '-') }}")
except metadata.PackageNotFoundError:
    # Source checkouts can build docs before the package is installed.
    release = PROJECT_METADATA["version"]

extensions = [
    # Import docstrings from Python modules.
    "sphinx.ext.autodoc",
    # Render NumPy- and Google-style docstrings.
    "sphinx.ext.napoleon",
    # Link documented objects back to highlighted source code.
    "sphinx.ext.viewcode",
    # Allow Sphinx pages to be written in Markdown with MyST directives.
    "myst_parser",
]

# Optional interface libraries are not required merely to build API docs.
autodoc_mock_imports = {{ mocked_imports | tojson }}

exclude_patterns = []

html_theme = "sphinx_book_theme"
html_title = project
html_theme_options = {
    # Show nested headings in the right-hand page table of contents.
    "show_toc_level": 2,
    # Keep the starter theme quiet and focused.
    "use_download_button": False,
    "use_fullscreen_button": False,
}
repository_url = PROJECT_METADATA["repository"]
if repository_url and "REPLACE_WITH" not in repository_url:
    # Add a repository button when a public repository URL is available.
    html_theme_options["repository_url"] = repository_url
    html_theme_options["use_repository_button"] = True
