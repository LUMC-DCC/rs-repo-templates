"""Generation tests for the Python Cookiecutter template.

The tests render representative Python projects and validate the generated
files, metadata, import behavior, and generated test suite.
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml
from cookiecutter.main import cookiecutter
from jsonschema import Draft7Validator
from rs_metadata.vocabulary import cff_schema

ROOT = Path(__file__).resolve().parents[1]
PYTHON_TEMPLATE = ROOT / "python"
SPDX_LICENSE_TEXT = "MIT License\n\nPermission is hereby granted for testing."
COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")

BASE_CONTEXT = {
    "project_name": "Research Template Demo",
    "project_slug": "research_template_demo",
    "project_short_description": "A generated research software template demo.",
    "project_long_description": (
        "A longer public description of the generated research software."
    ),
    "versioning": {
        "version": "0.2.0",
        "scheme": "SemVer",
        "scheme_details": "",
        "release_frequency": "After each major feature",
    },
    "development_status": "active",
    "keywords": {"entries": ["research-software", "template"]},
    "contributors": {
        "entries": [
            {
                "name": "Ada Lovelace",
                "given_names": "Ada",
                "family_names": "Lovelace",
                "email": "ada@example.org",
                "affiliations": [
                    {
                        "name": "Leiden University Medical Center",
                        "identifier": "https://ror.org/05xvt9f17",
                    }
                ],
                "orcid": "0000-0002-1825-0097",
                "url": "https://example.org/ada",
                "roles": ["Original author", "Maintainer"],
            },
            {
                "name": "Grace Hopper",
                "given_names": "Grace",
                "family_names": "Hopper",
                "email": "grace@example.org",
                "affiliations": [
                    {
                        "name": "Leiden University Medical Center",
                        "identifier": "https://ror.org/05xvt9f17",
                    }
                ],
                "orcid": "0000-0001-5109-3700",
                "roles": ["Co-author"],
            },
            {
                "name": "Research Software Team",
                "email": "rs@example.org",
                "url": "https://example.org/research-software-team",
                "roles": ["Maintainer"],
            },
            {
                "name": "Katherine Johnson",
                "affiliations": [
                    {
                        "name": "Leiden University Medical Center",
                        "identifier": "https://ror.org/05xvt9f17",
                    }
                ],
                "roles": ["Principal investigator"],
            },
        ],
    },
    "funding": {
        "entries": [
            {
                "funder": "LUMC",
                "award_number": "LUMC-2024-001",
                "award_title": "Research Software Sustainability",
                "grant_url": "https://example.org/grants/lumc-2024-001",
            },
            {
                "funder": "Health-RI",
                "project_code": "HRI-RS-2",
            },
            {
                "funder": "LUMC",
                "project_code": "RS-002",
            },
        ]
    },
    "motivation": {
        "purpose": "Demonstrate a generated research software repository.",
        "categories": {"entries": ["Data analysis", "Integration & interfacing"]},
        "problem_statement": "Researchers need repeatable project scaffolds.",
        "value_proposition": (
            "The template standardizes reusable foundations without hiding the code."
        ),
    },
    "audiences": {"entries": ["Researchers (academia)", "Software developers / RSEs"]},
    "related_software": {
        "entries": [
            {
                "name": "Snakemake",
                "url_or_doi": "https://snakemake.readthedocs.io",
                "relationship": "workflow orchestration inspiration",
            },
            {
                "name": "Research Object Crate",
                "url_or_doi": "https://www.researchobject.org/ro-crate/",
                "relationship": "metadata interoperability",
            },
        ]
    },
    "urls": {
        "repository": "https://github.com/LUMC-DCC/research-template-demo",
        "homepage": "https://example.org/research-template-demo",
        "documentation": "https://lumc-dcc.github.io/research-template-demo",
    },
    "registries": {
        "entries": [
            {"name": "PyPI", "url_or_id": "research-template-demo"},
            {
                "name": "bio.tools",
                "url_or_id": "research-template-demo",
                "notes": "life-science registry entry",
            },
        ]
    },
    "persistent_identifiers": {
        "entries": [
            {"type": "doi", "identifier": "10.5281/zenodo.12345"},
            {
                "type": "swh",
                "identifier": "swh:1:dir:bc286860f423ea7ced246ba7458eef4b4541cf2d",
                "associated_version": "0.2.0",
            },
        ],
    },
    "publications": {
        "entries": [
            {
                "title": "Research Template Demo: reusable software scaffolds",
                "doi": "10.1234/example",
                "preferred": True,
                "authors": [
                    {
                        "name": "Ada Lovelace",
                        "given_names": "Ada",
                        "family_names": "Lovelace",
                    },
                ],
            },
            {
                "citation": "Validation of reusable research software templates",
                "pmid": "12345678",
                "pmcid": "PMC7654321",
                "url": "https://example.org/publications/template-validation",
                "note": "Validation study",
                "authors": [
                    {
                        "name": "Grace Hopper",
                        "given_names": "Grace",
                        "family_names": "Hopper",
                    },
                ],
            },
        ]
    },
    "include_metadata": True,
    "documentation_builder": "mkdocs",
    "documentation_types": {"entries": ["user", "developer"]},
    "community_files": {
        "entries": [
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "CHANGELOG.md",
        ]
    },
    "support_routes": {
        "entries": [
            {
                "system": "GitHub issues",
                "url": "https://github.com/LUMC-DCC/research-template-demo/issues",
            },
            {
                "system": "Helpdesk",
                "url": "https://example.org/helpdesk",
            },
        ],
    },
    "contacts": {
        "community": "mailto:community@example.org",
        "code_of_conduct": "mailto:conduct@example.org",
        "security": "mailto:security@example.org",
    },
    "governance_notes": "Maintained by the research software team.",
    "programming_languages": {
        "entries": [
            {
                "name": "Python",
                "version_constraint": ">=3.11",
                "role": "primary package",
            },
            {
                "name": "R",
                "version_constraint": ">=4.3",
                "role": "analysis examples",
            },
        ],
    },
    "software_functions": {
        "entries": [
            {
                "operations": [
                    {
                        "term": "Statistical data analysis",
                        "uri": "http://edamontology.org/operation_2238",
                    }
                ],
                "topics": [
                    {
                        "term": "Proteomics",
                        "uri": "http://edamontology.org/topic_0121",
                    }
                ],
                "inputs": [
                    {
                        "data": {
                            "term": "Expression data",
                            "uri": "http://edamontology.org/data_2603",
                        },
                        "format": [
                            {
                                "term": "CSV",
                                "uri": "http://edamontology.org/format_3752",
                                "version_constraint": ">=1.0",
                                "schema_constraints": "Columns: sample_id, value",
                                "sample_url": "https://example.org/data/example.csv",
                            },
                            {
                                "term": "TSV",
                                "uri": "http://edamontology.org/format_3475",
                            },
                        ],
                    }
                ],
                "outputs": [
                    {
                        "data": {
                            "term": "Expression data",
                            "uri": "http://edamontology.org/data_2603",
                        },
                        "format": [
                            {
                                "term": "JSON",
                                "uri": "http://edamontology.org/format_3464",
                            }
                        ],
                    }
                ],
                "cmd": "research-template-demo analyse input.csv",
                "note": "Summarizes numeric observations by group.",
            }
        ]
    },
    "interfaces": {
        "entries": [
            {
                "type": "Command-line tool",
                "specification": "Command-line interface for local analysis workflows",
                "status": "Stable",
            },
            {
                "type": "Web API",
                "specification": "OpenAPI-described service endpoint for analysis jobs",
                "status": "Experimental",
            },
            {
                "type": "Script",
                "specification": "Batch entry point for scheduled processing",
                "status": "Experimental",
            },
        ]
    },
    "operating_systems": {
        "entries": [
            {
                "name": "Linux",
                "specification": ">=Ubuntu 22.04",
                "status": "Officially supported",
            },
            {
                "name": "macOS",
                "specification": ">=13",
                "status": "Officially supported",
            },
            {
                "name": "Windows",
                "status": "Expected to work",
            },
        ]
    },
    "external_dependencies": {
        "entries": [
            {
                "name": "Graphviz",
                "version_constraint": ">=9",
                "url": "https://graphviz.org/",
                "license": "EPL-1.0",
                "purpose": "Diagram rendering for reports",
            },
            {
                "name": "EDAM ontology",
                "url": "https://edamontology.org/",
                "license": "CC-BY-SA-4.0",
                "purpose": "Controlled vocabulary for function metadata",
            },
        ]
    },
    "external_services": {
        "entries": [
            {
                "name": "DCC consultancy",
                "provider": "LUMC DCC",
                "service_types": [
                    "Institutional support (DCC, IT, library)",
                    "Domain expertise",
                ],
                "quantity": "0.1 FTE during first release",
                "cost_coverage": ["Departmental overhead"],
            },
            {
                "name": "Hosted CI minutes",
                "provider": "GitHub Actions",
                "service_types": ["CI / CD minutes"],
                "quantity": "Standard hosted runner quota",
                "cost_coverage": ["Free tier"],
            },
        ]
    },
    "test_types": {
        "entries": [
            "Smoke tests",
            "Doctests",
            "Unit tests",
            "Integration tests",
            "System / end-to-end tests",
            "Regression tests",
        ],
    },
    "test_frameworks": {"entries": ["pytest"]},
    "quality_tools": {
        "formatter": "ruff",
        "linter": "ruff",
        "type_checker": "",
    },
    "project_manager": "uv",
    "distribution_channels": {"entries": ["PyPI", "GitHub Releases"]},
    "containerization": {
        "entries": [
            {
                "type": "Docker",
                "details": "Publish tagged images with project releases.",
            },
            {
                "type": "Apptainer / Singularity",
                "details": "Use on managed HPC systems.",
            },
        ],
    },
    "resource_requirements": (
        "Memory: 1 GB typical. Compute: 1 CPU core. GPU: not required."
    ),
    "maintenance_level": "Best-effort maintenance / no timeline commitment",
    "continuity_plan": "",
    "retirement_criteria": {"entries": []},
    "public_risk_notes": "",
    "regulatory_requirements": {
        "selected": {
            "entries": [
                "GDPR - General Data Protection Regulation (EU data protection)"
            ]
        },
        "additional": "Project releases follow the institutional research code.",
    },
    "security_measures": {
        "selected": {
            "entries": [
                "Vulnerability scanning (e.g., Snyk, Dependabot)",
                "Security patch management process",
            ]
        },
        "additional": "Security reports are reviewed privately.",
    },
    "data_management": {
        "sensitive_data_statement": "No sensitive data is stored by the software.",
        "dmp_reference": "",
    },
    "licensing": {
        "license": "MIT",
        "compatibility_check": "Yes - automated tooling",
    },
}


def render_python_project(tmp_path, monkeypatch, **overrides):
    """Render the Python template in an isolated temporary directory.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Pytest temporary directory.
    monkeypatch : pytest.MonkeyPatch
        Fixture used to isolate Cookiecutter's home and replay directories.
    **overrides
        Context values that override ``BASE_CONTEXT``.

    Returns
    -------
    pathlib.Path
        Path to the generated project.
    """
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    spdx_dir = tmp_path / "spdx"
    spdx_dir.mkdir(exist_ok=True)
    (spdx_dir / "MIT.json").write_text(
        json.dumps(
            {
                "licenseId": "MIT",
                "name": "MIT License",
                "licenseText": SPDX_LICENSE_TEXT,
            }
        ),
        encoding="utf-8",
    )
    (spdx_dir / "Apache-2.0.json").write_text(
        json.dumps(
            {
                "licenseId": "Apache-2.0",
                "name": "Apache License 2.0",
                "licenseText": "Apache License\nVersion 2.0",
            }
        ),
        encoding="utf-8",
    )
    (spdx_dir / "BSD-3-Clause.json").write_text(
        json.dumps(
            {
                "licenseId": "BSD-3-Clause",
                "name": "BSD 3-Clause License",
                "licenseText": "BSD 3-Clause License\n\nRedistribution permitted.",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("SPDX_LICENSE_API_BASE", spdx_dir.as_uri())

    output_dir = tmp_path / "generated"
    context = BASE_CONTEXT | overrides

    return Path(
        cookiecutter(
            str(PYTHON_TEMPLATE),
            no_input=True,
            extra_context=context,
            output_dir=str(output_dir),
            default_config={
                "cookiecutters_dir": str(tmp_path / "cookiecutters"),
                "replay_dir": str(tmp_path / "replay"),
            },
        )
    )


def test_python_default_context_generates_sparse_working_project(
    tmp_path,
    monkeypatch,
):
    """Ensure untouched public defaults produce a valid sparse repository."""
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    project_path = Path(
        cookiecutter(
            str(PYTHON_TEMPLATE),
            no_input=True,
            output_dir=str(tmp_path / "generated"),
            default_config={
                "cookiecutters_dir": str(tmp_path / "cookiecutters"),
                "replay_dir": str(tmp_path / "replay"),
            },
        )
    )

    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    assert project_path.name == "my_awesome_project"
    assert pyproject["project"]["version"] == "0.1.0"
    assert pyproject["project"]["requires-python"] == ">=3.12"
    for rel_path in (
        "CITATION.cff",
        "codemeta.json",
        "LICENSE",
        "docs",
        "tests",
        "CONTRIBUTING.md",
        ".github/workflows",
        ".pre-commit-config.yaml",
    ):
        assert not (project_path / rel_path).exists(), rel_path


def assert_no_template_artifacts(project_path):
    """Assert that rendered projects contain no template leftovers.

    Parameters
    ----------
    project_path : pathlib.Path
        Path to the generated project.
    """
    all_paths = list(project_path.rglob("*"))
    assert not [path for path in all_paths if path.name == ".DS_Store"]
    assert not (project_path / ".template_hooks").exists()
    assert not [path for path in all_paths if "{{" in path.name or "}}" in path.name]

    unresolved = []
    leading_blank_lines = []
    markdown_collisions = []
    for path in all_paths:
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        if content.startswith("\n"):
            leading_blank_lines.append(path.relative_to(project_path))
        if (
            "{{ cookiecutter" in content
            or "{% " in content
            or "@@PROJECT_" in content
            or "@@METADATA_" in content
        ):
            unresolved.append(path.relative_to(project_path))
        if path.suffix == ".md" and ("```##" in content or "|\n##" in content):
            markdown_collisions.append(path.relative_to(project_path))

    assert unresolved == []
    assert leading_blank_lines == []
    assert markdown_collisions == []


def assert_external_actions_are_pinned(project_path):
    """Assert generated workflow actions use immutable commit references.

    Parameters
    ----------
    project_path : pathlib.Path
        Generated project root.
    """
    for path in (project_path / ".github").rglob("*.yml"):
        content = path.read_text(encoding="utf-8")
        for action, reference in re.findall(
            r"uses:\s*([^@\s]+)@([^#\s]+)",
            content,
        ):
            if not action.startswith("./"):
                assert COMMIT_SHA_PATTERN.fullmatch(reference), (
                    path,
                    action,
                    reference,
                )


def expected_test_dependencies(context):
    """Return expected Python test extras for one rendered context.

    Parameters
    ----------
    context : dict
        Rendered or requested Cookiecutter context values.

    Returns
    -------
    list of str
        Expected dependencies in ``project.optional-dependencies.test``.
    """
    dependencies = ["pytest"]
    interfaces = context.get("interfaces", {}).get("entries", [])
    interface_types = {
        interface.get("type", "")
        for interface in interfaces
        if isinstance(interface, dict)
    }
    if interface_types & {
        "Bioinformatics portal",
        "Database portal",
        "SPARQL endpoint",
        "Web API",
        "Web application",
        "Web service",
        "Workbench",
    }:
        dependencies.append("fastapi")
    if interface_types & {
        "Bioinformatics portal",
        "Database portal",
        "SPARQL endpoint",
        "Web API",
        "Web application",
        "Workbench",
    }:
        dependencies.append("httpx")
    test_types = context.get("test_types", {}).get("entries", [])
    if "Property-based / fuzz" in test_types:
        dependencies.append("hypothesis")
    return dependencies


def expected_runtime_dependencies(context):
    """Return expected Python runtime dependencies for one context.

    Parameters
    ----------
    context : dict
        Rendered or requested Cookiecutter context values.

    Returns
    -------
    list of str
        Expected dependencies in ``project.dependencies``.
    """
    dependencies = []
    interface_types = {
        interface.get("type", "")
        for interface in context.get("interfaces", {}).get("entries", [])
        if isinstance(interface, dict)
    }
    if "Command-line tool" in interface_types:
        dependencies.append("typer")
    if interface_types & {"Ontology", "SPARQL endpoint"}:
        dependencies.append("rdflib")
    configuration_measures = {
        "Secrets management (e.g., environment variables, vault)",
        "Secure configuration management (e.g., Infrastructure-as-Code, hardening)",
    }
    security_measures = (
        context.get("security_measures", {}).get("selected", {}).get("entries", [])
    )
    http_interfaces = {
        "Bioinformatics portal",
        "Database portal",
        "SPARQL endpoint",
        "Web API",
        "Web application",
        "Web service",
        "Workbench",
    }
    has_runtime_configuration = bool(
        interface_types & http_interfaces
        or set(security_measures) & configuration_measures
    )
    if has_runtime_configuration:
        dependencies.append("pydantic-settings")
    return dependencies


def expected_quality_dependencies(context):
    """Return expected Python quality extras for one rendered context.

    Parameters
    ----------
    context : dict
        Rendered or requested Cookiecutter context values.

    Returns
    -------
    list of str
        Expected dependencies in ``project.optional-dependencies.quality``.
    """
    quality_tools = context.get("quality_tools", {})
    formatter_tool = quality_tools.get("formatter", "")
    linter_tool = quality_tools.get("linter", "")
    type_checker = quality_tools.get("type_checker", "")
    has_quality_checks = bool(formatter_tool) or bool(linter_tool) or bool(type_checker)
    dependencies = ["pre-commit"] if has_quality_checks else []
    if formatter_tool == "ruff" or linter_tool == "ruff":
        dependencies.append("ruff")
    if type_checker == "mypy":
        dependencies.append("mypy")
    return dependencies


TEST_FILE_BY_TYPE = {
    "Smoke tests": "tests/test_smoke.py",
    "Doctests": "tests/test_doctest.py",
    "Unit tests": "tests/test_unit.py",
    "Integration tests": "tests/test_integration.py",
    "System / end-to-end tests": "tests/test_system.py",
    "Regression tests": "tests/test_regression.py",
    "Property-based / fuzz": "tests/test_property.py",
}


def assert_selected_test_files(project_path, selected_types):
    """Assert that test type selection controls generated test files.

    Parameters
    ----------
    project_path : pathlib.Path
        Path to the generated project.
    selected_types : set of str
        Selected canonical SMP test type labels.
    """
    for test_type, rel_path in TEST_FILE_BY_TYPE.items():
        if test_type in selected_types:
            assert (project_path / rel_path).exists(), rel_path
        else:
            assert not (project_path / rel_path).exists(), rel_path


@pytest.mark.parametrize(
    ("case_name", "overrides", "present", "absent"),
    [
        (
            "full",
            {},
            [
                "LICENSE",
                "CITATION.cff",
                "codemeta.json",
                "docs/index.md",
                "docs/overview.md",
                "docs/developer.md",
                "docs/reference.md",
                "docs/legal.md",
                "docs/release.md",
                "mkdocs.yml",
                "CONTRIBUTING.md",
                "CODE_OF_CONDUCT.md",
                ".github/pull_request_template.md",
                "CHANGELOG.md",
                ".pre-commit-config.yaml",
                "tools/check_changelog.py",
                "tools/check_release.py",
                "Dockerfile",
                ".dockerignore",
                "Apptainer.def",
                "tests/test_smoke.py",
                "tests/test_doctest.py",
                "tests/test_unit.py",
                "tests/test_integration.py",
                "tests/test_system.py",
                "tests/test_regression.py",
                ".github/workflows/metadata.yml",
                ".github/workflows/docs.yml",
                ".github/workflows/tests.yml",
                ".github/workflows/quality.yml",
                ".github/workflows/containers.yml",
                ".github/workflows/distribution.yml",
                ".github/workflows/changelog.yml",
                ".github/workflows/license-compatibility.yml",
                ".github/workflows/security.yml",
                ".env.example",
                "src/research_template_demo/config.py",
                "src/research_template_demo/logging_config.py",
                "src/research_template_demo/adapters/api/__init__.py",
                "src/research_template_demo/adapters/api/app.py",
                "src/research_template_demo/adapters/api/routes/processing.py",
                "src/research_template_demo/adapters/api/schemas.py",
                "src/research_template_demo/adapters/server_runner.py",
                "src/research_template_demo/adapters/cli/__init__.py",
                "src/research_template_demo/adapters/cli/app.py",
                "src/research_template_demo/adapters/cli/commands/process.py",
                "scripts/run_example.py",
                "src/research_template_demo/services/__init__.py",
                "src/research_template_demo/services/processing.py",
            ],
            [
                "GOVERNANCE.md",
                "SECURITY.md",
                "SUPPORT.md",
                ".github/ISSUE_TEMPLATE",
                "tests/test_property.py",
                "Containerfile",
                "zensical.toml",
                ".zenodo.json",
                "licenses",
            ],
        ),
        (
            "minimal",
            {
                "project_slug": "minimal_demo",
                "documentation_types": {"entries": []},
                "test_types": {"entries": []},
                "interfaces": {"entries": []},
                "licensing": {"license": "", "compatibility_check": ""},
                "include_metadata": False,
                "quality_tools": {
                    "formatter": "",
                    "linter": "",
                    "type_checker": "",
                },
                "project_manager": "",
                "distribution_channels": {"entries": []},
                "containerization": {"entries": []},
                "community_files": {"entries": []},
                "security_measures": {"selected": {"entries": []}, "additional": ""},
            },
            [
                "README.md",
                "pyproject.toml",
                "src/minimal_demo/__init__.py",
                "src/minimal_demo/main.py",
                "src/minimal_demo/services/__init__.py",
                "src/minimal_demo/services/processing.py",
            ],
            [
                "LICENSE",
                "CITATION.cff",
                "codemeta.json",
                "docs",
                "mkdocs.yml",
                "zensical.toml",
                "tests",
                "src/minimal_demo/adapters",
                "scripts",
                "CONTRIBUTING.md",
                ".github/pull_request_template.md",
                "CODE_OF_CONDUCT.md",
                "GOVERNANCE.md",
                "SECURITY.md",
                "SUPPORT.md",
                "CHANGELOG.md",
                ".pre-commit-config.yaml",
                "tools/check_changelog.py",
                "tools/check_release.py",
                "Dockerfile",
                "Containerfile",
                ".dockerignore",
                "Apptainer.def",
                ".github/workflows/quality.yml",
                ".github/workflows/metadata.yml",
                ".github/workflows/containers.yml",
                ".github/workflows/distribution.yml",
                ".github/workflows/changelog.yml",
                ".github/workflows/license-compatibility.yml",
                ".github/workflows/security.yml",
                ".github/actions/setup-python-project",
                ".env.example",
                "src/minimal_demo/config.py",
                "src/minimal_demo/logging_config.py",
                "src/minimal_demo/adapters/server_runner.py",
                ".zenodo.json",
                "licenses",
            ],
        ),
    ],
)
def test_python_template_generates_expected_option_sets(
    tmp_path, monkeypatch, case_name, overrides, present, absent
):
    """Ensure full and minimal Python option sets render expected files."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_name=f"{case_name.title()} Demo",
        **overrides,
    )

    assert_no_template_artifacts(project_path)

    for rel_path in present:
        assert (project_path / rel_path).exists(), rel_path

    for rel_path in absent:
        assert not (project_path / rel_path).exists(), rel_path

    metadata = tomllib.loads((project_path / "pyproject.toml").read_text())
    expected_name = overrides.get(
        "project_slug",
        BASE_CONTEXT["project_slug"],
    ).replace("_", "-")
    assert metadata["project"]["name"] == expected_name
    assert (
        metadata["project"]["version"]
        == overrides.get(
            "versioning",
            BASE_CONTEXT["versioning"],
        )["version"]
    )
    programming_languages = overrides.get(
        "programming_languages",
        BASE_CONTEXT["programming_languages"],
    )
    expected_python_constraint = next(
        (
            programming_language["version_constraint"]
            for programming_language in programming_languages["entries"]
            if programming_language.get("name", "").lower() == "python"
            and programming_language.get("version_constraint")
        ),
        ">=3.12",
    )
    assert metadata["project"]["requires-python"] == expected_python_constraint
    assert metadata["project"]["description"] == overrides.get(
        "project_short_description",
        BASE_CONTEXT["project_short_description"],
    )
    assert metadata["project"]["keywords"] == BASE_CONTEXT["keywords"]["entries"]
    assert metadata["project"]["classifiers"] == [
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ]
    optional_dependencies = metadata["project"].get("optional-dependencies", {})
    if case_name == "full":
        assert optional_dependencies["license"] == ["licensecheck"]
        assert metadata["tool"]["licensecheck"] == {
            "license": "MIT",
            "format": "simple",
            "zero": True,
        }
        assert metadata["project"]["dependencies"] == expected_runtime_dependencies(
            BASE_CONTEXT,
        )
        assert metadata["project"]["license-files"] == ["LICENSE"]
        assert optional_dependencies["api"] == ["fastapi", "uvicorn[standard]"]
        assert optional_dependencies["quality"] == ["pre-commit", "ruff"]
        assert optional_dependencies["release"] == ["build", "packaging", "twine"]
        assert metadata["tool"]["ruff"]["line-length"] == 88
        assert "target-version" not in metadata["tool"]["ruff"]
        assert metadata["project"]["scripts"] == {
            "research-template-demo": "research_template_demo.adapters.cli.app:main",
            "research-template-demo-serve": (
                "research_template_demo.adapters.server_runner:main"
            ),
        }
        for workflow_path in (project_path / ".github" / "workflows").glob("*.yml"):
            workflow = workflow_path.read_text(encoding="utf-8")
            assert "permissions:\n  contents: read" in workflow
            assert "concurrency:" in workflow
            assert "timeout-minutes:" in workflow
        assert_external_actions_are_pinned(project_path)
        dependabot = yaml.safe_load(
            (project_path / ".github" / "dependabot.yml").read_text(encoding="utf-8")
        )
        assert {update["package-ecosystem"] for update in dependabot["updates"]} == {
            "github-actions",
            "pip",
        }
        pre_commit = yaml.safe_load(
            (project_path / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        )
        assert [hook["id"] for hook in pre_commit["repos"][0]["hooks"]] == [
            "ruff-check",
            "ruff-format",
        ]
        ruff_check = subprocess.run(
            ["ruff", "check", "."],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert ruff_check.returncode == 0, ruff_check.stdout + ruff_check.stderr
        subprocess.run(
            ["ruff", "format", "--check", "."],
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True,
        )
    else:
        assert metadata["project"]["dependencies"] == expected_runtime_dependencies(
            BASE_CONTEXT | overrides,
        )
        assert "license" not in optional_dependencies
        assert "quality" not in optional_dependencies
        assert "release" not in optional_dependencies
        assert "licensecheck" not in metadata.get("tool", {})
        assert "ruff" not in metadata.get("tool", {})
        assert "api" not in optional_dependencies
        assert "scripts" not in metadata["project"]
        assert "license-files" not in metadata["project"]
    rendered_context = BASE_CONTEXT | overrides
    if rendered_context["test_types"]["entries"]:
        assert optional_dependencies["test"] == expected_test_dependencies(
            rendered_context,
        )
    documentation_types = overrides.get(
        "documentation_types",
        BASE_CONTEXT["documentation_types"],
    )
    if not documentation_types["entries"]:
        assert "docs" not in optional_dependencies
    assert [author["name"] for author in metadata["project"]["authors"]] == [
        "Ada Lovelace",
        "Grace Hopper",
    ]
    assert [
        maintainer["name"] for maintainer in metadata["project"]["maintainers"]
    ] == [
        "Ada Lovelace",
        "Research Software Team",
    ]
    expected_urls = {
        "Source Code": "https://github.com/LUMC-DCC/research-template-demo",
        "Homepage": "https://example.org/research-template-demo",
        "Documentation": "https://lumc-dcc.github.io/research-template-demo",
        "Issue Tracker": "https://github.com/LUMC-DCC/research-template-demo/issues",
        "Funding": "https://example.org/grants/lumc-2024-001",
    }
    if "CHANGELOG.md" in rendered_context["community_files"]["entries"]:
        expected_urls["Changelog"] = (
            "https://github.com/LUMC-DCC/research-template-demo/blob/HEAD/CHANGELOG.md"
        )
    if "GitHub Releases" in rendered_context["distribution_channels"]["entries"]:
        expected_urls["Release Notes"] = (
            "https://github.com/LUMC-DCC/research-template-demo/releases"
        )
    if "PyPI" in rendered_context["distribution_channels"]["entries"]:
        expected_urls["Download"] = f"https://pypi.org/project/{expected_name}/#files"
    assert metadata["project"]["urls"] == expected_urls
    licensing = overrides.get("licensing", BASE_CONTEXT["licensing"])
    if licensing["license"]:
        license_text = (project_path / "LICENSE").read_text(encoding="utf-8")
        if licensing["license"] == "MIT":
            assert license_text == f"{SPDX_LICENSE_TEXT}\n"


def test_python_readme_badges_follow_available_project_metadata(
    tmp_path,
    monkeypatch,
):
    """Ensure README badges are derived from generated capabilities."""
    project_path = render_python_project(tmp_path, monkeypatch)
    readme = (project_path / "README.md").read_text(encoding="utf-8")

    assert (
        "https://github.com/LUMC-DCC/research-template-demo/actions/workflows/tests.yml/badge.svg"
    ) in readme
    assert "![Documentation]" in readme
    assert "img.shields.io/github/v/release/LUMC-DCC/research-template-demo" in readme
    assert "img.shields.io/pypi/v/research-template-demo" in readme
    assert "zenodo.org/badge/DOI/10.5281/zenodo.12345.svg" in readme
    assert "![Tool Type]" in readme


def test_python_zenodo_channel_generates_release_metadata(
    tmp_path,
    monkeypatch,
):
    """Ensure Zenodo selection writes complete GitHub release metadata."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        distribution_channels={"entries": ["Zenodo"]},
        funding={
            "entries": [
                {
                    "funder": "European Commission",
                    "award_number": "777541",
                },
                {
                    "funder": "LUMC",
                    "award_number": "LUMC-2024-001",
                },
            ]
        },
    )

    metadata = json.loads((project_path / ".zenodo.json").read_text())
    assert metadata["title"] == "Research Template Demo"
    assert metadata["upload_type"] == "software"
    assert metadata["access_right"] == "open"
    assert metadata["license"] == "MIT"
    assert metadata["creators"][0] == {
        "name": "Lovelace, Ada",
        "affiliation": "Leiden University Medical Center",
        "orcid": "0000-0002-1825-0097",
    }
    assert metadata["contributors"] == [
        {"name": "Research Software Team", "type": "ContactPerson"},
        {
            "name": "Katherine Johnson",
            "affiliation": "Leiden University Medical Center",
            "type": "ProjectLeader",
        },
    ]
    assert metadata["grants"] == [{"id": "777541"}]
    assert metadata["related_identifiers"][0] == {
        "identifier": "10.1234/example",
        "relation": "isDocumentedBy",
        "scheme": "doi",
        "resource_type": "publication-article",
    }


@pytest.mark.parametrize(
    ("project_manager", "setup_text", "run_prefix", "tool_config"),
    [
        ("uv", "uv sync --all-extras", "uv run ", None),
        ("poetry", "poetry install --all-extras", "poetry run ", None),
        ("pdm", "pdm install -G :all", "pdm run ", "pdm"),
        ("hatch", "hatch env create", "hatch run ", "hatch"),
        ("pixi", "prefix-dev/setup-pixi@", "pixi run ", "pixi"),
        (
            "pip",
            'python -m pip install -e ".[license,api,test,quality,release,docs]"',
            "",
            None,
        ),
    ],
)
def test_python_project_manager_controls_setup_and_commands(
    tmp_path,
    monkeypatch,
    project_manager,
    setup_text,
    run_prefix,
    tool_config,
):
    """Ensure each supported manager controls setup without shipping a lockfile.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Temporary generation directory.
    monkeypatch : pytest.MonkeyPatch
        Fixture used by the generation helper.
    project_manager : str
        Selected project-manager value.
    setup_text : str
        Manager-specific setup text expected in generated files.
    run_prefix : str
        Native command prefix expected in generated workflows.
    tool_config : str or None
        Expected project-manager table under ``tool`` when configuration is needed.
    """
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug=f"{project_manager}_manager_demo",
        project_manager=project_manager,
    )
    assert_no_template_artifacts(project_path)

    action = (
        project_path / ".github" / "actions" / "setup-python-project" / "action.yml"
    ).read_text(encoding="utf-8")
    tests_workflow = (project_path / ".github" / "workflows" / "tests.yml").read_text(
        encoding="utf-8"
    )
    contributing = (project_path / "CONTRIBUTING.md").read_text(encoding="utf-8")
    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())

    action_config = yaml.safe_load(action)
    assert action_config["name"] == "Set up Python project"
    assert "inputs" not in action_config
    if project_manager != "pixi":
        setup_python = next(
            step
            for step in action_config["runs"]["steps"]
            if step.get("uses", "").startswith("actions/setup-python@")
        )
        assert setup_python["with"] == {"python-version-file": "pyproject.toml"}
    assert setup_text in action or setup_text in contributing
    assert f"run: {run_prefix}python -m pytest" in tests_workflow
    assert "## Development setup" in contributing
    if tool_config:
        assert tool_config in pyproject["tool"]

    for lockfile in (
        "uv.lock",
        "poetry.lock",
        "pdm.lock",
        "pixi.lock",
        "pylock.toml",
    ):
        assert not (project_path / lockfile).exists()


def test_python_containerization_generates_composable_recipes_and_ci(
    tmp_path,
    monkeypatch,
):
    """Ensure all supported container recipes compose in one project."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="container_demo",
        containerization={
            "entries": [
                {"type": "Docker"},
                {"type": "OCI / Podman"},
                {"type": "Apptainer / Singularity"},
            ],
        },
        distribution_channels={
            "entries": [
                "GitHub Container Registry",
                "Docker Hub",
            ],
        },
    )

    dockerfile = (project_path / "Dockerfile").read_text(encoding="utf-8")
    containerfile = (project_path / "Containerfile").read_text(encoding="utf-8")
    apptainer = (project_path / "Apptainer.def").read_text(encoding="utf-8")
    workflow = (project_path / ".github" / "workflows" / "containers.yml").read_text(
        encoding="utf-8"
    )

    assert yaml.safe_load(workflow)["name"] == "Containers"
    assert dockerfile == containerfile
    assert "FROM python:3.12-slim AS builder" in dockerfile
    assert "USER appuser" in dockerfile
    assert "CONTAINER_DEMO_SERVER_HOST=0.0.0.0" in dockerfile
    assert 'CMD ["container-demo-serve"]' in dockerfile
    assert "SERVER_PORT=8000WORKDIR" not in dockerfile
    assert "\n \\\n" not in dockerfile
    assert "Bootstrap: docker" in apptainer
    assert "%test" in apptainer
    assert "CONTAINER_DEMO_SERVER_HOST=0.0.0.0" in apptainer
    assert "exec container-demo-serve" in apptainer
    assert "- Dockerfile" in workflow
    assert "- Containerfile" in workflow
    assert "apptainer build --fakeroot container_demo.sif" in workflow
    assert "publish-ghcr:" in workflow
    assert "publish-docker-hub:" in workflow
    assert not (project_path / ".github" / "workflows" / "distribution.yml").exists()
    assert (
        "release"
        not in tomllib.loads(
            (project_path / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]["optional-dependencies"]
    )


def test_python_release_policy_drives_docs_checks_and_distribution_ci(
    tmp_path,
    monkeypatch,
):
    """Ensure release fields drive generated policy and package publishing."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="release_demo",
        versioning={
            "version": "2026.8",
            "scheme": "CalVer",
            "scheme_details": "YYYY.MM",
            "release_frequency": "After each major feature",
        },
        distribution_channels={
            "entries": [
                "PyPI",
                "GitHub Releases",
                "conda-forge",
            ],
        },
    )

    release_docs = (project_path / "docs" / "release.md").read_text(encoding="utf-8")
    changelog = (project_path / "CHANGELOG.md").read_text(encoding="utf-8")
    workflow = (project_path / ".github" / "workflows" / "distribution.yml").read_text(
        encoding="utf-8"
    )
    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())

    assert yaml.safe_load(workflow)["name"] == "Distribution"
    assert "`pyproject.toml` is the source of truth" in release_docs
    assert "| Versioning scheme | CalVer |" in release_docs
    assert "| Versioning details | YYYY.MM |" in release_docs
    assert "This project uses CalVer for versions." in changelog
    assert "Policy details: YYYY.MM" in changelog
    assert "| Expected cadence | After each major feature |" in release_docs
    assert "- PyPI" in release_docs
    assert "- GitHub Releases" in release_docs
    assert "- conda-forge" in release_docs
    assert "trusted publisher" in release_docs
    assert "publish-pypi:" in workflow
    assert "publish-github-release:" in workflow
    assert "python tools/check_release.py --tag" in workflow
    assert pyproject["project"]["optional-dependencies"]["release"] == [
        "build",
        "packaging",
        "twine",
    ]

    valid_release = subprocess.run(
        [sys.executable, "tools/check_release.py", "--tag", "v2026.8"],
        cwd=project_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert valid_release.returncode == 0
    assert "Release metadata is valid" in valid_release.stdout


def test_python_test_types_select_sample_test_files(tmp_path, monkeypatch):
    """Ensure selected SMP test types control generated sample tests."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="selected_tests_demo",
        interfaces={"entries": []},
        test_types={
            "entries": [
                "Smoke tests",
                "Property-based / fuzz",
            ],
        },
    )

    assert (project_path / "tests" / "test_smoke.py").exists()
    assert (project_path / "tests" / "test_property.py").exists()
    assert_selected_test_files(
        project_path,
        {"Smoke tests", "Property-based / fuzz"},
    )

    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    assert pyproject["project"]["optional-dependencies"]["test"] == [
        "pytest",
        "hypothesis",
    ]


def test_python_test_framework_defaults_to_supported_pytest(tmp_path, monkeypatch):
    """Ensure Python test commands keep using the supported pytest scaffold."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="pytest_framework_demo",
        test_frameworks={"entries": ["unittest"]},
    )

    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    workflow = (project_path / ".github" / "workflows" / "tests.yml").read_text(
        encoding="utf-8"
    )

    assert "pytest" in pyproject["project"]["optional-dependencies"]["test"]
    assert "python -m pytest" in workflow


def test_python_quality_tool_defaults_render_ruff_and_pre_commit(
    tmp_path,
    monkeypatch,
):
    """Ensure Python quality defaults render Ruff and pre-commit scaffolds."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="quality_defaults_demo",
    )

    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    pre_commit = (project_path / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    workflow = (project_path / ".github" / "workflows" / "quality.yml").read_text(
        encoding="utf-8"
    )

    assert pyproject["project"]["optional-dependencies"]["quality"] == [
        "pre-commit",
        "ruff",
    ]
    assert pyproject["tool"]["ruff"]["lint"]["select"] == [
        "B",
        "E",
        "F",
        "I",
        "SIM",
        "UP",
    ]
    assert "ruff check" in pre_commit
    assert "ruff format --check" in pre_commit
    assert "ruff check ." in workflow
    assert "ruff format --check ." in workflow
    assert "mypy src" not in workflow


def test_python_quality_tool_selectors_render_mypy_when_selected(
    tmp_path,
    monkeypatch,
):
    """Ensure Python type-checking selection adds Mypy checks."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="quality_mypy_demo",
        quality_tools={
            **BASE_CONTEXT["quality_tools"],
            "type_checker": "mypy",
        },
    )

    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    pre_commit = (project_path / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    workflow = (project_path / ".github" / "workflows" / "quality.yml").read_text(
        encoding="utf-8"
    )

    rendered_context = BASE_CONTEXT | {
        "quality_tools": {
            **BASE_CONTEXT["quality_tools"],
            "type_checker": "mypy",
        },
    }
    assert pyproject["project"]["optional-dependencies"]["quality"] == (
        expected_quality_dependencies(rendered_context)
    )
    assert pyproject["tool"]["mypy"]["strict"] is True
    assert "python_version" not in pyproject["tool"]["mypy"]
    assert "mypy src" in pre_commit
    assert "mypy src" in workflow


@pytest.mark.parametrize(
    ("project_slug", "formatter_tool", "linter_tool", "expected_command"),
    [
        (
            "formatter_only_demo",
            "ruff",
            "",
            "ruff format --check",
        ),
        (
            "linter_only_demo",
            "",
            "ruff",
            "ruff check",
        ),
    ],
)
def test_python_quality_selectors_keep_responsibilities_independent(
    tmp_path,
    monkeypatch,
    project_slug,
    formatter_tool,
    linter_tool,
    expected_command,
):
    """Ensure formatter and linter selections render independent commands.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Pytest temporary directory.
    monkeypatch : pytest.MonkeyPatch
        Fixture used to isolate Cookiecutter's home and replay directories.
    project_slug : str
        Slug for the generated project.
    formatter_tool : str
        Requested formatter selector value.
    linter_tool : str
        Requested linter selector value.
    expected_command : str
        Quality command expected in generated local and CI configuration.
    """
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug=project_slug,
        quality_tools={
            "formatter": formatter_tool,
            "linter": linter_tool,
            "type_checker": "",
        },
    )

    pre_commit = (project_path / ".pre-commit-config.yaml").read_text(
        encoding="utf-8",
    )
    workflow = (project_path / ".github" / "workflows" / "quality.yml").read_text(
        encoding="utf-8"
    )

    assert expected_command in pre_commit
    assert expected_command in workflow
    if not formatter_tool:
        assert "ruff format --check" not in pre_commit
        assert "ruff format --check" not in workflow
    if not linter_tool:
        assert "ruff check" not in pre_commit
        assert "ruff check ." not in workflow


def test_python_quality_tools_can_be_omitted(tmp_path, monkeypatch):
    """Ensure empty quality selectors remove quality scaffolding."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="no_quality_demo",
        quality_tools={"formatter": "", "linter": "", "type_checker": ""},
    )

    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())

    assert "quality" not in pyproject["project"]["optional-dependencies"]
    assert "ruff" not in pyproject.get("tool", {})
    assert "mypy" not in pyproject.get("tool", {})
    assert not (project_path / ".pre-commit-config.yaml").exists()
    assert not (project_path / ".github" / "workflows" / "quality.yml").exists()


