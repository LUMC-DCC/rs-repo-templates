"""Generation tests for the R package Copier template."""

from __future__ import annotations

import importlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from copier import run_copy

ROOT = Path(__file__).resolve().parents[1]
COPIER_SOURCE = ROOT
COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")

R_CONTEXT = {
    "project_name": "Research Tools",
    "project_slug": "research.tools",
    "project_short_description": "Reusable R tools for research workflows.",
    "project_long_description": (
        "An installable R package demonstrating reproducible research tooling."
    ),
    "versioning": {
        "version": "0.1.0",
        "scheme": "SemVer",
        "scheme_details": "",
        "release_frequency": "On demand (irregular/as needed)",
    },
    "development_status": "active",
    "keywords": {"entries": ["research-software", "r-package"]},
    "contributors": {
        "entries": [
            {
                "name": "Ada Lovelace",
                "given_names": "Ada",
                "family_names": "Lovelace",
                "email": "ada@example.org",
                "orcid": "0000-0002-1825-0097",
                "roles": ["Original author", "Maintainer"],
            },
            {
                "name": "Grace Hopper",
                "given_names": "Grace",
                "family_names": "Hopper",
                "roles": ["Co-author"],
            },
        ]
    },
    "funding": {
        "entries": [
            {
                "funder": "LUMC",
                "funder_identifier": "05xvt9f17",
                "funder_identifier_type": "ror",
                "funder_url": "https://www.lumc.nl/",
                "award_number": "R-001",
            }
        ]
    },
    "motivation": {
        "purpose": "Provide reusable research analysis functions.",
        "categories": {"entries": ["Data analysis"]},
        "problem_statement": "Research scripts need reusable package boundaries.",
        "value_proposition": "The package starts with documented, tested structure.",
    },
    "audiences": {"entries": ["Researchers (academia)"]},
    "urls": {
        "repository": "https://github.com/LUMC-DCC/research.tools",
        "homepage": "https://example.org/research.tools",
        "documentation": "https://lumc-dcc.github.io/research.tools",
    },
    "registries": {"entries": [{"name": "CRAN", "url_or_id": "research.tools"}]},
    "persistent_identifiers": {
        "entries": [{"type": "doi", "identifier": "10.5281/zenodo.12345"}]
    },
    "licensing": {"license": "MIT", "compatibility_check": "Yes - manual check"},
    "access": {"type": "free", "details": "Available without charge."},
    "include_metadata": True,
    "documentation_builder": "pkgdown",
    "documentation_types": {"entries": ["user", "developer", "deployment"]},
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
                "url": "https://github.com/LUMC-DCC/research.tools/issues",
            }
        ]
    },
    "contacts": {
        "community": "community@example.org",
        "code_of_conduct": "conduct@example.org",
        "security": "security@example.org",
    },
    "programming_languages": {
        "entries": [{"name": "R", "version_constraint": ">= 4.3", "role": "primary"}]
    },
    "software_functions": {
        "entries": [
            {
                "operations": [{"term": "Statistical data analysis"}],
                "cmd": "research.tools::process_text('data')",
            }
        ]
    },
    "interfaces": {
        "entries": [
            {
                "type": "Library",
                "specification": "Exported R package functions",
                "status": "Stable",
            }
        ]
    },
    "operating_systems": {
        "entries": [
            {"name": "Linux", "status": "Officially supported"},
            {"name": "macOS", "status": "Officially supported"},
            {"name": "Windows", "status": "Expected to work"},
        ]
    },
    "external_dependencies": {
        "entries": [
            {"name": "Graphviz", "version_constraint": ">= 9", "purpose": "Plots"}
        ]
    },
    "external_services": {"entries": []},
    "test_types": {
        "entries": [
            "Smoke tests",
            "Doctests",
            "Unit tests",
            "Integration tests",
            "System / end-to-end tests",
            "Regression tests",
            "Property-based / fuzz",
        ]
    },
    "test_frameworks": {"entries": ["testthat"]},
    "quality_tools": {"formatter": "styler", "linter": "lintr", "type_checker": ""},
    "project_manager": "renv",
    "distribution_channels": {"entries": ["CRAN", "GitHub Releases", "Zenodo"]},
    "containerization": {
        "entries": [
            {"type": "Docker"},
            {"type": "OCI / Podman"},
            {"type": "Apptainer / Singularity"},
        ]
    },
    "resource_requirements": "Memory: 1 GB; CPU: one core.",
    "maintenance_level": "Active/routine maintenance",
    "continuity_plan": "Maintainers nominate a successor before handover.",
    "retirement_criteria": {"entries": ["Lack of maintainers"]},
    "regulatory_requirements": {"selected": {"entries": []}, "additional": ""},
    "security_measures": {"selected": {"entries": []}, "additional": ""},
    "data_management": {
        "sensitive_data_statement": "No sensitive data.",
        "dmp_reference": "",
    },
}


