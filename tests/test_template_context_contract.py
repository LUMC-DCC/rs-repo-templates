"""Tests for the RSM contract and local template-policy boundary."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from rsm_schema import RSMMetadata
from rsm_schema import schema as rsm_schema

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "_config" / "template_policies.json"
FIELD_USAGE_PATH = ROOT / "_contracts" / "field_usage.json"
FIELD_USAGE_DOC_PATH = ROOT / "_docs" / "contract" / "field-usage.md"
TEMPLATE_HOOKS = ROOT / "_cc_shared" / "template_hooks"


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
def context_builder():
    """Return the Cookiecutter context builder module."""
    return load_module(
        "build_cookiecutter_context",
        ROOT / "_scripts" / "build_cookiecutter_context.py",
    )


def load_json(path: Path) -> dict:
    """Load one UTF-8 JSON object."""
    return json.loads(path.read_text(encoding="utf-8"))


def rendered_defaults(context: dict, schema: dict) -> dict:
    """Resolve Cookiecutter scalar choices to their first value."""
    properties = schema["properties"]
    return {
        name: value[0]
        if isinstance(value, list) and "enum" in properties[name]
        else value
        for name, value in context.items()
        if name in properties
    }


def test_published_rsm_schema_is_the_public_contract():
    """Ensure the installed stable schema is valid and has one required field."""
    rsm_schema.validate_schema()

    assert rsm_schema.raw["$id"] == (
        "https://lumc-dcc.github.io/rsm-schema/schema/1.0.0/rsm.schema.json"
    )
    assert rsm_schema.raw["required"] == ["project_slug"]


def test_reusable_repository_file_models_are_integrated():
    """Ensure every reusable repository-file model is wired into generation."""
    sys.path.insert(0, str(TEMPLATE_HOOKS))
    try:
        from post_generation.repository_files import REPOSITORY_FILE_MODELS
    finally:
        sys.path.remove(str(TEMPLATE_HOOKS))

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


def test_cookiecutter_contexts_are_derived_from_rsm(context_builder):
    """Ensure shared and language contexts match the schema adapter output."""
    policies = context_builder.load_policies(POLICY_PATH)
    for template in policies:
        expected = context_builder.build_context(
            policies=policies,
            template=template,
        )
        assert load_json(ROOT / template / "cookiecutter.json") == expected
        assert set(expected) - {
            "__prompts__",
            "_jinja2_env_vars",
            "_template_name",
            "_template_defaults",
            "_template_schemas",
            "_template_supported_choices",
        } == set(rsm_schema.raw["properties"])


def test_cookiecutter_defaults_validate_as_rsm(context_builder):
    """Ensure empty Cookiecutter sentinels normalize to valid RSM metadata."""
    sys.path.insert(0, str(TEMPLATE_HOOKS))
    try:
        from utils.rsm import rsm_payload
    finally:
        sys.path.remove(str(TEMPLATE_HOOKS))

    schema = dict(rsm_schema.raw)
    for template in context_builder.load_policies(POLICY_PATH):
        context = context_builder.build_context(template=template)
        defaults = rendered_defaults(context, schema)
        payload = rsm_payload(defaults, RSMMetadata.model_fields)
        RSMMetadata.model_validate(payload)


def test_language_policies_only_narrow_published_choices(context_builder):
    """Ensure local capabilities remain subsets of published RSM choices."""
    policies = context_builder.load_policies(POLICY_PATH)
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


def test_language_slug_constraints_are_enforced(context_builder):
    """Ensure each language applies its own repository-name constraints."""
    sys.path.insert(0, str(TEMPLATE_HOOKS))
    try:
        validator = load_module(
            "template_context_validation",
            TEMPLATE_HOOKS / "post_generation" / "validation.py",
        )
    finally:
        sys.path.remove(str(TEMPLATE_HOOKS))

    python_context = context_builder.build_context(template="python")
    r_context = context_builder.build_context(template="r")
    validator.validate_context(
        rendered_defaults(python_context, dict(rsm_schema.raw))
        | {
            "project_slug": "valid_package",
            "_template_name": "python",
            "_template_schemas": python_context["_template_schemas"],
        }
    )
    validator.validate_context(
        rendered_defaults(r_context, dict(rsm_schema.raw))
        | {
            "project_slug": "Valid.Package",
            "_template_name": "r",
            "_template_schemas": r_context["_template_schemas"],
        }
    )

    with pytest.raises(ValueError, match=r"Invalid 'project_slug'.*python"):
        validator.validate_context(
            rendered_defaults(python_context, dict(rsm_schema.raw))
            | {
                "project_slug": "invalid-name",
                "_template_name": "python",
                "_template_schemas": python_context["_template_schemas"],
            }
        )


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