@pytest.mark.parametrize(
    (
        "project_slug",
        "interfaces",
        "test_types",
        "present",
        "absent",
    ),
    [
        (
            "plugin_portal_unit_demo",
            [
                {"type": "Plug-in"},
                {"type": "Database portal"},
            ],
            ["Smoke tests", "Unit tests"],
            [
                "src/plugin_portal_unit_demo/adapters/plugin/registry.py",
                "src/plugin_portal_unit_demo/adapters/plugin/hooks.py",
                "src/plugin_portal_unit_demo/adapters/portal/app.py",
                "src/plugin_portal_unit_demo/adapters/portal/routes/index.py",
                "src/plugin_portal_unit_demo/adapters/portal/routes/records.py",
            ],
            [
                "src/plugin_portal_unit_demo/adapters/api",
                "src/plugin_portal_unit_demo/adapters/cli",
                "scripts",
            ],
        ),
        (
            "cli_script_integration_demo",
            [
                {"type": "Command-line tool"},
                {"type": "Script"},
            ],
            ["Integration tests", "System / end-to-end tests"],
            [
                "src/cli_script_integration_demo/adapters/cli/app.py",
                "src/cli_script_integration_demo/adapters/cli/commands/process.py",
                "scripts/run_example.py",
            ],
            [
                "src/cli_script_integration_demo/adapters/api",
                "src/cli_script_integration_demo/adapters/portal",
                "src/cli_script_integration_demo/adapters/plugin",
            ],
        ),
        (
            "library_property_demo",
            [
                {"type": "Library"},
            ],
            ["Regression tests", "Property-based / fuzz"],
            [
                "src/library_property_demo/__init__.py",
                "src/library_property_demo/services/processing.py",
            ],
            [
                "src/library_property_demo/adapters",
                "scripts",
            ],
        ),
    ],
)
def test_python_interface_and_test_type_subsets_compose(
    tmp_path,
    monkeypatch,
    project_slug,
    interfaces,
    test_types,
    present,
    absent,
):
    """Ensure interface and test-type subsets render independently."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug=project_slug,
        interfaces={"entries": interfaces},
        test_types={"entries": test_types},
    )

    assert_no_template_artifacts(project_path)
    assert_selected_test_files(project_path, set(test_types))

    for rel_path in present:
        assert (project_path / rel_path).exists(), rel_path
    for rel_path in absent:
        assert not (project_path / rel_path).exists(), rel_path

    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    rendered_context = BASE_CONTEXT | {
        "interfaces": {"entries": interfaces},
        "test_types": {"entries": test_types},
    }
    assert pyproject["project"]["optional-dependencies"]["test"] == (
        expected_test_dependencies(rendered_context)
    )

    if project_slug == "plugin_portal_unit_demo":
        env = os.environ | {
            "PYTHONPATH": str(project_path / "src"),
        }
        result = subprocess.run(
            [sys.executable, "-m", "pytest"],
            cwd=project_path,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, result.stdout + result.stderr


def test_python_license_compatibility_check_controls_ci_and_config(
    tmp_path, monkeypatch
):
    """Ensure license compatibility checking controls Python CI and tooling."""
    project_path = render_python_project(tmp_path, monkeypatch)

    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    workflow = (
        project_path / ".github" / "workflows" / "license-compatibility.yml"
    ).read_text(encoding="utf-8")

    assert pyproject["project"]["optional-dependencies"]["license"] == ["licensecheck"]
    assert pyproject["tool"]["licensecheck"] == {
        "license": "MIT",
        "format": "simple",
        "zero": True,
    }
    assert "uses: ./.github/actions/setup-python-project" in workflow
    assert "run: uv run licensecheck" in workflow
    assert "licensecheck" in workflow


def test_python_license_compatibility_check_can_be_disabled(tmp_path, monkeypatch):
    """Ensure license compatibility files are omitted when disabled."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="license_check_disabled_demo",
        licensing={"license": "MIT", "compatibility_check": ""},
    )

    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())

    assert "license" not in pyproject["project"]["optional-dependencies"]
    assert "licensecheck" not in pyproject.get("tool", {})
    assert not (
        project_path / ".github" / "workflows" / "license-compatibility.yml"
    ).exists()


