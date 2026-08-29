"""Tests for the RSM contract and local template-policy boundary."""

from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest
from rsm_schema import RSMMetadata
from rsm_schema import schema as rsm_schema

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "_config" / "template_policies.json"
FIELD_USAGE_PATH = ROOT / "_contracts" / "field_usage.json"
FIELD_USAGE_DOC_PATH = ROOT / "_docs" / "contract" / "field-usage.md"
COPIER_TASKS = ROOT / "_copier_tasks"
QUESTION_PATH = ROOT / "_config" / "rsm_questions.yml"
COMPUTED_QUESTIONS = {
    "template_defaults",
    "template_schemas",
    "template_supported_choices",
}


def load_module(name: str, path: Path):
    """Load one repository module by path.

    Parameters
    ----------
    name
        Temporary import name.
    path
        Python source path.

    Returns
    -------
    module
        Imported module.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def question_builder():
    """Return the Copier question builder module."""
    return load_module(
        "build_copier_questions",
        ROOT / "_scripts" / "build_copier_questions.py",
    )


def load_json(path: Path) -> dict:
    """Load one UTF-8 JSON object."""
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_answer(value):
    """Convert nullable prompt defaults to finalization sentinels."""
    if value is None:
        return ""
    if isinstance(value, dict):
        return {name: normalize_answer(item) for name, item in value.items()}
    if isinstance(value, list):
        return [normalize_answer(item) for item in value]
    return value


def rendered_defaults(question_builder, template: str) -> dict:
    """Return public Copier defaults for one language template."""
    policies = question_builder.load_policies(POLICY_PATH)
    questions = question_builder.build_questions(policies=policies)
    defaults = {
        name: normalize_answer(deepcopy(question["default"]))
        for name, question in questions.items()
        if name in rsm_schema.raw["properties"]
    }
    defaults["project_slug"] = policies[template]["defaults"]["project_slug"]
    return defaults


def test_published_rsm_schema_is_the_public_contract():
    """Ensure the installed stable schema is valid and has one required field."""
    rsm_schema.validate_schema()

    assert rsm_schema.raw["$id"] == (
        "https://lumc-dcc.github.io/rsm-schema/schema/1.0.0/rsm.schema.json"
    )
    assert rsm_schema.raw["required"] == ["project_slug"]


def test_reusable_repository_file_models_are_integrated():
    """Ensure every reusable repository-file model is wired into generation."""
    sys.path.insert(0, str(COPIER_TASKS))
    try:
        from post_generation.repository_files import REPOSITORY_FILE_MODELS
    finally:
        sys.path.remove(str(COPIER_TASKS))

    integrated_outputs = {
        model_type.output_name for model_type in REPOSITORY_FILE_MODELS
    }
    assert integrated_outputs == {
        ".github/ISSUE_TEMPLATE.zip",
        ".github/pull_request_template.md",
        ".zenodo.json",
        "CHANGELOG.md",
        "CITATION.cff",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "GOVERNANCE.md",
        "LICENSE",
        "SECURITY.md",
        "SUPPORT.md",
        "codemeta.json",
    }


def test_copier_questions_are_derived_from_rsm(question_builder):
    """Ensure committed Copier questions match the schema adapter output."""
    questions = question_builder.build_questions(
        policies=question_builder.load_policies(POLICY_PATH)
    )

    assert QUESTION_PATH.read_text(encoding="utf-8") == (
        question_builder.questions_yaml(questions)
    )
    assert set(questions) - COMPUTED_QUESTIONS == set(rsm_schema.raw["properties"])


def test_copier_defaults_validate_as_rsm(question_builder):
    """Ensure empty Copier defaults normalize to valid RSM metadata."""
    sys.path.insert(0, str(COPIER_TASKS))
    try:
        from utils.rsm import rsm_payload
    finally:
        sys.path.remove(str(COPIER_TASKS))

    for template in question_builder.load_policies(POLICY_PATH):
        defaults = rendered_defaults(question_builder, template)
        payload = rsm_payload(defaults, RSMMetadata.model_fields)
        RSMMetadata.model_validate(payload)


def test_language_policies_only_narrow_published_choices(question_builder):
    """Ensure local capabilities remain subsets of published RSM choices."""
    policies = question_builder.load_policies(POLICY_PATH)
    properties = rsm_schema.raw["properties"]
    allowed = {
        "documentation_builder": set(properties["documentation_builder"]["enum"]),
        "test_frameworks": set(
            properties["test_frameworks"]["properties"]["entries"]["items"]["enum"]
        ),
        "project_manager": set(properties["project_manager"]["enum"]),
    }
    quality = properties["quality_tools"]["properties"]

    for policy in policies.values():
        supported = policy["supported_choices"]
        for field_name, choices in allowed.items():
            assert set(supported[field_name]) <= choices
        for tool_name, choices in supported["quality_tools"].items():
            assert set(choices) <= set(quality[tool_name]["enum"])


def test_language_slug_constraints_are_enforced(question_builder):
    """Ensure each language applies its own repository-name constraints."""
    sys.path.insert(0, str(COPIER_TASKS))
    try:
        validator = load_module(
            "template_context_validation",
            COPIER_TASKS / "post_generation" / "validation.py",
        )
    finally:
        sys.path.remove(str(COPIER_TASKS))

    policies = question_builder.load_policies(POLICY_PATH)
    python_context = rendered_defaults(question_builder, "python") | {
        "_template_name": "python",
        "_template_schemas": policies["python"]["field_schemas"],
    }
    r_context = rendered_defaults(question_builder, "r") | {
        "_template_name": "r",
        "_template_schemas": policies["r"]["field_schemas"],
    }
    validator.validate_context(python_context | {"project_slug": "valid_package"})
    validator.validate_context(r_context | {"project_slug": "Valid.Package"})

    with pytest.raises(ValueError, match=r"Invalid 'project_slug'.*python"):
        validator.validate_context(python_context | {"project_slug": "invalid-name"})


def test_field_usage_covers_the_published_schema():
    """Ensure every RSM field has one implementation-status entry."""
    usage = load_json(FIELD_USAGE_PATH)
    usage_fields = [field["name"] for field in usage["fields"]]

    assert len(usage_fields) == len(set(usage_fields))
    assert set(usage_fields) == set(rsm_schema.raw["properties"])
    for field in usage["fields"]:
        assert set(field["statuses"]) == set(usage["templates"])


def test_field_usage_docs_and_reference_audit_are_current():
    """Ensure the curated usage map matches docs and template references."""
    usage = load_json(FIELD_USAGE_PATH)
    docs_builder = load_module(
        "build_field_usage_docs",
        ROOT / "_scripts" / "build_field_usage_docs.py",
    )
    audit = load_module(
        "audit_field_usage_status",
        ROOT / "_scripts" / "audit_field_usage_status.py",
    )

    assert FIELD_USAGE_DOC_PATH.read_text(encoding="utf-8") == docs_builder.build_table(
        usage
    )
    assert audit.audit_usage(dict(rsm_schema.raw), usage, ROOT) == []
