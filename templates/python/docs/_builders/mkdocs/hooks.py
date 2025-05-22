"""Populate MkDocs configuration from generated project metadata.

CodeMeta is preferred when selected. PEP 621 package metadata provides the
same core values when the optional metadata files are absent.
"""

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEMETA_PATH = ROOT / "codemeta.json"
PYPROJECT_PATH = ROOT / "pyproject.toml"


def load_project_metadata():
    """Load public project metadata from CodeMeta or PEP 621.

    Returns
    -------
    dict
        Normalized metadata used by the MkDocs configuration.
    """
    if CODEMETA_PATH.exists():
        return json.loads(CODEMETA_PATH.read_text(encoding="utf-8"))

    pyproject = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    project = pyproject["project"]
    urls = project.get("urls", {})
    return {
        "name": project["name"],
        "description": project.get("description", ""),
        "codeRepository": urls.get("Source Code", ""),
    }


def on_config(config):
    """Apply CodeMeta values to MkDocs configuration.

    Parameters
    ----------
    config : mkdocs.config.defaults.MkDocsConfig
        Mutable MkDocs configuration.

    Returns
    -------
    mkdocs.config.defaults.MkDocsConfig
        Updated configuration.
    """
    project_metadata = load_project_metadata()
    config["site_name"] = project_metadata["name"]
    config["site_description"] = project_metadata.get("description", "")

    repository_url = project_metadata.get("codeRepository", "")
    if repository_url:
        config["repo_url"] = repository_url
        config["repo_name"] = repository_url.rstrip("/").rsplit("/", 1)[-1]

    return config