def test_python_operating_systems_render_platform_metadata_and_ci(
    tmp_path, monkeypatch
):
    """Ensure operating-system entries render as support and CI metadata."""
    project_path = render_python_project(tmp_path, monkeypatch)

    readme = (project_path / "README.md").read_text(encoding="utf-8")
    docs_overview = (project_path / "docs" / "overview.md").read_text(encoding="utf-8")
    docs_usage = (project_path / "docs" / "usage.md").read_text(encoding="utf-8")
    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    codemeta = json.loads((project_path / "codemeta.json").read_text())
    tests_workflow = yaml.safe_load(
        (project_path / ".github" / "workflows" / "tests.yml").read_text(
            encoding="utf-8"
        )
    )

    for content in (readme, docs_overview, docs_usage):
        assert "## Platform support" in content
        assert "- Linux >=Ubuntu 22.04 - Officially supported" in content
        assert "- macOS >=13 - Officially supported" in content
        assert "- Windows - Expected to work" in content

    assert codemeta["operatingSystem"] == [
        "Linux >=Ubuntu 22.04",
        "macOS >=13",
        "Windows",
    ]
    assert pyproject["project"]["classifiers"] == [
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ]
    assert tests_workflow["jobs"]["tests"]["strategy"]["matrix"]["os"] == [
        "ubuntu-latest",
        "macos-latest",
    ]
    assert "windows-latest" not in (
        project_path / ".github" / "workflows" / "tests.yml"
    ).read_text(encoding="utf-8")


