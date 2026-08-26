"""Build Cookiecutter contexts from the published RSM schema.

The installed ``rsm-schema`` package owns public fields, defaults, choices, and
descriptions. This module adds only language-specific generation policy and
Cookiecutter's private rendering settings.
"""

from __future__ import annotations

import argparse
import copy
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rsm_schema import schema as rsm_schema

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_POLICY_PATH = ROOT / "_config" / "template_policies.json"


def load_rsm_schema() -> dict[str, Any]:
    """Return a mutable copy of the bundled RSM JSON Schema.

    Returns
    -------
    dict[str, Any]
        Published RSM schema bundled with the installed package.
    """
    return copy.deepcopy(dict(rsm_schema.raw))


def load_policies(path: Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    """Load language-specific template policies.

    Parameters
    ----------
    path
        Policy JSON path.

    Returns
    -------
    dict[str, Any]
        Policies keyed by template name.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def field_default(field: Mapping[str, Any], *, nested: bool = False) -> Any:
    """Derive a Cookiecutter-compatible value for one RSM field.

    Parameters
    ----------
    field
        JSON Schema property definition.
    nested
        Whether the field is nested inside an RSM object. Optional enum members
        use ``None`` at this level so the generated context remains valid.

    Returns
    -------
    Any
        Schema default, an empty scalar or container, or ``None`` for an
        optional nested enum.
    """
    field_type = field.get("type")
    if field_type == "object":
        result = copy.deepcopy(field.get("default", {}))
        for name, child in field.get("properties", {}).items():
            result.setdefault(name, field_default(child, nested=True))
        return result
    if "default" in field:
        return copy.deepcopy(field["default"])
    if field_type == "string":
        # Optional enum members are represented by ``null`` internally.
        # Empty strings are not valid enum values, while Cookiecutter needs
        # each nested member to exist for templates that access it directly.
        if nested and field.get("enum"):
            return None
        return ""
    if field_type == "boolean":
        return False
    if field_type == "array":
        return []
    return None


def choice_value(field: Mapping[str, Any], default: Any) -> Any:
    """Render scalar enum fields as Cookiecutter choices.

    Parameters
    ----------
    field
        JSON Schema property definition.
    default
        Effective field default.

    Returns
    -------
    Any
        Ordered choice list for scalar enums, otherwise ``default``.
    """
    choices = field.get("enum")
    if field.get("type") != "string" or not isinstance(choices, list):
        return default

    ordered = list(choices)
    if default not in ordered:
        return [default, *ordered]
    return [default, *[choice for choice in ordered if choice != default]]


def template_metadata(
    policies: Mapping[str, Any],
    template: str | None,
) -> dict[str, Any]:
    """Build private metadata consumed by post-generation hooks.

    Parameters
    ----------
    policies
        Language policies keyed by template name.
    template
        Selected language template.

    Returns
    -------
    dict[str, Any]
        Private Cookiecutter metadata.
    """
    policy = policies.get(template, {}) if template else {}
    return {
        "_template_name": template or "",
        "_template_defaults": copy.deepcopy(policy.get("defaults", {})),
        "_template_schemas": copy.deepcopy(policy.get("field_schemas", {})),
        "_template_supported_choices": copy.deepcopy(
            policy.get("supported_choices", {})
        ),
    }


def build_context(
    schema: Mapping[str, Any] | None = None,
    *,
    policies: Mapping[str, Any] | None = None,
    template: str | None = None,
) -> dict[str, Any]:
    """Build a Cookiecutter context from RSM fields and template policy.

    Parameters
    ----------
    schema
        RSM JSON Schema. The installed schema is used when omitted.
    policies
        Language policies. The maintained policy file is used when omitted.
    template
        Template name, such as ``python`` or ``r``.

    Returns
    -------
    dict[str, Any]
        Cookiecutter context with private template metadata.
    """
    schema_document = dict(schema or load_rsm_schema())
    policy_document = dict(policies or load_policies())
    template_policy = policy_document.get(template, {}) if template else {}
    overrides = template_policy.get("defaults", {})
    properties = schema_document.get("properties", {})
    context: dict[str, Any] = {}
    prompts: dict[str, str] = {}

    for name, field in properties.items():
        default = copy.deepcopy(overrides.get(name, field_default(field)))
        context[name] = choice_value(field, default)
        if description := field.get("description"):
            prompts[name] = description

    context["__prompts__"] = prompts
    context["_jinja2_env_vars"] = {
        "lstrip_blocks": True,
        "trim_blocks": True,
    }
    context.update(template_metadata(policy_document, template))
    return context


def write_context(context: Mapping[str, Any], path: Path) -> bool:
    """Write a generated context only when its content changes.

    Parameters
    ----------
    context
        Cookiecutter context data.
    path
        Destination JSON path.

    Returns
    -------
    bool
        Whether the destination changed.
    """
    content = context_json(context)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def context_json(context: Mapping[str, Any]) -> str:
    """Serialize a generated Cookiecutter context consistently.

    Parameters
    ----------
    context
        Cookiecutter context data.

    Returns
    -------
    str
        Pretty-printed JSON ending in one newline.
    """
    return json.dumps(context, indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    """Run the command-line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--policies", type=Path, default=DEFAULT_POLICY_PATH)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--template", required=True)
    args = parser.parse_args()
    write_context(
        build_context(policies=load_policies(args.policies), template=args.template),
        args.output,
    )


if __name__ == "__main__":
    main()
