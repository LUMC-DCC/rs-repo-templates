"""Audit external GitHub Action references for immutable commit pins."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USES_PATTERN = re.compile(
    r"^\s*(?:-\s*)?uses:\s*[\"']?([^@\s\"']+)@([^#\s\"']+)",
    re.MULTILINE,
)
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
IGNORED_DIRECTORIES = {".git", ".venv", "site"}


def workflow_files(root: Path) -> list[Path]:
    """Find workflow and composite-action YAML files.

    Parameters
    ----------
    root : pathlib.Path
        Repository root to scan.

    Returns
    -------
    list[pathlib.Path]
        Sorted YAML paths below ``.github`` directories.
    """
    paths = []
    for path in root.rglob("*"):
        if path.suffix not in {".yml", ".yaml"} or ".github" not in path.parts:
            continue
        if any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue
        paths.append(path)
    return sorted(paths)


def unpinned_references(path: Path) -> list[tuple[str, str]]:
    """Return external action references without full commit pins.

    Parameters
    ----------
    path : pathlib.Path
        Workflow or composite-action YAML path.

    Returns
    -------
    list[tuple[str, str]]
        Action names and mutable references found in the file.
    """
    content = path.read_text(encoding="utf-8")
    return [
        (action, reference)
        for action, reference in USES_PATTERN.findall(content)
        if not action.startswith("./") and not COMMIT_PATTERN.fullmatch(reference)
    ]


def audit(root: Path) -> list[str]:
    """Collect actionable pinning failures.

    Parameters
    ----------
    root : pathlib.Path
        Repository root to scan.

    Returns
    -------
    list[str]
        Human-readable failures.
    """
    failures = []
    for path in workflow_files(root):
        for action, reference in unpinned_references(path):
            failures.append(
                f"{path.relative_to(root)}: {action}@{reference} is not pinned to "
                "a full commit SHA"
            )
    return failures


def main() -> None:
    """Run the command-line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    failures = audit(args.root.resolve())
    if failures:
        raise SystemExit("\n".join(failures))
    print("[actions] All external actions use immutable commit pins.")


if __name__ == "__main__":
    main()
