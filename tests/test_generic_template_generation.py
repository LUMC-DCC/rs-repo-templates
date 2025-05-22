"""Generation tests for the language-agnostic Copier template.

The tests verify the neutral repository backbone, reusable public files, and
builder-specific documentation without asserting language implementation code.
"""

from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from copier import run_copy

ROOT = Path(__file__).resolve().parents[1]
COPIER_SOURCE = ROOT

RICH_CONTEXT = {
    "project_name": "Research Backbone",
    "project_slug": "research-backbone",
    "project_short_description": "A language-neutral research software repository.",
    "project_long_description": (
        "A reusable foundation for metadata, documentation, and collaboration."
    ),
    "versioning": {
        "version": "0.1.0",
        "scheme": "SemVer",
        "scheme_details": "",
        "release_frequency": "On demand (irregular/as needed)",
    },
    "contributors": {
        "entries": [
            {
                "name": "Ada Lovelace",
                "given_names": "Ada",
                "family_names": "Lovelace",
                "email": "ada@example.org",
                "roles": ["Original author", "Maintainer"],
            }
        ]
    },
    "urls": {
        "repository": "https://github.com/LUMC-DCC/research-backbone",
        "homepage": "",
        "documentation": "https://lumc-dcc.github.io/research-backbone",
    },
    "include_metadata": True,
    "access": {
        "type": "free-with-restrictions",
        "details": "https://example.org/research-backbone/access",
    },
    "community_files": {
        "entries": [
            "CHANGELOG.md",
            "CODE_OF_CONDUCT.md",
            "CONTRIBUTING.md",
            "GOVERNANCE.md",
            "SECURITY.md",
            "SUPPORT.md",
        ]
    },
    "code_review_policy": "At least **two reviewers** must approve each change.",
    "support_routes": {
        "entries": [
            {
                "system": "GitHub Issues",
                "url": "https://github.com/LUMC-DCC/research-backbone/issues",
            }
        ]
    },
    "contacts": {
        "code_of_conduct": "community@example.org",
        "community": "community@example.org",
        "security": "security@example.org",
    },
    "licensing": {
        "license": "Institutional research license\n\nPermission terms go here.",
        "compatibility_check": "Yes - automated tooling",
    },
}


@pytest.fixture(scope="session")
def generic_copier_source(tmp_path_factory):
    """Create one non-Git source copy for generic generation tests.

    Parameters
    ----------
    tmp_path_factory : pytest.TempPathFactory
        Factory for the isolated template source.

    Returns
    -------
    pathlib.Path
        Copier source containing configuration, tasks, and all scaffolds.
    """
    source = tmp_path_factory.mktemp("generic-copier-source")
    for directory in ("_config", "_copier_tasks", "templates"):
        shutil.copytree(ROOT / directory, source / directory)
    shutil.copy2(ROOT / "copier.yml", source / "copier.yml")
    return source


def finalize_generic_project(project_path: Path) -> None:
    """Run shared finalization for a rendered generic project.

    Parameters
    ----------
    project_path
        Rendered repository root.
    """
    task_root = ROOT / "_copier_tasks"
    sys.path.insert(0, str(task_root))
    try:
        finalize_module = importlib.import_module("finalize")
        finalize_module.finalize(project_path, "generic")
    finally:
        sys.path.remove(str(task_root))


def render_generic_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    generic_copier_source: Path,
    **overrides,
) -> Path:
    """Render and finalize one generic project.

    Parameters
    ----------
    tmp_path
        Pytest temporary directory.
    monkeypatch
        Fixture used to isolate Copier user configuration.
    generic_copier_source
        Isolated template source.
    **overrides
        Context values overriding the rich representative context.

    Returns
    -------
    pathlib.Path
        Generated repository root.
    """
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    context = RICH_CONTEXT | overrides
    project_path = tmp_path / "generated" / context["project_slug"]
    run_copy(
        str(generic_copier_source),
        project_path,
        data={"template_type": "generic"} | context,
        defaults=True,
        overwrite=True,
        quiet=True,
        unsafe=True,
        skip_tasks=True,
    )
    finalize_generic_project(project_path)
    return project_path


def test_generic_default_context_generates_neutral_backbone(
    tmp_path,
    monkeypatch,
    generic_copier_source,
):
    """Ensure untouched defaults generate only universal repository files."""
    project_path = render_generic_project(
        tmp_path,
        monkeypatch,
        generic_copier_source,
        project_name="",
        project_short_description="",
        project_long_description="",
        include_metadata=False,
        community_files={"entries": []},
        support_routes={"entries": []},
        contacts={"code_of_conduct": "", "community": "", "security": ""},
        licensing={"license": "", "compatibility_check": ""},
        documentation_types={"entries": []},
        documentation_builder="",
    )

    for rel_path in (
        ".copier-answers.yml",
        ".editorconfig",
        ".gitattributes",
        ".gitignore",
        ".pre-commit-config.yaml",
        ".github/dependabot.yml",
        ".github/workflows/repository.yml",
        "README.md",
    ):
        assert (project_path / rel_path).is_file(), rel_path

    editorconfig = (project_path / ".editorconfig").read_text(encoding="utf-8")
    assert editorconfig.startswith("root = true\n")

    for rel_path in (
        "CITATION.cff",
        "biotools.json",
        "codemeta.json",
        "LICENSE",
        "docs",
        "src",
        "tests",
        "pyproject.toml",
        "tools",
        ".github/workflows/metadata.yml",
        ".github/workflows/changelog.yml",
        ".github/workflows/docs.yml",
    ):
        assert not (project_path / rel_path).exists(), rel_path