def test_python_external_dependencies_render_docs_and_codemeta(tmp_path, monkeypatch):
    """Ensure external dependencies render as docs and CodeMeta metadata."""
    project_path = render_python_project(tmp_path, monkeypatch)

    readme = (project_path / "README.md").read_text(encoding="utf-8")
    docs_overview = (project_path / "docs" / "overview.md").read_text(encoding="utf-8")
    docs_usage = (project_path / "docs" / "usage.md").read_text(encoding="utf-8")
    codemeta = json.loads((project_path / "codemeta.json").read_text())

    graphviz_line = (
        "- [Graphviz >=9](https://graphviz.org/) - Diagram rendering for reports; "
        "license: EPL-1.0"
    )
    edam_line = (
        "- [EDAM ontology](https://edamontology.org/) - "
        "Controlled vocabulary for function metadata; license: CC-BY-SA-4.0"
    )
    assert "## External dependencies" not in readme
    for content in (docs_overview, docs_usage):
        assert "## External dependencies" in content
        assert graphviz_line in content
        assert edam_line in content

    assert codemeta["softwareRequirements"] == [
        {
            "@type": "SoftwareSourceCode",
            "@id": "https://graphviz.org/",
            "name": "Graphviz",
            "url": "https://graphviz.org/",
            "version": ">=9",
            "license": "https://spdx.org/licenses/EPL-1.0",
            "description": "Diagram rendering for reports",
        },
        {
            "@type": "SoftwareSourceCode",
            "@id": "https://edamontology.org/",
            "name": "EDAM ontology",
            "url": "https://edamontology.org/",
            "license": "https://spdx.org/licenses/CC-BY-SA-4.0",
            "description": "Controlled vocabulary for function metadata",
        },
    ]


def test_python_external_services_render_generated_docs_only(tmp_path, monkeypatch):
    """Ensure external services render to docs without expanding README."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        documentation_types={"entries": ["user", "deployment"]},
    )

    readme = (project_path / "README.md").read_text(encoding="utf-8")
    docs_overview = (project_path / "docs" / "overview.md").read_text(encoding="utf-8")
    docs_deployment = (project_path / "docs" / "deployment.md").read_text(
        encoding="utf-8"
    )

    dcc_line = (
        "- DCC consultancy - provider: LUMC DCC; type: "
        "Institutional support (DCC, IT, library), Domain expertise; "
        "quantity: 0.1 FTE during first release; "
        "cost coverage: Departmental overhead"
    )
    ci_line = (
        "- Hosted CI minutes - provider: GitHub Actions; type: CI / CD minutes; "
        "quantity: Standard hosted runner quota; cost coverage: Free tier"
    )

    assert "## External services" not in readme
    for content in (docs_overview, docs_deployment):
        assert "## External services" in content
        assert dcc_line in content
        assert ci_line in content


@pytest.mark.parametrize(
    ("project_slug", "interfaces", "security_measures", "expected"),
    [
        (
            "http_config_demo",
            {"entries": [{"type": "Web API"}]},
            {"selected": {"entries": []}, "additional": ""},
            True,
        ),
        (
            "secure_config_demo",
            {"entries": [{"type": "Script"}]},
            {
                "selected": {
                    "entries": [
                        "Secrets management (e.g., environment variables, vault)"
                    ]
                },
                "additional": "",
            },
            True,
        ),
        (
            "lean_library_demo",
            {"entries": [{"type": "Library"}]},
            {"selected": {"entries": []}, "additional": ""},
            False,
        ),
    ],
)
def test_python_runtime_configuration_follows_selected_capabilities(
    tmp_path,
    monkeypatch,
    project_slug,
    interfaces,
    security_measures,
    expected,
):
    """Ensure runtime settings are included only for relevant capabilities."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug=project_slug,
        interfaces=interfaces,
        security_measures=security_measures,
    )

    config_path = project_path / "src" / project_slug / "config.py"
    logging_path = project_path / "src" / project_slug / "logging_config.py"
    env_example_path = project_path / ".env.example"
    assert config_path.exists() is expected
    assert logging_path.exists() is expected
    assert env_example_path.exists() is expected

    context = BASE_CONTEXT | {
        "interfaces": interfaces,
        "security_measures": security_measures,
    }
    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    assert pyproject["project"]["dependencies"] == expected_runtime_dependencies(
        context,
    )
    if expected:
        env_example = env_example_path.read_text(encoding="utf-8")
        assert f"{project_slug.upper()}_LOG_LEVEL=INFO" in env_example
        assert "SECRET=" not in env_example
        assert "logging.getLogger" in logging_path.read_text(encoding="utf-8")
    is_http = interfaces["entries"][0]["type"] in {
        "Bioinformatics portal",
        "Database portal",
        "SPARQL endpoint",
        "Web API",
        "Web application",
        "Web service",
        "Workbench",
    }
    server_runner_path = (
        project_path / "src" / project_slug / "adapters" / "server_runner.py"
    )
    assert server_runner_path.exists() is is_http
    if is_http:
        env_example = env_example_path.read_text(encoding="utf-8")
        assert f"{project_slug.upper()}_SERVER_HOST=127.0.0.1" in env_example
        assert f"{project_slug.upper()}_SERVER_PORT=8000" in env_example
        runner = server_runner_path.read_text(encoding="utf-8")
        for setting in (
            "settings.server_host",
            "settings.server_port",
            "settings.server_root_path",
            "settings.server_reload",
            "settings.log_level.lower()",
        ):
            assert setting in runner