@pytest.fixture(scope="session")
def r_copier_source(tmp_path_factory):
    """Create one isolated source copy for R generation tests."""
    source = tmp_path_factory.mktemp("r-copier-source")
    for directory in ("_config", "_copier_tasks", "templates"):
        shutil.copytree(ROOT / directory, source / directory)
    shutil.copy2(ROOT / "copier.yml", source / "copier.yml")
    return source


def finalize_r_project(project_path: Path) -> None:
    """Run shared finalization for a rendered R project."""
    task_root = ROOT / "_copier_tasks"
    sys.path.insert(0, str(task_root))
    try:
        finalize_module = importlib.import_module("finalize")
        finalize_module.finalize(project_path, "r")
    finally:
        sys.path.remove(str(task_root))


def render_r_project(tmp_path, monkeypatch, r_copier_source, **overrides):
    """Render and finalize one representative R repository."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    spdx_dir = tmp_path / "spdx"
    spdx_dir.mkdir()
    (spdx_dir / "MIT.json").write_text(
        json.dumps(
            {
                "licenseId": "MIT",
                "name": "MIT License",
                "licenseText": "MIT License\n\nPermission is granted for testing.",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("SPDX_LICENSE_API_BASE", spdx_dir.as_uri())

    context = R_CONTEXT | overrides
    project_path = tmp_path / "generated" / context["project_slug"]
    run_copy(
        str(r_copier_source),
        project_path,
        data={"template_type": "r"} | context,
        defaults=True,
        overwrite=True,
        quiet=True,
        unsafe=True,
        skip_tasks=True,
    )
    finalize_r_project(project_path)
    return project_path


def run(command, cwd):
    """Run one generated-project verification command."""
    return subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)


def test_r_default_context_generates_installable_package(
    tmp_path, monkeypatch, r_copier_source
):
    """Untouched defaults should produce a sparse but buildable R package."""
    project = render_r_project(
        tmp_path,
        monkeypatch,
        r_copier_source,
        **{
            key: value
            for key, value in {
                "project_name": "",
                "project_slug": "my.awesome.project",
                "project_short_description": "",
                "project_long_description": "",
                "contributors": {"entries": []},
                "licensing": {"license": "", "compatibility_check": ""},
                "include_metadata": False,
                "documentation_types": {"entries": []},
                "documentation_builder": "",
                "community_files": {"entries": []},
                "test_types": {"entries": []},
                "test_frameworks": {"entries": []},
                "quality_tools": {"formatter": "", "linter": "", "type_checker": ""},
                "distribution_channels": {"entries": []},
                "containerization": {"entries": []},
            }.items()
        },
    )

    for rel_path in (
        "DESCRIPTION",
        "NAMESPACE",
        "R/process.R",
        "man/process_text.Rd",
        "my.awesome.project.Rproj",
        ".Rprofile",
        ".github/workflows/repository.yml",
    ):
        assert (project / rel_path).is_file(), rel_path
    for rel_path in (
        "tests",
        "docs",
        "codemeta.json",
        "CITATION.cff",
        "Containerfile",
        "environment.R",
        ".lintr",
    ):
        assert not (project / rel_path).exists(), rel_path

    parsed = run(
        ["Rscript", "-e", "d <- read.dcf('DESCRIPTION'); stopifnot(nrow(d) == 1)"],
        project,
    )
    assert parsed.returncode == 0, parsed.stdout + parsed.stderr
    built = run(["R", "CMD", "build", "."], project)
    assert built.returncode == 0, built.stdout + built.stderr


def test_r_rich_context_composes_package_and_shared_backbone(
    tmp_path, monkeypatch, r_copier_source
):
    """R-specific files should compose with all reusable public files."""
    project = render_r_project(tmp_path, monkeypatch, r_copier_source)
    for rel_path in (
        "DESCRIPTION",
        "NAMESPACE",
        "R/process.R",
        "man/process_text.Rd",
        "tests/testthat.R",
        "tests/testthat/test-smoke.R",
        "tests/testthat/test-doctest.R",
        "tests/testthat/test-unit.R",
        "tests/testthat/test-integration.R",
        "tests/testthat/test-system.R",
        "tests/testthat/test-regression.R",
        "tests/testthat/test-property.R",
        "_pkgdown.yml",
        "docs/documentation.md",
        "docs/developer.md",
        "codemeta.json",
        "CITATION.cff",
        "LICENSE",
        "CONTRIBUTING.md",
        ".github/workflows/tests.yml",
        ".github/workflows/quality.yml",
        ".github/workflows/docs.yml",
        ".github/workflows/distribution.yml",
        "Dockerfile",
        "Containerfile",
        "Apptainer.def",
        "tools/check_release.R",
    ):
        assert (project / rel_path).is_file(), rel_path

    description = (project / "DESCRIPTION").read_text(encoding="utf-8")
    assert "Package: research.tools" in description
    assert "Version: 0.1.0" in description
    assert 'given = "Ada"' in description
    assert 'role = c("aut", "cre")' in description
    assert "Depends: R (>= 4.3.0)" in description
    assert "License: MIT + file LICENSE" in description
    assert "COPYRIGHT HOLDER: Ada Lovelace, Grace Hopper" in (
        project / "LICENSE"
    ).read_text(encoding="utf-8")
    assert "MIT License" in (project / "LICENSE.md").read_text(encoding="utf-8")
    assert "testthat (>= 3.0.0)" in description
    assert "styler" in description
    assert "lintr" in description
    assert "pkgdown" in description
    documentation = (project / "docs/documentation.md").read_text(encoding="utf-8")
    assert "pkgdown::build_site(preview = TRUE)" in documentation
    assert "pkgdown::build_site()" in documentation
    assert "@@DOCS_" not in documentation

    readme = (project / "README.md").read_text(encoding="utf-8")
    contributing = (project / "CONTRIBUTING.md").read_text(encoding="utf-8")
    codemeta = json.loads((project / "codemeta.json").read_text(encoding="utf-8"))
    for heading in (
        "## Purpose",
        "## Intended Audience",
        "## Installation",
        "## Usage",
        "## Citation",
        "## Support",
    ):
        assert heading in readme
    assert "library(research.tools)" in readme
    assert "See `LICENSE.md` for the full license text." in readme
    assert "## Access" in readme
    assert "styler::style_pkg" in contributing
    assert "lintr::lint_package" in contributing
    assert "testthat::test_local" in contributing
    assert codemeta["programmingLanguage"][0]["name"] == "R"
    assert codemeta["isAccessibleForFree"] is True
    assert codemeta["funder"][0]["@id"] == "https://ror.org/05xvt9f17"

    for rel_path in ("Dockerfile", "Containerfile", "Apptainer.def", "DESCRIPTION"):
        content = (project / rel_path).read_text(encoding="utf-8")
        assert "@@R_" not in content
    assert "rocker/r-ver:4.3.0" in (project / "Dockerfile").read_text(encoding="utf-8")

    built = run(["R", "CMD", "build", "."], project)
    assert built.returncode == 0, built.stdout + built.stderr
    release = run(["Rscript", "tools/check_release.R", "v0.1.0"], project)
    assert release.returncode == 0, release.stdout + release.stderr


def test_r_manager_and_capability_selection(tmp_path, monkeypatch, r_copier_source):
    """Rix and optional test selections should prune incompatible files."""
    project = render_r_project(
        tmp_path,
        monkeypatch,
        r_copier_source,
        project_manager="rix",
        test_types={"entries": ["Unit tests"]},
        quality_tools={"formatter": "", "linter": "", "type_checker": ""},
        documentation_types={"entries": []},
        documentation_builder="",
        distribution_channels={"entries": []},
        containerization={"entries": []},
    )
    assert (project / "environment.R").is_file()
    assert not (project / ".Rprofile").exists()
    assert (project / "tests/testthat/test-unit.R").is_file()
    for test_name in ("test-smoke.R", "test-integration.R", "test-system.R"):
        assert not (project / "tests/testthat" / test_name).exists()
    assert not (project / ".github/workflows/quality.yml").exists()
    assert not (project / ".github/workflows/docs.yml").exists()
    assert not (project / ".github/workflows/distribution.yml").exists()
    environment = (project / "environment.R").read_text(encoding="utf-8")
    assert 'r_ver = "4.3.0"' in environment
    assert "@@R_" not in environment
    assert "Rscript environment.R" in (project / "README.md").read_text(
        encoding="utf-8"
    )


def test_r_workflows_are_valid_and_actions_are_pinned(
    tmp_path, monkeypatch, r_copier_source
):
    """Generated R workflows should parse and pin every external action."""
    project = render_r_project(tmp_path, monkeypatch, r_copier_source)
    workflows = sorted((project / ".github/workflows").glob("*.yml"))
    assert workflows
    for workflow in workflows:
        parsed = yaml.safe_load(workflow.read_text(encoding="utf-8"))
        assert "jobs" in parsed
        for match in re.finditer(r"uses:\s+[^\s@]+@([^\s#]+)", workflow.read_text()):
            assert COMMIT_SHA_PATTERN.fullmatch(match.group(1)), workflow

    tests = yaml.safe_load((project / ".github/workflows/tests.yml").read_text())
    assert tests["jobs"]["check"]["strategy"]["matrix"]["os"] == [
        "ubuntu-latest",
        "macos-latest",
    ]
