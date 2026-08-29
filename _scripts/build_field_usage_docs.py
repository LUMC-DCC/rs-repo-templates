"""Build the field usage reference page from the usage map.

The generated Markdown page keeps human-facing documentation in sync with the
curated implementation map in ``_contracts/field_usage.json``.
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_USAGE_PATH = ROOT / "_contracts" / "field_usage.json"
DEFAULT_OUTPUT_PATH = ROOT / "_docs" / "contract" / "field-usage.md"


def markdown_escape(value):
    """Escape table-sensitive Markdown characters.

    Parameters
    ----------
    value : object
        Value to render in a Markdown table cell.

    Returns
    -------
    str
        Escaped single-line Markdown text.
    """
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_table(usage):
    """Render the field usage map as a Markdown table.

    Parameters
    ----------
    usage : dict
        Parsed field usage map.

    Returns
    -------
    str
        Markdown document content.
    """
    templates = list(usage["templates"])
    status_headers = [f"{template.title()} Status" for template in templates]
    lines = [
        "# Field Usage",
        "",
        "This table is generated from `_contracts/field_usage.json`.",
        "Update the usage map first, then run the repository maintenance command.",
        "",
        "| Field | " + " | ".join(status_headers) + " | Targets | Notes |",
        "| --- | " + " | ".join("---" for _ in status_headers) + " | --- | --- |",
    ]

    for field in usage["fields"]:
        targets = ", ".join(f"`{target}`" for target in field["targets"])
        statuses = [
            f"`{markdown_escape(field['statuses'][template])}`"
            for template in templates
        ]
        lines.append(
            "| {name} | {statuses} | {targets} | {notes} |".format(
                name=f"`{markdown_escape(field['name'])}`",
                statuses=" | ".join(statuses),
                targets=markdown_escape(targets),
                notes=markdown_escape(field["notes"]),
            )
        )

    lines.append("")
    return "\n".join(lines)


def load_usage(path):
    """Load a field usage map from disk.

    Parameters
    ----------
    path : pathlib.Path
        JSON usage map path.

    Returns
    -------
    dict
        Parsed usage map.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def write_docs(content, path):
    """Write generated documentation content.

    Parameters
    ----------
    content : str
        Markdown content to write.
    path : pathlib.Path
        Destination documentation path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--usage", type=Path, default=DEFAULT_USAGE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="update documentation")
    mode.add_argument(
        "--check",
        action="store_true",
        help="report drift without changing documentation",
    )
    args = parser.parse_args()

    content = build_table(load_usage(args.usage))
    current = args.output.read_text(encoding="utf-8") if args.output.exists() else None
    if current == content:
        return
    if args.check:
        print(f"[out-of-sync] {args.output.relative_to(ROOT)}")
        print(
            "Run `poetry run python _scripts/build_field_usage_docs.py --write` "
            "to update it."
        )
        raise SystemExit(1)
    write_docs(content, args.output)
    print(f"[docs] Updated {args.output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