def test_python_interfaces_keep_matching_code_scaffolds(tmp_path, monkeypatch):
    """Ensure interface entries control matching Python code scaffolds."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="interface_scaffold_demo",
        interfaces={
            "entries": [
                {
                    "type": "Command-line tool",
                    "specification": "CLI for local usage",
                    "status": "Stable",
                },
                {
                    "type": "Web API",
                    "specification": "HTTP API for service usage",
                    "status": "Experimental",
                },
                {
                    "type": "Script",
                    "specification": "Batch script for scheduled usage",
                    "status": "Experimental",
                },
            ],
        },
    )

    assert (
        project_path / "src" / "interface_scaffold_demo" / "adapters" / "cli" / "app.py"
    ).exists()
    assert (
        project_path / "src" / "interface_scaffold_demo" / "adapters" / "api" / "app.py"
    ).exists()
    assert (project_path / "scripts" / "run_example.py").exists()

    metadata = tomllib.loads((project_path / "pyproject.toml").read_text())
    assert metadata["project"]["optional-dependencies"]["api"] == [
        "fastapi",
        "uvicorn[standard]",
    ]
    assert metadata["project"]["dependencies"] == expected_runtime_dependencies(
        BASE_CONTEXT
        | {
            "interfaces": {
                "entries": [
                    {"type": "Command-line tool"},
                    {"type": "Web API"},
                    {"type": "Script"},
                ]
            }
        },
    )
    assert metadata["project"]["scripts"] == {
        "interface-scaffold-demo": "interface_scaffold_demo.adapters.cli.app:main",
        "interface-scaffold-demo-serve": (
            "interface_scaffold_demo.adapters.server_runner:main"
        ),
    }


@pytest.mark.parametrize(
    ("interface_type", "is_http"),
    [
        ("Bioinformatics portal", True),
        ("Command-line tool", False),
        ("Database portal", True),
        ("Desktop application", False),
        ("Library", False),
        ("Ontology", False),
        ("Plug-in", False),
        ("Script", False),
        ("SPARQL endpoint", True),
        ("Suite", False),
        ("Web application", True),
        ("Web API", True),
        ("Web service", True),
        ("Workbench", True),
        ("Workflow", False),
    ],
)
def test_python_each_canonical_interface_renders_independently(
    tmp_path,
    monkeypatch,
    interface_type,
    is_http,
):
    """Ensure every canonical interface is a valid standalone selection."""
    project_slug = re.sub(r"[^a-z0-9]+", "_", interface_type.lower()).strip("_")
    interfaces = {"entries": [{"type": interface_type}]}
    security_measures = {"selected": {"entries": []}, "additional": ""}
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug=project_slug,
        interfaces=interfaces,
        security_measures=security_measures,
    )

    assert_no_template_artifacts(project_path)
    for source_path in (project_path / "src").rglob("*.py"):
        compile(source_path.read_text(encoding="utf-8"), str(source_path), "exec")

    config_path = project_path / "src" / project_slug / "config.py"
    logging_path = project_path / "src" / project_slug / "logging_config.py"
    server_runner_path = (
        project_path / "src" / project_slug / "adapters" / "server_runner.py"
    )
    assert config_path.exists() is is_http
    assert logging_path.exists() is is_http
    assert server_runner_path.exists() is is_http

    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    context = BASE_CONTEXT | {
        "interfaces": interfaces,
        "security_measures": security_measures,
    }
    assert pyproject["project"]["dependencies"] == expected_runtime_dependencies(
        context
    )

    expected_scripts = {}
    command_name = project_slug.replace("_", "-")
    if interface_type == "Command-line tool":
        expected_scripts[command_name] = f"{project_slug}.adapters.cli.app:main"
    if is_http:
        expected_scripts[f"{command_name}-serve"] = (
            f"{project_slug}.adapters.server_runner:main"
        )
    assert pyproject["project"].get("scripts", {}) == expected_scripts

    env = os.environ | {"PYTHONPATH": str(project_path / "src")}
    generated_tests = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=project_path,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert generated_tests.returncode == 0, (
        generated_tests.stdout + generated_tests.stderr
    )


def test_python_canonical_tool_types_select_expected_scaffolds(tmp_path, monkeypatch):
    """Ensure all canonical tool types map to Python scaffold families."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="canonical_interfaces_demo",
        interfaces={
            "entries": [
                {"type": "Bioinformatics portal"},
                {"type": "Command-line tool"},
                {"type": "Database portal"},
                {"type": "Desktop application"},
                {"type": "Library"},
                {"type": "Ontology"},
                {"type": "Plug-in"},
                {"type": "Script"},
                {"type": "SPARQL endpoint"},
                {"type": "Suite"},
                {"type": "Web application"},
                {"type": "Web API"},
                {"type": "Web service"},
                {"type": "Workbench"},
                {"type": "Workflow"},
            ],
        },
    )

    expected_paths = [
        "scripts/run_example.py",
        "src/canonical_interfaces_demo/adapters/api/app.py",
        "src/canonical_interfaces_demo/adapters/api/routes/health.py",
        "src/canonical_interfaces_demo/adapters/api/routes/processing.py",
        "src/canonical_interfaces_demo/adapters/api/routes/sparql.py",
        "src/canonical_interfaces_demo/adapters/api/schemas.py",
        "src/canonical_interfaces_demo/adapters/server.py",
        "src/canonical_interfaces_demo/adapters/server_runner.py",
        "src/canonical_interfaces_demo/adapters/soap/app.py",
        "src/canonical_interfaces_demo/adapters/soap/service.py",
        "src/canonical_interfaces_demo/adapters/cli/app.py",
        "src/canonical_interfaces_demo/adapters/cli/commands/process.py",
        "src/canonical_interfaces_demo/adapters/desktop/app.py",
        "src/canonical_interfaces_demo/adapters/desktop/view_model.py",
        "src/canonical_interfaces_demo/adapters/plugin/hooks.py",
        "src/canonical_interfaces_demo/adapters/plugin/registry.py",
        "src/canonical_interfaces_demo/adapters/portal/app.py",
        "src/canonical_interfaces_demo/adapters/portal/models.py",
        "src/canonical_interfaces_demo/adapters/portal/repository.py",
        "src/canonical_interfaces_demo/adapters/portal/routes/index.py",
        "src/canonical_interfaces_demo/adapters/portal/routes/records.py",
        "src/canonical_interfaces_demo/adapters/portal/summary.py",
        "src/canonical_interfaces_demo/adapters/portal/views.py",
        "src/canonical_interfaces_demo/adapters/suite/commands.py",
        "src/canonical_interfaces_demo/adapters/suite/runner.py",
        "src/canonical_interfaces_demo/adapters/web/app.py",
        "src/canonical_interfaces_demo/adapters/web/routes/index.py",
        "src/canonical_interfaces_demo/adapters/web/views.py",
        "src/canonical_interfaces_demo/ontology/metadata.py",
        "src/canonical_interfaces_demo/ontology/graph.py",
        "src/canonical_interfaces_demo/ontology/namespaces.py",
        "src/canonical_interfaces_demo/ontology/serializers.py",
        "src/canonical_interfaces_demo/ontology/terms.py",
        "src/canonical_interfaces_demo/ontology/validation.py",
        "src/canonical_interfaces_demo/services/processing.py",
        "src/canonical_interfaces_demo/workflows/config.py",
        "src/canonical_interfaces_demo/workflows/io.py",
        "src/canonical_interfaces_demo/workflows/pipeline.py",
        "src/canonical_interfaces_demo/workflows/steps.py",
        "workflows/README.md",
        "workflows/definitions/README.md",
        "workflows/examples/example_input.txt",
    ]
    for rel_path in expected_paths:
        assert (project_path / rel_path).exists(), rel_path

    # Parse every generated module so option composition cannot emit invalid Python.
    for source_path in (project_path / "src").rglob("*.py"):
        compile(
            source_path.read_text(encoding="utf-8"),
            str(source_path),
            "exec",
        )

    server_module = (
        project_path / "src/canonical_interfaces_demo/adapters/server.py"
    ).read_text(encoding="utf-8")
    assert 'app.mount("/api", api_app' in server_module
    assert 'app.mount("/soap", soap_app' in server_module
    assert 'app.mount("/portal", portal_app' in server_module
    assert 'app.mount("/", web_app' in server_module

    implementation_free_packages = [
        "src/canonical_interfaces_demo/adapters/cli/__init__.py",
        "src/canonical_interfaces_demo/adapters/desktop/__init__.py",
        "src/canonical_interfaces_demo/adapters/plugin/__init__.py",
        "src/canonical_interfaces_demo/adapters/portal/__init__.py",
        "src/canonical_interfaces_demo/adapters/suite/__init__.py",
        "src/canonical_interfaces_demo/adapters/web/__init__.py",
        "src/canonical_interfaces_demo/ontology/__init__.py",
        "src/canonical_interfaces_demo/workflows/__init__.py",
    ]
    for rel_path in implementation_free_packages:
        content = (project_path / rel_path).read_text(encoding="utf-8")
        assert "def " not in content
        assert "class " not in content

    wiring_modules = [
        "src/canonical_interfaces_demo/adapters/web/app.py",
        "src/canonical_interfaces_demo/adapters/portal/app.py",
    ]
    for rel_path in wiring_modules:
        content = (project_path / rel_path).read_text(encoding="utf-8")
        assert "@app." not in content
        assert "@web." not in content
        assert "@portal." not in content

    metadata = tomllib.loads((project_path / "pyproject.toml").read_text())
    optional_dependencies = metadata["project"]["optional-dependencies"]
    assert metadata["project"]["dependencies"] == [
        "typer",
        "rdflib",
        "pydantic-settings",
    ]
    assert optional_dependencies["api"] == ["fastapi", "uvicorn[standard]"]
    assert optional_dependencies["soap"] == [
        "a2wsgi",
        "fastapi",
        "lxml",
        (
            "spyne @ https://github.com/arskom/spyne/archive/"
            "af96bf95feb7950617640671f8aba9654f31acd3.tar.gz"
        ),
        "uvicorn[standard]",
    ]
    assert optional_dependencies["web"] == ["fastapi", "uvicorn[standard]"]
    assert metadata["tool"]["hatch"]["metadata"] == {"allow-direct-references": True}
    assert metadata["project"]["entry-points"] == {
        "canonical_interfaces_demo.plugins": {
            "example": "canonical_interfaces_demo.adapters.plugin.registry:get_plugin",
        },
    }
    assert metadata["project"]["gui-scripts"] == {
        "canonical-interfaces-demo-desktop": (
            "canonical_interfaces_demo.adapters.desktop.app:main"
        ),
    }
    assert metadata["project"]["scripts"] == {
        "canonical-interfaces-demo": (
            "canonical_interfaces_demo.adapters.cli.app:main"
        ),
        "canonical-interfaces-demo-serve": (
            "canonical_interfaces_demo.adapters.server_runner:main"
        ),
    }
    integration_tests = (project_path / "tests/test_integration.py").read_text(
        encoding="utf-8"
    )
    for test_name in (
        "test_cli_application_processes_a_command",
        "test_api_application_serves_selected_routes",
        "test_portal_application_serves_pages_and_records",
        "test_web_application_serves_a_browser_page",
        "test_combined_server_mounts_selected_http_interfaces",
        "test_soap_application_publishes_wsdl",
        "test_desktop_view_model_processes_without_opening_a_window",
        "test_plugin_registry_returns_a_working_plugin",
        "test_suite_runner_dispatches_a_registered_command",
        "test_ontology_document_is_valid_turtle",
        "test_workflow_pipeline_coordinates_selected_steps",
        "test_example_script_can_run_without_cli_process",
    ):
        assert test_name in integration_tests


def test_python_sparql_endpoint_scaffold_is_route_specific(tmp_path, monkeypatch):
    """Ensure SPARQL endpoints do not inherit process API routes."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="sparql_endpoint_demo",
        interfaces={
            "entries": [
                {"type": "SPARQL endpoint"},
            ],
        },
    )

    routes_dir = (
        project_path / "src" / "sparql_endpoint_demo" / "adapters" / "api" / "routes"
    )
    app_module = (
        project_path / "src" / "sparql_endpoint_demo" / "adapters" / "api" / "app.py"
    ).read_text(encoding="utf-8")

    assert (routes_dir / "health.py").exists()
    assert (routes_dir / "sparql.py").exists()
    assert (
        project_path / "src" / "sparql_endpoint_demo" / "ontology" / "graph.py"
    ).exists()
    assert not (routes_dir / "processing.py").exists()
    assert not (
        project_path
        / "src"
        / "sparql_endpoint_demo"
        / "adapters"
        / "api"
        / "schemas.py"
    ).exists()
    assert "sparql.router" in app_module
    assert "processing.router" not in app_module

    sparql_route = (routes_dir / "sparql.py").read_text(encoding="utf-8")
    metadata = tomllib.loads((project_path / "pyproject.toml").read_text())
    assert metadata["project"]["dependencies"] == ["rdflib", "pydantic-settings"]
    assert "ontology_graph" in sparql_route
    assert "graph.query(query)" in sparql_route


@pytest.mark.parametrize(
    (
        "documentation_builder",
        "present",
        "absent",
        "docs_dependencies",
        "docs_build_command",
    ),
    [
        (
            "mkdocs",
            [
                "docs/index.md",
                "docs/overview.md",
                "docs/resource-requirements.md",
                "docs/sustainability.md",
                "docs/security-and-data.md",
                "docs/release.md",
                "docs/functions.md",
                "docs/usage.md",
                "docs/developer.md",
                "docs/reference.md",
                "docs/documentation.md",
                "docs/legal.md",
                "docs/hooks.py",
                "docs/.pages",
                "mkdocs.yml",
            ],
            [
                "docs/index.rst",
                "docs/conf.py",
                "docs/source/conf.py",
                "docs/Makefile",
                "docs/make.bat",
                "docs/deployment.md",
                "zensical.toml",
            ],
            [
                "mkdocs",
                "mkdocs-awesome-pages-plugin",
                "mkdocs-material",
                "pymdown-extensions",
                "mkdocstrings[python]",
            ],
            "mkdocs build --strict",
        ),
        (
            "zensical",
            [
                "docs/index.md",
                "docs/overview.md",
                "docs/resource-requirements.md",
                "docs/sustainability.md",
                "docs/security-and-data.md",
                "docs/release.md",
                "docs/functions.md",
                "docs/usage.md",
                "docs/developer.md",
                "docs/reference.md",
                "docs/documentation.md",
                "docs/legal.md",
                "zensical.toml",
            ],
            [
                "docs/source",
                "docs/hooks.py",
                "docs/.pages",
                "docs/Makefile",
                "docs/make.bat",
                "mkdocs.yml",
            ],
            ["zensical", "mkdocstrings[python]"],
            "zensical build --strict",
        ),
        (
            "sphinx",
            [
                "docs/source/index.md",
                "docs/source/overview.md",
                "docs/source/resource-requirements.md",
                "docs/source/sustainability.md",
                "docs/source/security-and-data.md",
                "docs/source/release.md",
                "docs/source/functions.md",
                "docs/source/usage.md",
                "docs/source/developer.md",
                "docs/source/reference.md",
                "docs/source/documentation.md",
                "docs/source/legal.md",
                "docs/source/conf.py",
                "docs/Makefile",
                "docs/make.bat",
            ],
            [
                "docs/index.md",
                "docs/index.rst",
                "docs/conf.py",
                "docs/hooks.py",
                "docs/source/index.rst",
                "docs/source/deployment.md",
                "mkdocs.yml",
                "zensical.toml",
            ],
            ["myst-parser", "sphinx", "sphinx-book-theme"],
            "sphinx-build -W -b html docs/source docs/build/html",
        ),
        (
            "pkgdown",
            [
                "docs/index.md",
                "docs/overview.md",
                "docs/functions.md",
                "docs/usage.md",
                "docs/developer.md",
                "docs/reference.md",
                "docs/documentation.md",
                "docs/legal.md",
            ],
            [
                "docs/source",
                "docs/hooks.py",
                "docs/Makefile",
                "docs/make.bat",
                "mkdocs.yml",
                "zensical.toml",
                ".github/workflows/docs.yml",
            ],
            [],
            None,
        ),
    ],
)
def test_python_documentation_builder_scaffolds_are_selected(
    tmp_path,
    monkeypatch,
    documentation_builder,
    present,
    absent,
    docs_dependencies,
    docs_build_command,
):
    """Ensure Python docs builders select compatible scaffold files."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug=f"{documentation_builder}_docs_demo",
        documentation_builder=documentation_builder,
    )

    assert_no_template_artifacts(project_path)
    assert not (project_path / "docs" / "_builders").exists()
    assert not (project_path / "docs" / "_shared").exists()

    for rel_path in present:
        assert (project_path / rel_path).exists(), rel_path

    for rel_path in absent:
        assert not (project_path / rel_path).exists(), rel_path

    metadata = tomllib.loads((project_path / "pyproject.toml").read_text())
    optional_dependencies = metadata["project"].get("optional-dependencies", {})
    assert optional_dependencies.get("docs", []) == docs_dependencies
    if docs_build_command:
        docs_workflow = (project_path / ".github" / "workflows" / "docs.yml").read_text(
            encoding="utf-8"
        )
        assert "uses: ./.github/actions/setup-python-project" in docs_workflow
        assert "run: uv run" in docs_workflow
        assert docs_build_command in docs_workflow

    if documentation_builder == "mkdocs":
        mkdocs_config = yaml.safe_load((project_path / "mkdocs.yml").read_text())
        assert mkdocs_config["site_name"] == BASE_CONTEXT["project_name"]
        assert mkdocs_config["theme"]["name"] == "material"
        assert mkdocs_config["hooks"] == ["docs/hooks.py"]
        assert mkdocs_config["plugins"] == [
            "search",
            "awesome-pages",
            {
                "mkdocstrings": {
                    "handlers": {"python": {"paths": ["src"]}},
                }
            },
        ]
        assert "nav" not in mkdocs_config
        reference = (project_path / "docs/reference.md").read_text(encoding="utf-8")
        assert "::: mkdocs_docs_demo" in reference
        assert "mkdocs_docs_demo.services.processing" in reference

        hook_path = project_path / "docs" / "hooks.py"
        spec = importlib.util.spec_from_file_location(
            "generated_mkdocs_hooks", hook_path
        )
        hook = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hook)
        resolved_config = hook.on_config({})
        assert resolved_config["site_name"] == BASE_CONTEXT["project_name"]
        assert (
            resolved_config["site_description"]
            == BASE_CONTEXT["project_long_description"]
        )
        assert resolved_config["repo_url"] == BASE_CONTEXT["urls"]["repository"]
        assert resolved_config["repo_name"] == "research-template-demo"
        pages_config = yaml.safe_load((project_path / "docs" / ".pages").read_text())
        assert pages_config["nav"] == [
            "index.md",
            "overview.md",
            "resource-requirements.md",
            "sustainability.md",
            "security-and-data.md",
            "release.md",
            "functions.md",
            "usage.md",
            "developer.md",
            "reference.md",
            "documentation.md",
            "legal.md",
            "...",
        ]
        build = subprocess.run(
            ["mkdocs", "build", "--strict"],
            cwd=project_path,
            check=False,
            capture_output=True,
            text=True,
        )
        assert build.returncode == 0, build.stdout + build.stderr

    if documentation_builder == "zensical":
        zensical_config = tomllib.loads(
            (project_path / "zensical.toml").read_text(encoding="utf-8")
        )["project"]
        assert zensical_config["site_name"] == BASE_CONTEXT["project_name"]
        assert (
            zensical_config["site_description"]
            == BASE_CONTEXT["project_short_description"]
        )
        assert zensical_config["repo_url"] == BASE_CONTEXT["urls"]["repository"]
        assert zensical_config["theme"]["features"] == [
            "navigation.sections",
            "navigation.top",
            "content.action.edit",
            "content.action.view",
        ]
        assert zensical_config["plugins"]["mkdocstrings"]["handlers"]["python"][
            "paths"
        ] == ["src"]
        reference = (project_path / "docs/reference.md").read_text(encoding="utf-8")
        assert "::: zensical_docs_demo" in reference
        assert "zensical_docs_demo.services.processing" in reference
        contributing = (project_path / "CONTRIBUTING.md").read_text(encoding="utf-8")
        assert "uv run zensical build --strict" in contributing
        build = subprocess.run(
            ["zensical", "build", "--strict"],
            cwd=project_path,
            check=False,
            capture_output=True,
            text=True,
        )
        assert build.returncode == 0, build.stdout + build.stderr

    if docs_dependencies == ["myst-parser", "sphinx", "sphinx-book-theme"]:
        sphinx_config = (project_path / "docs" / "source" / "conf.py").read_text(
            encoding="utf-8"
        )
        assert 'html_theme = "sphinx_book_theme"' in sphinx_config
        reference = (project_path / "docs/source/reference.md").read_text(
            encoding="utf-8"
        )
        assert ".. automodule:: sphinx_docs_demo" in reference
        assert "sphinx_docs_demo.services.processing" in reference
        assert '"sphinx.ext.autodoc"' in sphinx_config
        assert '"myst_parser"' in sphinx_config
        assert 'project = PROJECT_METADATA["name"]' in sphinx_config
        assert 'author = ", ".join(PROJECT_METADATA["authors"])' in sphinx_config
        assert 'repository_url = PROJECT_METADATA["repository"]' in sphinx_config
        assert 'html_theme_options["use_repository_button"] = True' in sphinx_config
        expected_distribution = f"{documentation_builder}-docs-demo"
        assert f'release = metadata.version("{expected_distribution}")' in sphinx_config
        assert "except metadata.PackageNotFoundError:" in sphinx_config
        assert 'release = PROJECT_METADATA["version"]' in sphinx_config
        build = subprocess.run(
            [
                "sphinx-build",
                "-W",
                "-b",
                "html",
                "docs/source",
                "docs/build/html",
            ],
            cwd=project_path,
            check=False,
            capture_output=True,
            text=True,
        )
        assert build.returncode == 0, build.stdout + build.stderr


