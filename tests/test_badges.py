"""Focused regression tests for metadata-driven README badges."""

from __future__ import annotations

import importlib
from pathlib import Path

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
