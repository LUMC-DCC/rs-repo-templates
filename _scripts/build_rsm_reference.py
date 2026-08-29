"""Build the local RSM field reference from the installed public schema.

The page is an inspection aid for template users and integrators. Field names,
requirements, defaults, descriptions, and controlled values remain owned by
``rsm-schema`` and are never curated again in this repository.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def markdown_escape(value: Any) -> str:
    """Escape one value for a Markdown table cell.

    Parameters
    ----------
    value
        Value to render.

    Returns
    -------
    str
        Escaped, single-line text.
    """
    return str(value).replace("|", "\\|").replace("\n", " ")


def schema_type(field: Mapping[str, Any]) -> str:
    """Describe the top-level JSON shape of one field.

    Parameters
    ----------
    field
        JSON Schema field definition.

    Returns
    -------
    str
        Compact type label.
    """
    field_type = field.get("type", "value")
    if field_type == "object":
        entries = field.get("properties", {}).get("entries", {})
        if entries.get("type") == "array":
            return "collection object"
    return str(field_type)


def schema_default(field: Mapping[str, Any]) -> str:
    """Render the schema-owned default for one field.

    Parameters
    ----------
    field
        JSON Schema field definition.

    Returns
    -------
    str
        Inline JSON or an explicit no-default marker.
    """
    if "default" not in field:
        return "Not defined"
    value = json.dumps(field["default"], ensure_ascii=False, separators=(",", ":"))
    return f"`{value}`"


def local_ref(schema: Mapping[str, Any], reference: str) -> Mapping[str, Any]:
    """Resolve one local JSON Pointer reference.

    Parameters
    ----------
    schema
        Complete JSON Schema document.
    reference
        Local reference beginning with ``#/``.

    Returns
    -------
    collections.abc.Mapping
        Referenced schema node.

    Raises
    ------
    ValueError
        If the reference is not local.
    """
    if not reference.startswith("#/"):
        raise ValueError(f"Cannot resolve external schema reference: {reference}")
    node: Any = schema
    for token in reference[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        node = node[token]
    return node


def controlled_values(
    field: Mapping[str, Any],
    schema: Mapping[str, Any],
) -> list[tuple[str, list[Any]]]:
    """Collect controlled values reachable from one public field.

    Parameters
    ----------
    field
        Top-level JSON Schema field definition.
    schema
        Complete JSON Schema document.

    Returns
    -------
    list[tuple[str, list[Any]]]
        Relative value paths and their enum members.
    """
    found: list[tuple[str, list[Any]]] = []

    def visit(node: Mapping[str, Any], path: str, refs: frozenset[str]) -> None:
        """Traverse structural schemas and local references.

        Parameters
        ----------
        node
            Current JSON Schema node.
        path
            Relative public value path.
        refs
            References already followed on this branch.
        """
        if values := node.get("enum"):
            found.append((path or "value", list(values)))
        if (reference := node.get("$ref")) and reference not in refs:
            visit(local_ref(schema, reference), path, refs | {reference})
        for branch in ("allOf", "anyOf", "oneOf"):
            for child in node.get(branch, []):
                visit(child, path, refs)
        for name, child in node.get("properties", {}).items():
            child_path = f"{path}.{name}" if path else name
            visit(child, child_path, refs)
        if isinstance(items := node.get("items"), Mapping):
            visit(items, f"{path}[]", refs)

    visit(field, "", frozenset())
    unique: dict[tuple[str, str], tuple[str, list[Any]]] = {}
    for path, values in found:
        key = (path, json.dumps(values, ensure_ascii=False, sort_keys=True))
        unique[key] = (path, values)
    return list(unique.values())


def build_reference(schema: Mapping[str, Any]) -> str:
    """Render a Markdown field reference from an RSM JSON Schema.

    Parameters
    ----------
    schema
        Published RSM JSON Schema.

    Returns
    -------
    str
        Generated Markdown document.
    """
    schema_url = str(schema.get("$id", ""))
    required = set(schema.get("required", []))
    properties = schema.get("properties", {})
    lines = [
        "# RSM field reference",
        "",
        "Generated from the "
        f"[published RSM schema]({schema_url}). Do not edit this page directly.",
        "",
        "| Field | Shape | Required | Schema default | Description |",
        "| --- | --- | --- | --- | --- |",
    ]
    enum_groups: list[tuple[str, list[tuple[str, list[Any]]]]] = []
    for name, field in properties.items():
        lines.append(
            "| `{name}` | {shape} | {required} | {default} | {description} |".format(
                name=markdown_escape(name),
                shape=markdown_escape(schema_type(field)),
                required="yes" if name in required else "no",
                default=markdown_escape(schema_default(field)),
                description=markdown_escape(field.get("description", "")),
            )
        )
        if values := controlled_values(field, schema):
            enum_groups.append((name, values))

    lines.extend(["", "## Controlled values", ""])
    for field_name, groups in enum_groups:
        lines.append(f"### `{field_name}`")
        lines.append("")
        for path, values in groups:
            rendered = ", ".join(f"`{markdown_escape(value)}`" for value in values)
            label = f"`{path}`: " if path != "value" else ""
            lines.append(f"- {label}{rendered}")
        lines.append("")
    return "\n".join(lines)
