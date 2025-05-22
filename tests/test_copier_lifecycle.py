"""Integration tests for Copier generation and template updates."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import yaml
from copier import run_copy, run_update

ROOT = Path(__file__).resolve().parents[1]


def run_git(repository: Path, *arguments: str) -> str:
    """Run a Git command in one test repository.

    Parameters
    ----------
    repository
        Git working tree.
    *arguments
        Arguments passed after ``git``.

    Returns
    -------
    str
        Stripped command output.
    """
    result = subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def initialize_repository(
    repository: Path,
    message: str,
    tag: str | None = None,
) -> None:
    """Initialize and commit one temporary Git repository.

    Parameters
    ----------
    repository
        Directory to initialize.
    message
        Initial commit message.
    tag
        Optional annotated release tag.
    """
    run_git(repository, "init", "--initial-branch=main")
    run_git(repository, "config", "user.name", "Template Test")
    run_git(repository, "config", "user.email", "template@example.org")
    run_git(repository, "add", ".")
    run_git(repository, "commit", "-m", message)
    if tag:
        run_git(repository, "tag", "-a", tag, "-m", tag)


def copy_template_source(destination: Path) -> Path:
    """Copy the complete Copier source without repository build artifacts.

    Parameters
    ----------
    destination
        Empty destination for the temporary template repository.

    Returns
    -------
    pathlib.Path
        Populated template source.
    """
    destination.mkdir()
    for directory in ("_config", "_copier_tasks", "templates"):
        shutil.copytree(ROOT / directory, destination / directory)
    shutil.copy2(ROOT / "copier.yml", destination / "copier.yml")
    return destination


def test_python_project_updates_preserve_edits_and_apply_new_answers(tmp_path):
    """Ensure a tagged update merges project work and new capabilities."""
    template = copy_template_source(tmp_path / "template")
    initialize_repository(template, "feat: initial template", "v1.0.0")

    project = tmp_path / "project"
    run_copy(
        str(template),
        project,
        data={
            "template_type": "python",
            "project_name": "Lifecycle Demo",
            "project_slug": "lifecycle_demo",
        },
        vcs_ref="v1.0.0",
        defaults=True,
        overwrite=True,
        quiet=True,
        unsafe=True,
    )
    initialize_repository(project, "chore: generate project")

    readme = project / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8")
        + "\n## Project notes\n\nProject-owned README content.\n",
        encoding="utf-8",
    )
    research_notes = project / "RESEARCH_NOTES.md"
    research_notes.write_text(
        "# Research notes\n\nProject-owned content.\n",
        encoding="utf-8",
    )
    service = project / "src" / "lifecycle_demo" / "services" / "processing.py"
    service.write_text(
        service.read_text(encoding="utf-8") + "\n# Project-owned extension.\n",
        encoding="utf-8",
    )
    run_git(project, "add", ".")
    run_git(project, "commit", "-m", "feat: extend generated project")

    gitignore = template / "templates" / "python" / ".gitignore"
    gitignore.write_text(
        gitignore.read_text(encoding="utf-8") + "\n# Local test output\n*.local-test\n",
        encoding="utf-8",
    )
    run_git(template, "add", ".")
    run_git(template, "commit", "-m", "feat: extend Python template")
    run_git(template, "tag", "-a", "v1.1.0", "-m", "v1.1.0")

    previous_commit = yaml.safe_load(
        (project / ".copier-answers.yml").read_text(encoding="utf-8")
    )["_commit"]
    run_update(
        project,
        data={"test_types": {"entries": ["Unit tests"]}},
        vcs_ref="v1.1.0",
        defaults=True,
        overwrite=True,
        quiet=True,
        unsafe=True,
    )

    updated_readme = readme.read_text(encoding="utf-8")
    assert "Project-owned README content." in updated_readme
    assert "python -m pytest" in updated_readme
    assert "Project-owned content." in research_notes.read_text(encoding="utf-8")
    assert "Project-owned extension." in service.read_text(encoding="utf-8")
    assert "*.local-test" in gitignore.read_text(encoding="utf-8")
    assert (project / "tests" / "test_unit.py").exists()
    assert (project / ".github" / "workflows" / "tests.yml").exists()

    answers = yaml.safe_load(
        (project / ".copier-answers.yml").read_text(encoding="utf-8")
    )
    assert answers["_commit"] != previous_commit
    assert answers["template_type"] == "python"
    assert answers["test_types"] == {"entries": ["Unit tests"]}
    assert "<<<<<<<" not in updated_readme


def test_r_template_generates_through_the_shared_copier_entrypoint(tmp_path):
    """Ensure the R package scaffold uses the shared answers and task lifecycle."""
    template = copy_template_source(tmp_path / "template")
    project = tmp_path / "r-project"

    run_copy(
        str(template),
        project,
        data={"template_type": "r"},
        defaults=True,
        overwrite=True,
        quiet=True,
        unsafe=True,
    )

    answers = yaml.safe_load(
        (project / ".copier-answers.yml").read_text(encoding="utf-8")
    )
    assert answers["template_type"] == "r"
    assert answers["project_slug"] == "my.awesome.project"
    assert (
        (project / "README.md")
        .read_text(encoding="utf-8")
        .startswith("# my.awesome.project\n")
    )
    assert (project / "DESCRIPTION").exists()
    assert (project / "R" / "process.R").exists()
    assert (project / "man" / "process_text.Rd").exists()
    assert (project / ".pre-commit-config.yaml").exists()
    assert (project / ".github" / "workflows" / "repository.yml").exists()
    assert not (project / ".github" / "workflows" / "tests.yml").exists()
