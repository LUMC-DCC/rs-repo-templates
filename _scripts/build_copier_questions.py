"""Build Copier questions from the published RSM schema.

The published schema owns public fields, defaults, controlled values, and
descriptions. This adapter expresses those fields in Copier's questionnaire
format and adds only computed language-policy values used while rendering.
"""

from __future__ import annotations

import argparse
import copy
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from rsm_schema import schema as rsm_schema

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_POLICY_PATH = ROOT / "_config" / "template_policies.json"
DEFAULT_OUTPUT_PATH = ROOT / "_config" / "rsm_questions.yml"


class NoAliasDumper(yaml.SafeDumper):
    """YAML dumper that keeps generated question defaults self-contained."""

    def ignore_aliases(self, data: Any) -> bool:
        """Disable YAML anchors in generated configuration.

        Parameters
        ----------
        data
            Value considered by the YAML serializer.

        Returns
        -------
        bool
            Always ``True`` so repeated defaults remain explicit.
        """
        return True


def load_policies(path: Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    """Load language-specific rendering policies.

    Parameters
    ----------
    path
        Policy JSON path.

    Returns
    -------
    dict[str, Any]
        Policies keyed by template type.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def field_default(field: Mapping[str, Any], *, nested: bool = False) -> Any:
    """Derive a nullable Copier default for one RSM field.

    Parameters
    ----------
    field
        JSON Schema property definition.
    nested
        Whether the property is nested in an object.

    Returns
    -------
    Any
        Schema default or an empty nullable value of the appropriate shape.
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
        return ""
    if field_type == "boolean":
        return False
    if field_type == "array":
        return []
    if nested:
        return None
    return None


def copier_type(field: Mapping[str, Any]) -> str:
    """Map one JSON Schema type to Copier's prompt types.

    Parameters
    ----------
    field
        JSON Schema property definition.

    Returns
    -------
    str
        Copier prompt type.
    """
    field_type = field.get("type")
    if field_type == "boolean":
        return "bool"
    if field_type == "integer":
        return "int"
    if field_type == "number":
        return "float"
    if field_type == "string":
        return "str"
    return "yaml"


def enum_choices(field: Mapping[str, Any]) -> dict[str, Any] | None:
    """Build labeled Copier choices for a scalar RSM enum.

    Parameters
    ----------
    field
        JSON Schema property definition.

    Returns
    -------
    dict[str, Any] | None
        Nullable choices, or ``None`` for an uncontrolled field.
    """
    values = field.get("enum")
    if field.get("type") != "string" or not isinstance(values, list):
        return None
    return {"Not specified": ""} | {str(value): value for value in values}


def project_slug_default(policies: Mapping[str, Any]) -> str:
    """Build the language-aware project slug default expression."""
    branches = []
    for index, (name, policy) in enumerate(policies.items()):
        keyword = "if" if index == 0 else "elif"
        default = policy.get("defaults", {}).get("project_slug", "project")
        branches.append(f"{{% {keyword} template_type == {name!r} %}}{default}")
    return "".join(branches) + "{% else %}project{% endif %}"


def project_slug_validator(policies: Mapping[str, Any]) -> str:
    """Build a Copier validator for language-specific slug constraints."""
    branches = []
    for index, (name, policy) in enumerate(policies.items()):
        keyword = "if" if index == 0 else "elif"
        schema = policy.get("field_schemas", {}).get("project_slug", {})
        checks = []
        if pattern := schema.get("pattern"):
            checks.append(f"not (project_slug | regex_search({pattern!r}))")
        if minimum := schema.get("minLength"):
            checks.append(f"project_slug | length < {minimum}")
        forbidden = schema.get("not", {}).get("enum", [])
        if forbidden:
            checks.append(f"project_slug in {forbidden!r}")
        condition = " or ".join(checks) or "false"
        guidance = schema.get("description", "Invalid project slug.")
        branches.append(
            f"{{% {keyword} template_type == {name!r} and ({condition}) %}}{guidance}"
        )
    return "".join(branches) + "{% endif %}"


def computed_policy_question(
    policies: Mapping[str, Any],
    policy_key: str,
) -> dict[str, Any]:
    """Build one hidden language-policy value.

    Parameters
    ----------
    policies
        Policies keyed by template type.
    policy_key
        Policy member to expose while rendering.

    Returns
    -------
    dict[str, Any]
        Hidden Copier question definition.
    """
    branches = []
    for index, (name, policy) in enumerate(policies.items()):
        keyword = "if" if index == 0 else "elif"
        value = json.dumps(policy.get(policy_key, {}), ensure_ascii=False)
        branches.append(f"{{% {keyword} template_type == {name!r} %}}{value}")
    default = "".join(branches) + "{% else %}{}{% endif %}"
    return {"type": "yaml", "default": default, "when": False}


def build_questions(
    schema: Mapping[str, Any] | None = None,
    *,
    policies: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build Copier questions from RSM properties and local policies.

    Parameters
    ----------
    schema
        Published RSM JSON Schema.
    policies
        Language-specific rendering policies.

    Returns
    -------
    dict[str, Any]
        Ordered Copier question definitions.
    """
    schema_document = dict(schema or rsm_schema.raw)
    policy_document = dict(policies or load_policies())
    questions: dict[str, Any] = {}

    for name, field in schema_document.get("properties", {}).items():
        question: dict[str, Any] = {
            "type": copier_type(field),
            "default": field_default(field),
        }
        if description := field.get("description"):
            question["help"] = description
        if choices := enum_choices(field):
            question["choices"] = choices
        if field.get("type") in {"array", "object"}:
            question["multiline"] = True
        if name == "project_slug":
            question["default"] = project_slug_default(policy_document)
            question["validator"] = project_slug_validator(policy_document)
        questions[name] = question

    questions["template_defaults"] = computed_policy_question(
        policy_document, "defaults"
    )
    questions["template_schemas"] = computed_policy_question(
        policy_document, "field_schemas"
    )
    questions["template_supported_choices"] = computed_policy_question(
        policy_document, "supported_choices"
    )
    return questions


def questions_yaml(questions: Mapping[str, Any]) -> str:
    """Serialize generated Copier questions consistently."""
    return yaml.dump(
        dict(questions),
        Dumper=NoAliasDumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=100,
    )


def write_questions(questions: Mapping[str, Any], path: Path) -> bool:
    """Write generated questions only when content changes."""
    content = questions_yaml(questions)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> None:
    """Run the command-line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--policies", type=Path, default=DEFAULT_POLICY_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="update questions")
    mode.add_argument(
        "--check",
        action="store_true",
        help="report drift without changing questions",
    )
    args = parser.parse_args()
    questions = build_questions(policies=load_policies(args.policies))
    content = questions_yaml(questions)
    current = args.output.read_text(encoding="utf-8") if args.output.exists() else None
    if current == content:
        return
    if args.check:
        print(f"[out-of-sync] {args.output.relative_to(ROOT)}")
        print(
            "Run `poetry run python _scripts/build_copier_questions.py --write` "
            "to update it."
        )
        raise SystemExit(1)
    write_questions(questions, args.output)
    print(f"[questions] Updated {args.output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
