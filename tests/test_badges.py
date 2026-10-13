"""Focused regression tests for metadata-driven README badges."""

from __future__ import annotations

import importlib
from pathlib import Path
from urllib.parse import unquote

import pytest

TASKS = Path(__file__).resolve().parents[1] / "_copier_tasks"


@pytest.fixture
def badges(monkeypatch):
    """Import the source-side renderer without changing global import paths."""
    monkeypatch.syspath_prepend(str(TASKS))
    return importlib.import_module("renderers.badges")


@pytest.mark.parametrize("path", ["docs/usage.md", "docs/source/usage.md"])
@pytest.mark.parametrize("template", ["generic", "python", "r"])
def test_usage_badge_links_to_existing_guide(badges, tmp_path, path, template):
    """User guides are discoverable even before publishing a docs site."""
    guide = tmp_path / path
    guide.parent.mkdir(parents=True)
    guide.write_text("# Usage\n", encoding="utf-8")
    ctx = {
        "_template_name": template,
        "documentation_types": {"entries": ["user"]},
        "urls": {"repository": "https://github.com/example/project.git"},
    }
    rendered = "\n".join(badges.build_readme_badges(ctx, tmp_path))
    assert "![Usage]" in rendered
    assert f"](https://github.com/example/project/blob/HEAD/{path})" in rendered


def test_usage_badge_uses_relative_links_without_github(badges, tmp_path):
    """Local projects and other Git hosts retain working README-relative links."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/usage.md").touch()
    ctx = {
        "documentation_types": {"entries": ["User guide"]},
        "urls": {"repository": "https://gitlab.com/example/project"},
    }
    rendered = "\n".join(badges.build_readme_badges(ctx, tmp_path))
    assert "![Usage]" in rendered
    assert "](docs/usage.md)" in rendered


@pytest.mark.parametrize("selected", [[], ["developer"], ["user"]])
def test_usage_badge_omits_missing_or_unselected_guides(badges, tmp_path, selected):
    """A selection alone never creates a link to a missing guide."""
    ctx = {"documentation_types": {"entries": selected}}
    if "user" not in selected:
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs/usage.md").touch()
    assert not any(
        "![Usage]" in badge for badge in badges.build_readme_badges(ctx, tmp_path)
    )


@pytest.mark.parametrize("name", ["bio.tools", "BioTools", "Bio tools"])
@pytest.mark.parametrize(
    "identifier",
    [
        "research_tool-1",
        "biotools:research_tool-1",
        "https://bio.tools/research_tool-1",
        "http://bio.tools/tool/research_tool-1",
        "https://bio.tools/t/research_tool-1/",
    ],
)
def test_biotools_badge_links_to_canonical_entry(badges, name, identifier):
    """Accept the registry's identifier representations without guessing an ID."""
    ctx = {"registries": {"entries": [{"name": name, "url_or_id": identifier}]}}
    rendered = "\n".join(badges.build_readme_badges(ctx))
    assert "![bio.tools]" in rendered
    assert "](https://bio.tools/research_tool-1)" in rendered
    assert "bio.tools-research__tool--1-blue" in unquote(rendered)


@pytest.mark.parametrize(
    "identifier",
    ["", None, "https://example.org/tool", "https://bio.tools/", "not an id"],
)
def test_biotools_badge_omits_missing_or_invalid_entries(badges, identifier):
    """Selecting a registry alone is not evidence that an entry exists."""
    ctx = {"registries": {"entries": [{"name": "bio.tools", "url_or_id": identifier}]}}
    assert not any("![bio.tools]" in badge for badge in badges.build_readme_badges(ctx))


def test_biotools_badge_skips_other_registries_and_duplicate_entries(badges):
    ctx = {
        "registries": {
            "entries": [
                {"name": "other", "url_or_id": "wrong"},
                {"name": "bio.tools", "url_or_id": ""},
                {"name": "bio.tools", "url_or_id": "right"},
                {"name": "bio.tools", "url_or_id": "right"},
            ]
        }
    }
    rendered = badges.build_readme_badges(ctx)
    assert sum("![bio.tools]" in badge for badge in rendered) == 1
    assert "](https://bio.tools/right)" in rendered[0]


@pytest.mark.parametrize("path", ["LICENSE", "LICENSE.md", "LICENSE.txt"])
def test_license_badge_links_to_existing_license(badges, tmp_path, path):
    (tmp_path / path).touch()
    rendered = "\n".join(badges.build_readme_badges({}, tmp_path))
    assert "![License]" in rendered
    assert f"]({path})" in rendered


def test_license_badge_prefers_full_r_license(badges, tmp_path):
    (tmp_path / "LICENSE").touch()
    (tmp_path / "LICENSE.md").touch()
    rendered = "\n".join(badges.build_readme_badges({}, tmp_path))
    assert "](LICENSE.md)" in rendered
    assert "](LICENSE)" not in rendered


def test_license_badge_omits_missing_license(badges, tmp_path):
    ctx = {"licensing": {"license": "MIT"}}
    assert not any(
        "![License]" in badge for badge in badges.build_readme_badges(ctx, tmp_path)
    )


@pytest.mark.parametrize(
    "identifier",
    [
        "10.5281/zenodo.12345",
        "https://doi.org/10.5281/zenodo.12345",
        "https://dx.doi.org/10.5281/zenodo.12345",
        "doi:10.5281/zenodo.12345",
    ],
)
def test_zenodo_badge_uses_supplied_doi(badges, identifier):
    ctx = {
        "persistent_identifiers": {
            "entries": [
                {"type": "doi", "identifier": ""},
                {"type": "doi", "identifier": identifier},
            ]
        }
    }
    rendered = "\n".join(badges.build_readme_badges(ctx))
    assert "https://zenodo.org/badge/DOI/10.5281/zenodo.12345.svg" in rendered
    assert "](https://doi.org/10.5281/zenodo.12345)" in rendered


def test_zenodo_selection_does_not_invent_doi_badge(badges):
    ctx = {"distribution_channels": {"entries": ["Zenodo"]}}
    assert not any("![DOI]" in badge for badge in badges.build_readme_badges(ctx))


def test_other_doi_badge_uses_generic_provider(badges):
    ctx = {
        "persistent_identifiers": {
            "entries": [{"type": "doi", "identifier": "10.1234/project"}]
        }
    }
    rendered = "\n".join(badges.build_readme_badges(ctx))
    assert "img.shields.io/badge/DOI-" in rendered
    assert "](https://doi.org/10.1234/project)" in rendered
    assert "zenodo.org" not in rendered