def test_python_empty_documentation_builder_uses_plain_markdown(tmp_path, monkeypatch):
    """Ensure Python docs can be scaffolded without a builder."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="generic_docs_demo",
        documentation_builder="",
    )

    assert_no_template_artifacts(project_path)
    assert (project_path / "docs" / "index.md").exists()
    assert (project_path / "docs" / "overview.md").exists()
    assert (project_path / "docs" / "functions.md").exists()
    assert (project_path / "docs" / "usage.md").exists()
    assert (project_path / "docs" / "developer.md").exists()
    assert (project_path / "docs" / "reference.md").exists()
    assert (project_path / "docs" / "documentation.md").exists()
    assert (project_path / "docs" / "legal.md").exists()
    assert not (project_path / "docs" / "deployment.md").exists()
    assert not (project_path / "docs" / "conf.py").exists()
    assert not (project_path / "mkdocs.yml").exists()
    assert not (project_path / "zensical.toml").exists()

    metadata = tomllib.loads((project_path / "pyproject.toml").read_text())
    optional_dependencies = metadata["project"]["optional-dependencies"]
    assert "docs" not in optional_dependencies
    assert not (project_path / ".github" / "workflows" / "docs.yml").exists()


def test_python_zensical_supports_user_docs_without_public_urls(tmp_path, monkeypatch):
    """Ensure minimal Zensical docs do not require repository or API metadata."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="zensical_user_docs_demo",
        documentation_builder="zensical",
        documentation_types={"entries": ["user"]},
        urls={"repository": "", "homepage": "", "documentation": ""},
    )

    config = tomllib.loads(
        (project_path / "zensical.toml").read_text(encoding="utf-8")
    )["project"]
    assert "site_url" not in config
    assert "repo_url" not in config
    assert "plugins" not in config
    assert (project_path / "docs" / "usage.md").exists()
    assert not (project_path / "docs" / "developer.md").exists()
    assert not (project_path / "docs" / "reference.md").exists()

    build = subprocess.run(
        ["zensical", "build", "--strict"],
        cwd=project_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert build.returncode == 0, build.stdout + build.stderr


def test_python_documentation_types_select_expected_pages(tmp_path, monkeypatch):
    """Ensure documentation_types controls optional documentation pages."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        documentation_types={"entries": ["deployment"]},
    )

    assert (project_path / "docs" / "deployment.md").exists()
    assert not (project_path / "docs" / "usage.md").exists()
    assert not (project_path / "docs" / "developer.md").exists()
    assert not (project_path / "docs" / "reference.md").exists()

    readme = (project_path / "README.md").read_text(encoding="utf-8")
    assert "## Documentation" in readme
    assert "- Deployment notes:" in readme
    assert "- User guide:" not in readme
    assert "- Developer guide:" not in readme

    deployment = (project_path / "docs" / "deployment.md").read_text(encoding="utf-8")
    assert "## HTTP service" in deployment
    assert "research-template-demo-serve" in deployment
    assert "## Script" in deployment
    assert "## Web application" not in deployment
    assert "## Portal" not in deployment
    assert "## External dependencies" in deployment
    assert "[Graphviz >=9](https://graphviz.org/)" in deployment


def test_python_community_file_selector_keeps_expected_files(tmp_path, monkeypatch):
    """Ensure the controlled community selector keeps requested files."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        community_files={"entries": ["GOVERNANCE.md", "SECURITY.md", "SUPPORT.md"]},
        public_risk_notes="Use the institutional security route for private reports.",
    )

    assert (project_path / "GOVERNANCE.md").exists()
    assert (project_path / "SECURITY.md").exists()
    assert (project_path / "SUPPORT.md").exists()
    assert (project_path / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml").exists()
    assert (
        project_path / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml"
    ).exists()
    assert (project_path / ".github" / "ISSUE_TEMPLATE" / "config.yml").exists()
    assert not (project_path / "CONTRIBUTING.md").exists()
    assert not (project_path / ".github" / "pull_request_template.md").exists()
    assert not (project_path / "CODE_OF_CONDUCT.md").exists()
    assert not (project_path / "CHANGELOG.md").exists()
    assert not (project_path / "tools" / "check_changelog.py").exists()
    assert not (project_path / ".github" / "workflows" / "changelog.yml").exists()

    governance = (project_path / "GOVERNANCE.md").read_text(encoding="utf-8")
    security = (project_path / "SECURITY.md").read_text(encoding="utf-8")
    support = (project_path / "SUPPORT.md").read_text(encoding="utf-8")
    assert governance.startswith("# Governance")
    assert security.startswith("# Security")
    assert support.startswith("# Support")
    assert BASE_CONTEXT["governance_notes"] in governance
    assert "Use the institutional security route" in security
    assert "https://github.com/LUMC-DCC/research-template-demo/issues" in support
    issue_form = yaml.safe_load(
        (project_path / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml").read_text(
            encoding="utf-8"
        )
    )
    assert issue_form["name"] == "Bug report"
    assert issue_form["labels"] == ["bug", "triage"]
    assert any(field.get("id") == "reproduce" for field in issue_form["body"])


def test_python_minimum_metadata_can_be_disabled(tmp_path, monkeypatch):
    """Ensure the paired metadata files and workflow follow one control."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="without_citation_demo",
        include_metadata=False,
    )

    assert not (project_path / "CITATION.cff").exists()
    assert not (project_path / "codemeta.json").exists()
    assert not (project_path / ".github/workflows/metadata.yml").exists()


def test_python_custom_license_generates_custom_license_file(tmp_path, monkeypatch):
    """Ensure unrecognized license values become custom license text."""
    custom_text = "Example Institutional License\n\nPermission for internal use."
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="custom_license_demo",
        licensing={"license": custom_text, "compatibility_check": ""},
    )

    assert (project_path / "LICENSE").read_text(encoding="utf-8") == (
        f"{custom_text}\n"
    )

    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    readme = (project_path / "README.md").read_text(encoding="utf-8")
    docs_legal = (project_path / "docs" / "legal.md").read_text(encoding="utf-8")

    assert "license" not in pyproject["project"]
    assert pyproject["project"]["license-files"] == ["LICENSE"]
    assert "license" not in pyproject["project"]["optional-dependencies"]
    assert "licensecheck" not in pyproject.get("tool", {})
    assert not (
        project_path / ".github" / "workflows" / "license-compatibility.yml"
    ).exists()
    assert "custom terms in `LICENSE`" in readme
    assert "custom terms in `LICENSE`" in docs_legal


def test_python_license_accepts_any_spdx_identifier(tmp_path, monkeypatch):
    """Ensure arbitrary SPDX identifiers can be fetched and rendered."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="bsd_license_demo",
        licensing={
            "license": "BSD-3-Clause",
            "compatibility_check": "Yes - automated tooling",
        },
    )

    license_text = (project_path / "LICENSE").read_text(encoding="utf-8")
    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    codemeta = json.loads((project_path / "codemeta.json").read_text())

    assert license_text == "BSD 3-Clause License\n\nRedistribution permitted.\n"
    assert pyproject["project"]["license"] == "BSD-3-Clause"
    assert pyproject["project"]["license-files"] == ["LICENSE"]
    assert pyproject["tool"]["licensecheck"]["license"] == "BSD-3-Clause"
    assert codemeta["license"] == "https://spdx.org/licenses/BSD-3-Clause"
    assert (
        project_path / ".github" / "workflows" / "license-compatibility.yml"
    ).exists()