def test_generic_biotools_registry_generates_registry_metadata(
    tmp_path,
    monkeypatch,
    generic_copier_source,
):
    """Ensure bio.tools metadata is independent of the minimum metadata set."""
    project_path = render_generic_project(
        tmp_path,
        monkeypatch,
        generic_copier_source,
        include_metadata=False,
        registries={
            "entries": [{"name": "bio.tools", "url_or_id": "research-backbone"}]
        },
    )

    metadata = json.loads((project_path / "biotools.json").read_text())
    assert metadata[0]["biotoolsID"] == "research-backbone"
    assert metadata[0]["name"] == "Research Backbone"
    assert "license" not in metadata[0]
    assert not (project_path / "codemeta.json").exists()


def test_generic_rich_context_generates_public_backbone(
    tmp_path,
    monkeypatch,
    generic_copier_source,
):
    """Ensure selected reusable files and neutral workflows compose together."""
    project_path = render_generic_project(
        tmp_path,
        monkeypatch,
        generic_copier_source,
        documentation_types={"entries": ["user", "deployment", "developer"]},
        documentation_builder="zensical",
    )

    for rel_path in (
        "CITATION.cff",
        "codemeta.json",
        "LICENSE",
        "CHANGELOG.md",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "GOVERNANCE.md",
        "SECURITY.md",
        "SUPPORT.md",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/pull_request_template.md",
        ".github/workflows/repository.yml",
        ".github/workflows/metadata.yml",
        ".github/workflows/changelog.yml",
        ".github/workflows/docs.yml",
        "tools/check_changelog.py",
        "docs/developer.md",
        "docs/reference.md",
        "docs/requirements.txt",
        "zensical.toml",
    ):
        assert (project_path / rel_path).is_file(), rel_path

    for rel_path in ("pyproject.toml", "src", "tests", "Dockerfile"):
        assert not (project_path / rel_path).exists(), rel_path

    developer_docs = (project_path / "docs" / "developer.md").read_text(
        encoding="utf-8"
    )
    assert "## Architecture" in developer_docs
    assert "## Code review" in developer_docs
    assert "@@DOCS_" not in developer_docs

    legal_docs = (project_path / "docs" / "legal.md").read_text(encoding="utf-8")
    assert "Configure a compatible checker" in legal_docs
    assert "checked automatically in CI" not in legal_docs

    readme = (project_path / "README.md").read_text(encoding="utf-8")
    overview = (project_path / "docs" / "overview.md").read_text(encoding="utf-8")
    contributing = (project_path / "CONTRIBUTING.md").read_text(encoding="utf-8")
    pull_request = (project_path / ".github" / "pull_request_template.md").read_text(
        encoding="utf-8"
    )
    codemeta = json.loads((project_path / "codemeta.json").read_text(encoding="utf-8"))
    for heading in (
        "## Purpose",
        "## Intended Audience",
        "## Installation",
        "## Usage",
        "## Citation",
        "## Support",
    ):
        assert heading in readme
    assert "## Access" in readme
    assert "Free with restrictions" in overview
    assert "## Code review" in contributing
    assert RICH_CONTEXT["code_review_policy"] in contributing
    assert "code-review policy in `CONTRIBUTING.md`" in pull_request
    assert codemeta["isAccessibleForFree"] is True
    assert codemeta["schema:usageInfo"] == RICH_CONTEXT["access"]["details"]


@pytest.mark.parametrize("builder", ["plain", "mkdocs", "zensical", "sphinx"])
def test_generic_documentation_builders_produce_valid_output(
    tmp_path,
    monkeypatch,
    generic_copier_source,
    builder,
):
    """Render every generic documentation strategy and build static variants."""
    selected_builder = "" if builder == "plain" else builder
    project_path = render_generic_project(
        tmp_path,
        monkeypatch,
        generic_copier_source,
        documentation_types={"entries": ["user", "deployment", "developer"]},
        documentation_builder=selected_builder,
        community_files={"entries": []},
        licensing={"license": "", "compatibility_check": ""},
    )

    if builder == "plain":
        assert (project_path / "docs" / "index.md").is_file()
        assert not (project_path / "docs" / "requirements.txt").exists()
        assert not (project_path / ".github" / "workflows" / "docs.yml").exists()
        return

    commands = {
        "mkdocs": [sys.executable, "-m", "mkdocs", "build", "--strict"],
        "zensical": [shutil.which("zensical"), "build", "--strict"],
        "sphinx": [
            sys.executable,
            "-m",
            "sphinx",
            "-W",
            "-b",
            "html",
            "docs/source",
            "docs/build/html",
        ],
    }
    result = subprocess.run(
        commands[builder],
        cwd=project_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
