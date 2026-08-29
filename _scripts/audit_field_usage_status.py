"""Audit field usage statuses against Copier template references.

This script does not decide whether a field is fully implemented. It only
checks that fields referenced by templates are represented in the contract and
are not still marked as purely planned for that template.
"""

import argparse
import json
import re
from pathlib import Path

from jinja2 import Environment, meta
from rsm_schema import schema as rsm_schema

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_USAGE_PATH = ROOT / "_contracts" / "field_usage.json"

PATH_PATTERN = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)")
REFERENCE_STATUSES = {
    "control",
    "implemented",
    "partial",
}


def load_json(path):
    """Load a JSON document from disk.

    Parameters
    ----------
    path : pathlib.Path
        Path to the JSON document.

    Returns
    -------
    dict
        Parsed JSON content.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def find_template_references(template_dir):
    """Find undeclared Copier fields in one template directory.

    Parameters
    ----------
    template_dir : pathlib.Path
        Root directory of a language template.

    Returns
    -------
    dict[str, set[str]]
        Referenced field names mapped to relative template paths.
    """
    references = {}
    environment = Environment()
    environment.filters["to_nice_yaml"] = str

    for path in template_dir.rglob("*"):
        for field_name in PATH_PATTERN.findall(str(path.relative_to(template_dir))):
            references.setdefault(field_name, set()).add(
                str(path.relative_to(template_dir))
            )

        if not path.is_file():
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        parsed = environment.parse(content)
        for field_name in meta.find_undeclared_variables(parsed):
            references.setdefault(field_name, set()).add(
                str(path.relative_to(template_dir))
            )

    return references


def audit_usage(schema, usage, root):
    """Validate status declarations against template references.

    Parameters
    ----------
    schema : dict
        Published RSM JSON Schema.
    usage : dict
        Parsed field usage map.
    root : pathlib.Path
        Repository root.

    Returns
    -------
    list[str]
        Human-readable audit errors. An empty list means the audit passed.
    """
    contract_fields = set(schema.get("properties", {}))
    field_usage = {field["name"]: field for field in usage["fields"]}
    errors = []

    for template_name in usage["templates"]:
        template_dir = root / "templates" / template_name
        if not template_dir.exists():
            errors.append(f"Template directory does not exist: {template_name}")
            continue

        references = find_template_references(template_dir)
        for field_name in sorted(set(references) & contract_fields):
            status = field_usage[field_name]["statuses"][template_name]
            if status not in REFERENCE_STATUSES:
                locations = ", ".join(sorted(references[field_name])[:5])
                errors.append(
                    f"{template_name}: field `{field_name}` is referenced in "
                    f"{locations} "
                    f"but status is `{status}`"
                )

    return errors


def main():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--usage", type=Path, default=DEFAULT_USAGE_PATH)
    args = parser.parse_args()

    errors = audit_usage(dict(rsm_schema.raw), load_json(args.usage), ROOT)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)

    print("Field usage statuses match template references.")


if __name__ == "__main__":
    main()