def test_python_shared_community_files_render_standard_content(tmp_path, monkeypatch):
    """Ensure shared community files render standards and project metadata."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        community_files={
            "entries": [
                "CONTRIBUTING.md",
                "CODE_OF_CONDUCT.md",
                "GOVERNANCE.md",
                "SECURITY.md",
                "SUPPORT.md",
                "CHANGELOG.md",
            ]
        },
        versioning={
            **BASE_CONTEXT["versioning"],
            "release_frequency": "On (fixed) schedule",
        },
        continuity_plan="Maintainers hand over active work through reviewed issues.",
        retirement_criteria={"entries": ["Lack of maintainers"]},
        public_risk_notes="Use coordinated disclosure for suspected vulnerabilities.",
        data_management={
            **BASE_CONTEXT["data_management"],
            "dmp_reference": "DMP-123",
        },
    )

    contributing = (project_path / "CONTRIBUTING.md").read_text(encoding="utf-8")
    pull_request_template = (
        project_path / ".github" / "pull_request_template.md"
    ).read_text(encoding="utf-8")
    code_of_conduct = (project_path / "CODE_OF_CONDUCT.md").read_text(encoding="utf-8")
    changelog = (project_path / "CHANGELOG.md").read_text(encoding="utf-8")
    governance = (project_path / "GOVERNANCE.md").read_text(encoding="utf-8")
    security = (project_path / "SECURITY.md").read_text(encoding="utf-8")
    support = (project_path / "SUPPORT.md").read_text(encoding="utf-8")

    assert "Conventional Commits" in contributing
    assert "ruff check ." in contributing
    assert "Rebase" in contributing
    assert "CI runs on pushes and pull requests" in contributing
    assert "| Metadata |" in contributing
    assert "Validate generated metadata files." in contributing
    assert "The branch is rebased on the target branch" in contributing
    assert "No secrets, private data, or non-public security details" in contributing
    assert "Use a Conventional Commit pull request title" in pull_request_template
    assert "Metadata files are updated" in pull_request_template
    assert "Documentation is updated" in pull_request_template
    assert "Tests cover new behavior" in pull_request_template
    assert "Commands run:" in pull_request_template
    assert "Contributor Covenant" in code_of_conduct
    assert "Enforcement Guidelines" in code_of_conduct
    assert BASE_CONTEXT["contacts"]["code_of_conduct"] in code_of_conduct
    assert "Keep a Changelog" in changelog
    assert "## [Unreleased]" in changelog
    for heading in ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]:
        assert f"### {heading}" in changelog
    assert "Expected release cadence: On (fixed) schedule" in changelog
    assert "[Unreleased]:" in changelog
    changelog_check = subprocess.run(
        [sys.executable, "tools/check_changelog.py"],
        cwd=project_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert changelog_check.returncode == 0, (
        changelog_check.stdout + changelog_check.stderr
    )
    metadata_workflow = (
        project_path / ".github" / "workflows" / "metadata.yml"
    ).read_text(encoding="utf-8")
    changelog_workflow = (
        project_path / ".github" / "workflows" / "changelog.yml"
    ).read_text(encoding="utf-8")
    assert "Validate research software metadata" in metadata_workflow
    assert (
        "LUMC-DCC/rs-metadata@27f3da06c4bae5f735c492608b5ffea6c2715c21"
        in metadata_workflow
    )
    assert "Check changelog format" in changelog_workflow
    assert "python tools/check_changelog.py" in changelog_workflow
    assert "Maintainers hand over active work" in governance
    assert "Lack of maintainers" in governance
    assert "Research Software Team" in governance
    assert "Katherine Johnson" in governance
    assert "## Supported versions" in security
    assert "## Reporting a vulnerability" in security
    assert BASE_CONTEXT["contacts"]["security"] in security
    assert "Vulnerability scanning (e.g., Snyk, Dependabot)" in security
    assert "Security reports are reviewed privately" in security
    assert "Use coordinated disclosure" in security
    assert "## Regulatory and policy requirements" in security
    assert "GDPR - General Data Protection Regulation" in security
    assert BASE_CONTEXT["regulatory_requirements"]["additional"] in security
    assert "DMP-123" in security
    assert BASE_CONTEXT["urls"]["documentation"] in support
    assert "## What to include" in support
    assert "https://github.com/LUMC-DCC/research-template-demo/issues" in support
    assert "https://example.org/helpdesk" in support
    issue_template_config = yaml.safe_load(
        (project_path / ".github" / "ISSUE_TEMPLATE" / "config.yml").read_text(
            encoding="utf-8"
        )
    )
    assert {
        "name": "Helpdesk",
        "url": "https://example.org/helpdesk",
        "about": "Use this route for project support.",
    } in issue_template_config["contact_links"]


def test_python_operational_context_prefers_docs_with_readme_fallback(
    tmp_path,
    monkeypatch,
):
    """Ensure public operational context stays discoverable without bloating README."""
    context = {
        "resource_requirements": "Memory: 8 GB. Compute: 4 CPU cores.",
        "maintenance_level": "Security maintenance only",
        "continuity_plan": "A backup maintainer receives repository access.",
        "retirement_criteria": {
            "entries": ["Lack of maintainers", "Security / privacy risks"]
        },
        "public_risk_notes": "Public deployments require access controls.",
        "contacts": {
            **BASE_CONTEXT["contacts"],
            "security": "security@example.org",
        },
        "security_measures": {
            "selected": {"entries": ["Data encryption in transit (e.g., HTTPS/TLS)"]},
            "additional": "Audit access quarterly.",
        },
        "data_management": {
            "sensitive_data_statement": ("User-supplied sensitive data is supported."),
            "dmp_reference": "DMP-123",
        },
    }
    documented_tmp_path = tmp_path / "documented"
    documented_tmp_path.mkdir()
    documented_project = render_python_project(
        documented_tmp_path,
        monkeypatch,
        project_slug="documented_policy_demo",
        **context,
    )

    docs_dir = documented_project / "docs"
    resources = (docs_dir / "resource-requirements.md").read_text(encoding="utf-8")
    sustainability = (docs_dir / "sustainability.md").read_text(encoding="utf-8")
    security = (docs_dir / "security-and-data.md").read_text(encoding="utf-8")
    readme = (documented_project / "README.md").read_text(encoding="utf-8")

    assert "Memory: 8 GB" in resources
    assert "Security maintenance only" in sustainability
    assert "Lack of maintainers" in sustainability
    assert "security@example.org" in security
    assert "Audit access quarterly" in security
    assert "DMP-123" in security
    assert "Memory: 8 GB" not in readme
    assert "Security maintenance only" not in readme

    readme_tmp_path = tmp_path / "readme"
    readme_tmp_path.mkdir()
    readme_project = render_python_project(
        readme_tmp_path,
        monkeypatch,
        project_slug="readme_policy_demo",
        documentation_types={"entries": []},
        **context,
    )
    fallback_readme = (readme_project / "README.md").read_text(encoding="utf-8")

    assert not (readme_project / "docs").exists()
    assert "## Resource requirements" in fallback_readme
    assert "Memory: 8 GB" in fallback_readme
    assert "## Sustainability" in fallback_readme
    assert "Security maintenance only" in fallback_readme
    assert "## Security and data" in fallback_readme
    assert "DMP-123" in fallback_readme


def test_python_vulnerability_scanning_controls_security_workflow(
    tmp_path,
    monkeypatch,
):
    """Ensure vulnerability-scanning metadata controls security automation."""
    selected_tmp = tmp_path / "selected"
    selected_tmp.mkdir()
    selected_path = render_python_project(
        selected_tmp,
        monkeypatch,
        project_slug="security_scan_demo",
        documentation_builder="",
        test_types={"entries": []},
        quality_tools={"formatter": "", "linter": "", "type_checker": ""},
        include_metadata=False,
        community_files={"entries": []},
        licensing={"license": "MIT", "compatibility_check": ""},
        containerization={"entries": []},
        distribution_channels={"entries": []},
    )
    workflow_path = selected_path / ".github/workflows/security.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    developer_docs = (selected_path / "docs/developer.md").read_text(encoding="utf-8")

    assert set(workflow["jobs"]) == {"dependency-review", "codeql"}
    assert workflow["jobs"]["dependency-review"]["timeout-minutes"] == 10
    assert workflow["jobs"]["codeql"]["timeout-minutes"] == 30
    assert "`security.yml`" in developer_docs
    readme = (selected_path / "README.md").read_text(encoding="utf-8")
    assert "actions/workflows/security.yml/badge.svg" in readme
    assert not (selected_path / ".github/workflows/docs.yml").exists()

    unselected_tmp = tmp_path / "unselected"
    unselected_tmp.mkdir()
    unselected_path = render_python_project(
        unselected_tmp,
        monkeypatch,
        project_slug="without_security_scan_demo",
        documentation_builder="",
        test_types={"entries": []},
        quality_tools={"formatter": "", "linter": "", "type_checker": ""},
        include_metadata=False,
        community_files={"entries": []},
        licensing={"license": "MIT", "compatibility_check": ""},
        containerization={"entries": []},
        distribution_channels={"entries": []},
        security_measures={
            "selected": {"entries": ["Security patch management process"]},
            "additional": "",
        },
    )
    assert not (unselected_path / ".github/workflows/security.yml").exists()
    assert "`security.yml`" not in (unselected_path / "docs/developer.md").read_text(
        encoding="utf-8"
    )


def test_generated_python_package_imports(tmp_path, monkeypatch):
    """Ensure a generated Python package can be imported from source."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="importable_demo",
    )

    env = os.environ | {
        "PYTHONPATH": str(project_path / "src"),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from importable_demo import __version__; "
                "from importable_demo import process_text; "
                "from importable_demo.main import main; "
                "assert __version__ == '0.2.0'; "
                "assert callable(main); "
                "assert process_text('abc').output_text == 'ABC'"
            ),
        ],
        cwd=project_path,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_project_name_renders_in_python_public_surfaces(tmp_path, monkeypatch):
    """Ensure project_name renders in current Python project surfaces."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_name="Specific Project Name",
        project_slug="specific_project_name",
    )

    readme = (project_path / "README.md").read_text(encoding="utf-8")
    docs_landing = (project_path / "docs" / "index.md").read_text(encoding="utf-8")
    package_init = (
        project_path / "src" / "specific_project_name" / "__init__.py"
    ).read_text(encoding="utf-8")
    citation = yaml.safe_load(
        (project_path / "CITATION.cff").read_text(encoding="utf-8")
    )

    assert readme.startswith("# Specific Project Name")
    assert "Repository:" not in readme
    assert f"Homepage: {BASE_CONTEXT['urls']['homepage']}" in readme
    assert f"Documentation: {BASE_CONTEXT['urls']['documentation']}" in readme
    assert (
        "Publication: [Research Template Demo: reusable software scaffolds]"
        "(https://doi.org/10.1234/example)"
    ) in readme
    assert readme.index("Publication:") < readme.index("Homepage:")
    assert docs_landing.startswith("# Specific Project Name")
    assert '"""Public Python package for Specific Project Name.' in package_init
    assert citation["title"] == "Specific Project Name"

    env = os.environ | {
        "PYTHONPATH": str(project_path / "src"),
    }
    result = subprocess.run(
        [sys.executable, "-m", "specific_project_name.main"],
        cwd=project_path,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "SPECIFIC PROJECT NAME"


def test_project_long_description_renders_in_python_public_surfaces(
    tmp_path, monkeypatch
):
    """Ensure project_long_description renders in narrative public surfaces."""
    project_path = render_python_project(tmp_path, monkeypatch)

    docs_overview = (project_path / "docs" / "overview.md").read_text(encoding="utf-8")
    codemeta = json.loads((project_path / "codemeta.json").read_text())
    citation = yaml.safe_load(
        (project_path / "CITATION.cff").read_text(encoding="utf-8")
    )

    assert BASE_CONTEXT["project_long_description"] in docs_overview
    assert codemeta["description"] == BASE_CONTEXT["project_long_description"]
    assert citation["abstract"] == BASE_CONTEXT["project_long_description"]


def test_funding_renders_in_python_public_metadata_and_docs(tmp_path, monkeypatch):
    """Ensure multiple funding records render in public metadata and docs."""
    project_path = render_python_project(tmp_path, monkeypatch)

    docs_overview = (project_path / "docs" / "overview.md").read_text(encoding="utf-8")
    codemeta = json.loads((project_path / "codemeta.json").read_text())

    assert "## Funding" in docs_overview
    assert (
        "- LUMC: Research Software Sustainability "
        "(award LUMC-2024-001) "
        "([grant](https://example.org/grants/lumc-2024-001))"
    ) in docs_overview
    assert "- Health-RI (project HRI-RS-2)" in docs_overview
    assert "- LUMC (project RS-002)" in docs_overview
    assert codemeta["funder"] == [
        {
            "@type": "Organization",
            "name": "LUMC",
        },
        {
            "@type": "Organization",
            "name": "Health-RI",
        },
    ]
    assert codemeta["funding"] == ["LUMC-2024-001", "HRI-RS-2", "RS-002"]


def test_project_context_renders_in_python_readme_docs_and_metadata(
    tmp_path, monkeypatch
):
    """Ensure purpose, audiences, and related software render publicly."""
    project_path = render_python_project(tmp_path, monkeypatch)

    readme = (project_path / "README.md").read_text(encoding="utf-8")
    docs_overview = (project_path / "docs" / "overview.md").read_text(encoding="utf-8")
    docs_functions = (project_path / "docs" / "functions.md").read_text(
        encoding="utf-8"
    )
    docs_usage = (project_path / "docs" / "usage.md").read_text(encoding="utf-8")
    docs_developer = (project_path / "docs" / "developer.md").read_text(
        encoding="utf-8"
    )
    docs_reference = (project_path / "docs" / "reference.md").read_text(
        encoding="utf-8"
    )
    docs_legal = (project_path / "docs" / "legal.md").read_text(encoding="utf-8")
    codemeta = json.loads((project_path / "codemeta.json").read_text())

    expected_related = [
        (
            "- [Snakemake](https://snakemake.readthedocs.io) - workflow "
            "orchestration inspiration"
        ),
        (
            "- [Research Object Crate](https://www.researchobject.org/ro-crate/) "
            "- metadata interoperability"
        ),
    ]

    for content in (readme, docs_overview):
        assert (
            "Publication: [Research Template Demo: reusable software scaffolds]"
            "(https://doi.org/10.1234/example)"
        ) in content
        assert "## Purpose" in content
        assert BASE_CONTEXT["motivation"]["purpose"] in content
        assert "## Purpose Categories" in content
        assert "- Data analysis" in content
        assert "- Integration & interfacing" in content
        assert "## Intended Audience" in content
        assert "- Researchers (academia)" in content
        assert "- Software developers / RSEs" in content
        assert "## Related Software" in content
        for related_software in expected_related:
            assert related_software in content
    assert "## Problem" in docs_overview
    assert BASE_CONTEXT["motivation"]["problem_statement"] in docs_overview
    assert "## Value and need" in docs_overview
    assert BASE_CONTEXT["motivation"]["value_proposition"] in docs_overview
    assert BASE_CONTEXT["motivation"]["problem_statement"] not in readme
    assert BASE_CONTEXT["motivation"]["value_proposition"] not in readme
    assert "## Programming languages" not in readme
    assert (
        "![Tool Type](https://img.shields.io/badge/tool%20type-"
        "Command--line%20tool%20%7C%20Script%20%7C%20Web%20API-blue?labelColor=gray)"
    ) in readme
    assert readme.index("![Tool Type]") < readme.index(
        BASE_CONTEXT["project_short_description"]
    )
    assert "## Programming languages" in docs_overview
    assert "- Python >=3.11 - primary package" in docs_overview
    assert "- R >=4.3 - analysis examples" in docs_overview
    assert "## Input data formats" not in readme
    assert "## Output data formats" not in readme
    assert "## Functions" in readme
    assert "<summary>Statistical data analysis</summary>" in readme
    assert "# biotools-function" in readme
    assert "operation:" in readme
    assert '- term: "Statistical data analysis"' in readme
    assert '- term: "CSV"' in readme
    assert 'cmd: "research-template-demo analyse input.csv"' in readme
    assert "## Functions and operations" not in readme
    assert "## Input data formats" not in docs_overview
    assert "## Output data formats" not in docs_overview
    assert "## Functions and operations" in docs_overview
    assert "Statistical data analysis" in docs_overview
    assert "[Proteomics](http://edamontology.org/topic_0121)" in docs_overview
    assert "Columns: sample_id, value" in docs_overview
    assert "[sample](https://example.org/data/example.csv)" in docs_overview
    assert "`research-template-demo analyse input.csv`" in docs_overview
    assert "# Functions and operations" in docs_functions
    assert "## Statistical data analysis" in docs_functions
    assert "**Operations**" in docs_functions
    assert (
        "- [Statistical data analysis](http://edamontology.org/operation_2238)"
        in docs_functions
    )
    assert "**Topics**" in docs_functions
    assert "- [Proteomics](http://edamontology.org/topic_0121)" in docs_functions
    assert "**Inputs**" in docs_functions
    assert "[Expression data](http://edamontology.org/data_2603)" in docs_functions
    assert "Columns: sample_id, value" in docs_functions
    assert "[sample](https://example.org/data/example.csv)" in docs_functions
    assert "**Outputs**" in docs_functions
    assert (
        "- [Expression data](http://edamontology.org/data_2603) "
        "([JSON](http://edamontology.org/format_3464))"
    ) in docs_functions
    assert "```bash\nresearch-template-demo analyse input.csv\n```" in docs_functions
    assert "Summarizes numeric observations by group." in docs_functions
    assert "## Available functions" in docs_usage
    assert "[Functions and operations](functions.md)" in docs_usage
    assert "## Function metadata" in docs_developer
    assert "[Functions and operations](functions.md)" in docs_developer
    assert "`biotools-function` metadata blocks" in docs_developer
    assert "## Interfaces" in docs_overview
    assert (
        "- Command-line tool (Stable) - Command-line interface for local "
        "analysis workflows" in docs_overview
    )
    assert (
        "- Web API (Experimental) - OpenAPI-described service endpoint for "
        "analysis jobs"
    ) in docs_overview
    assert (
        "- Script (Experimental) - Batch entry point for scheduled processing"
        in docs_overview
    )
    assert "## Access interfaces" in docs_usage
    assert "Command-line tool (Stable)" in docs_usage
    assert "Web API (Experimental)" in docs_usage
    assert "Script (Experimental)" in docs_usage
    assert 'research-template-demo process "example input"' in docs_usage
    assert "research-template-demo-serve" in docs_usage
    assert 'python scripts/run_example.py "example input"' in docs_usage
    assert "adapters.web.app" not in docs_usage
    assert "## Interface contracts" in docs_developer
    assert "implementation files" in docs_developer
    assert "### Command-line tool" in docs_developer
    assert "### Web API" in docs_developer
    assert "### Script" in docs_developer
    assert "### Portal" not in docs_developer
    assert "## API interfaces" in docs_reference
    assert "Web API (Experimental)" in docs_reference
    assert "Command-line tool (Stable)" not in docs_reference

    assert docs_overview.index("Publication:") < docs_overview.index("## Purpose")
    assert "## Legal and Licensing" in readme
    assert "This project is licensed under `MIT`." in readme
    assert "# Legal and licensing" in docs_legal
    assert "This project is licensed under `MIT`." in docs_legal
    assert (
        "Dependency license compatibility is checked automatically in CI." in docs_legal
    )
    assert (
        "Dependencies are expected to use licenses compatible with MIT."
        not in docs_overview
    )
    assert (
        "Dependencies are expected to use licenses compatible with MIT." not in readme
    )
    assert "## Regulatory and policy requirements" in docs_legal
    assert "GDPR - General Data Protection Regulation" in docs_legal
    assert BASE_CONTEXT["regulatory_requirements"]["additional"] in docs_legal
    assert codemeta["relatedLink"] == [
        "https://snakemake.readthedocs.io",
        "https://www.researchobject.org/ro-crate/",
    ]


def test_python_template_generates_codemeta_metadata(tmp_path, monkeypatch):
    """Ensure Python projects render machine-readable CodeMeta metadata."""
    project_path = render_python_project(tmp_path, monkeypatch)

    codemeta = json.loads((project_path / "codemeta.json").read_text())

    assert codemeta["@context"] == [
        "https://w3id.org/codemeta/3.1",
        {"schema": "https://schema.org/"},
    ]
    assert codemeta["@type"] == "SoftwareSourceCode"
    assert codemeta["name"] == "Research Template Demo"
    assert codemeta["version"] == "0.2.0"
    assert codemeta["description"] == BASE_CONTEXT["project_long_description"]
    assert codemeta["developmentStatus"] == "active"
    assert codemeta["applicationCategory"] == [
        "Command-line tool",
        "Web API",
        "Script",
    ]
    assert codemeta["applicationSubCategory"] == ["http://edamontology.org/topic_0121"]
    assert codemeta["schema:featureList"] == ["http://edamontology.org/operation_2238"]
    assert codemeta["programmingLanguage"] == [
        {"@type": "ComputerLanguage", "name": "Python", "version": ">=3.11"},
        {"@type": "ComputerLanguage", "name": "R", "version": ">=4.3"},
    ]
    assert codemeta["operatingSystem"] == [
        "Linux >=Ubuntu 22.04",
        "macOS >=13",
        "Windows",
    ]
    assert codemeta["license"] == "https://spdx.org/licenses/MIT"
    assert codemeta["codeRepository"] == (
        "https://github.com/LUMC-DCC/research-template-demo"
    )
    assert codemeta["url"] == "https://example.org/research-template-demo"
    assert codemeta["softwareHelp"] == {
        "@type": "CreativeWork",
        "url": "https://lumc-dcc.github.io/research-template-demo",
    }
    assert codemeta["supportingData"] == [
        {
            "@type": "DataFeed",
            "@id": "https://example.org/data/example.csv",
            "name": "CSV",
            "url": "https://example.org/data/example.csv",
        }
    ]
    assert "provider" not in codemeta
    assert codemeta["funder"] == [
        {
            "@type": "Organization",
            "name": "LUMC",
        },
        {
            "@type": "Organization",
            "name": "Health-RI",
        },
    ]
    assert codemeta["funding"] == ["LUMC-2024-001", "HRI-RS-2", "RS-002"]
    assert codemeta["keywords"] == ["research-software", "template"]
    assert codemeta["relatedLink"] == [
        "https://snakemake.readthedocs.io",
        "https://www.researchobject.org/ro-crate/",
    ]
    assert codemeta["softwareRequirements"] == [
        {
            "@type": "SoftwareSourceCode",
            "@id": "https://graphviz.org/",
            "name": "Graphviz",
            "url": "https://graphviz.org/",
            "version": ">=9",
            "license": "https://spdx.org/licenses/EPL-1.0",
            "description": "Diagram rendering for reports",
        },
        {
            "@type": "SoftwareSourceCode",
            "@id": "https://edamontology.org/",
            "name": "EDAM ontology",
            "url": "https://edamontology.org/",
            "license": "https://spdx.org/licenses/CC-BY-SA-4.0",
            "description": "Controlled vocabulary for function metadata",
        },
    ]
    assert [entry["@id"] for entry in codemeta["referencePublication"]] == [
        "https://doi.org/10.1234/example",
        "https://example.org/publications/template-validation",
    ]
    assert all(
        entry["@type"] == "ScholarlyArticle"
        for entry in codemeta["referencePublication"]
    )
    assert codemeta["sameAs"] == [
        "https://pypi.org/project/research-template-demo/",
        "https://bio.tools/research-template-demo",
    ]
    assert codemeta["author"] == [
        {
            "@type": "Person",
            "@id": "https://orcid.org/0000-0002-1825-0097",
            "name": "Ada Lovelace",
            "givenName": "Ada",
            "familyName": "Lovelace",
            "email": "ada@example.org",
            "affiliation": {
                "@type": "Organization",
                "@id": "https://ror.org/05xvt9f17",
                "name": "Leiden University Medical Center",
            },
            "url": "https://example.org/ada",
        },
        {
            "@type": "Person",
            "@id": "https://orcid.org/0000-0001-5109-3700",
            "name": "Grace Hopper",
            "givenName": "Grace",
            "familyName": "Hopper",
            "email": "grace@example.org",
            "affiliation": {
                "@type": "Organization",
                "@id": "https://ror.org/05xvt9f17",
                "name": "Leiden University Medical Center",
            },
        },
    ]
    assert codemeta["maintainer"] == [
        {
            "@type": "Person",
            "@id": "https://orcid.org/0000-0002-1825-0097",
            "name": "Ada Lovelace",
            "givenName": "Ada",
            "familyName": "Lovelace",
            "email": "ada@example.org",
            "affiliation": {
                "@type": "Organization",
                "@id": "https://ror.org/05xvt9f17",
                "name": "Leiden University Medical Center",
            },
            "url": "https://example.org/ada",
        },
        {
            "@type": "Person",
            "@id": "https://example.org/research-software-team",
            "name": "Research Software Team",
            "email": "rs@example.org",
            "url": "https://example.org/research-software-team",
        },
    ]
    assert codemeta["contributor"] == [
        {
            "@type": "Person",
            "name": "Katherine Johnson",
            "affiliation": {
                "@type": "Organization",
                "@id": "https://ror.org/05xvt9f17",
                "name": "Leiden University Medical Center",
            },
        }
    ]
    assert codemeta["identifier"] == [
        "https://doi.org/10.5281/zenodo.12345",
        {
            "@type": "PropertyValue",
            "propertyID": "swh",
            "value": "swh:1:dir:bc286860f423ea7ced246ba7458eef4b4541cf2d",
            "description": "Persistent identifier for version 0.2.0",
        },
    ]
    assert codemeta["sameAs"] == [
        "https://pypi.org/project/research-template-demo/",
        "https://bio.tools/research-template-demo",
    ]


def test_project_team_fallback_renders_when_authors_are_missing(
    tmp_path,
    monkeypatch,
):
    """Ensure selected metadata remains structurally complete without authors."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        contributors={"entries": []},
        documentation_builder="sphinx",
    )

    codemeta = json.loads((project_path / "codemeta.json").read_text())
    citation = yaml.safe_load(
        (project_path / "CITATION.cff").read_text(encoding="utf-8")
    )
    assert "provider" not in codemeta
    assert codemeta["author"] == [
        {
            "@type": "Organization",
            "name": "Project team",
        }
    ]
    assert citation["authors"] == [{"name": "Project team"}]


def test_python_codemeta_preserves_overlapping_people_roles(tmp_path, monkeypatch):
    """Ensure overlapping people roles share stable CodeMeta identifiers."""
    overlapping_person = {
        "name": "Ada Lovelace",
        "given_names": "Ada",
        "family_names": "Lovelace",
        "email": "ada@example.org",
        "affiliations": [{"name": "LUMC"}],
        "orcid": "0000-0002-1825-0097",
        "roles": ["Original author", "Maintainer", "Principal investigator"],
    }
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        contributors={"entries": [overlapping_person]},
    )

    codemeta = json.loads((project_path / "codemeta.json").read_text())

    assert codemeta["author"][0]["@id"] == "https://orcid.org/0000-0002-1825-0097"
    assert codemeta["maintainer"][0]["@id"] == codemeta["author"][0]["@id"]
    assert codemeta["contributor"][0]["@id"] == codemeta["author"][0]["@id"]
    assert codemeta["author"][0]["name"] == "Ada Lovelace"
    assert codemeta["maintainer"][0]["name"] == "Ada Lovelace"
    assert codemeta["contributor"][0]["name"] == "Ada Lovelace"


def test_python_people_metadata_accepts_structured_names(tmp_path, monkeypatch):
    """Ensure generated metadata can compose names from structured parts."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        contributors={
            "entries": [
                {
                    "name": "Ada Lovelace",
                    "given_names": "Ada",
                    "family_names": "Lovelace",
                    "email": "ada@example.org",
                    "roles": ["Original author"],
                },
                {
                    "name": "Grace Hopper",
                    "given_names": "Grace",
                    "family_names": "Hopper",
                    "email": "grace@example.org",
                    "roles": ["Maintainer"],
                },
                {
                    "name": "Katherine Johnson",
                    "given_names": "Katherine",
                    "family_names": "Johnson",
                    "affiliations": [{"name": "LUMC"}],
                    "roles": ["Principal investigator"],
                },
            ]
        },
        community_files={"entries": ["GOVERNANCE.md"]},
    )

    pyproject = tomllib.loads((project_path / "pyproject.toml").read_text())
    codemeta = json.loads((project_path / "codemeta.json").read_text())
    citation = yaml.safe_load(
        (project_path / "CITATION.cff").read_text(encoding="utf-8")
    )
    governance = (project_path / "GOVERNANCE.md").read_text(encoding="utf-8")

    assert pyproject["project"]["authors"][0]["name"] == "Ada Lovelace"
    assert pyproject["project"]["maintainers"][0]["name"] == "Grace Hopper"
    assert codemeta["author"][0]["name"] == "Ada Lovelace"
    assert codemeta["maintainer"][0]["name"] == "Grace Hopper"
    assert codemeta["contributor"][0]["name"] == "Katherine Johnson"
    assert citation["authors"][0]["given-names"] == "Ada"
    assert citation["authors"][0]["family-names"] == "Lovelace"
    assert "Grace Hopper <grace@example.org>" in governance
    assert "Katherine Johnson, LUMC" in governance


def test_python_template_generates_citation_metadata(tmp_path, monkeypatch):
    """Ensure Python projects render machine-readable citation metadata."""
    project_path = render_python_project(tmp_path, monkeypatch)

    citation_text = (project_path / "CITATION.cff").read_text(encoding="utf-8")
    citation = yaml.safe_load(citation_text)
    Draft7Validator(cff_schema()).validate(citation)

    assert citation["cff-version"] == "1.2.0"
    assert citation["title"] == "Research Template Demo"
    assert citation["type"] == "software"
    assert citation["version"] == "0.2.0"
    assert citation["abstract"] == (
        "A longer public description of the generated research software."
    )
    assert citation["repository-code"] == (
        "https://github.com/LUMC-DCC/research-template-demo"
    )
    assert citation["url"] == "https://example.org/research-template-demo"
    assert citation["keywords"] == ["research-software", "template"]
    assert citation["authors"] == [
        {
            "family-names": "Lovelace",
            "given-names": "Ada",
            "affiliation": "Leiden University Medical Center",
            "email": "ada@example.org",
            "orcid": "https://orcid.org/0000-0002-1825-0097",
            "website": "https://example.org/ada",
        },
        {
            "family-names": "Hopper",
            "given-names": "Grace",
            "affiliation": "Leiden University Medical Center",
            "email": "grace@example.org",
            "orcid": "https://orcid.org/0000-0001-5109-3700",
        },
    ]
    assert citation["contact"] == [
        {
            "family-names": "Lovelace",
            "given-names": "Ada",
            "affiliation": "Leiden University Medical Center",
            "email": "ada@example.org",
            "orcid": "https://orcid.org/0000-0002-1825-0097",
            "website": "https://example.org/ada",
        },
        {
            "name": "Research Software Team",
            "email": "rs@example.org",
            "website": "https://example.org/research-software-team",
        },
    ]
    assert citation["identifiers"] == [
        {
            "type": "doi",
            "value": "10.5281/zenodo.12345",
        },
        {
            "type": "swh",
            "value": "swh:1:dir:bc286860f423ea7ced246ba7458eef4b4541cf2d",
            "description": "Persistent identifier for version 0.2.0",
        },
    ]
    assert citation["preferred-citation"] == {
        "type": "article",
        "title": "Research Template Demo: reusable software scaffolds",
        "doi": "10.1234/example",
        "authors": [{"family-names": "Lovelace", "given-names": "Ada"}],
    }
    assert citation["references"] == [
        {
            "type": "article",
            "title": "Research Template Demo: reusable software scaffolds",
            "doi": "10.1234/example",
            "authors": [{"family-names": "Lovelace", "given-names": "Ada"}],
        },
        {
            "type": "article",
            "title": "Validation of reusable research software templates",
            "pmcid": "PMC7654321",
            "url": "https://example.org/publications/template-validation",
            "identifiers": [
                {
                    "type": "other",
                    "value": "PMID:12345678",
                    "description": "PMID",
                }
            ],
            "notes": "Validation study",
            "authors": [{"family-names": "Hopper", "given-names": "Grace"}],
        },
    ]


def test_generated_python_metadata_passes_lumc_profile(tmp_path, monkeypatch):
    """Ensure generated metadata passes the authoritative LUMC validator."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        urls={
            **BASE_CONTEXT["urls"],
            "homepage": "https://lumc-dcc.github.io/research-template-demo",
        },
        publications={
            "entries": [
                {
                    "title": "Fast and accurate short read alignment",
                    "doi": "10.1093/bioinformatics/btp352",
                    "preferred": True,
                    "authors": [
                        {
                            "name": "Ada Lovelace",
                            "given_names": "Ada",
                            "family_names": "Lovelace",
                        }
                    ],
                }
            ]
        },
    )

    result = subprocess.run(
        [str(Path(sys.executable).with_name("rs-metadata")), "validate", "."],
        cwd=project_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_generated_python_project_tests_pass(tmp_path, monkeypatch):
    """Ensure the generated project's own test suite passes."""
    project_path = render_python_project(
        tmp_path,
        monkeypatch,
        project_slug="tested_demo",
    )

    env = os.environ | {
        "PYTHONPATH": str(project_path / "src"),
    }
    result = subprocess.run(
        [sys.executable, "-m", "pytest"],
        cwd=project_path,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
