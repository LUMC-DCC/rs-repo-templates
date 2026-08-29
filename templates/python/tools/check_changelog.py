"""Validate the generated project changelog structure.

The check follows Keep a Changelog's automation guidance: CI should support
mechanical consistency without deciding whether a change deserves an entry.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
HEADING_RE = re.compile(r"^(?P<level>#{1,6})\s+(?P<title>.+?)\s*$")
RELEASE_RE = re.compile(
    r"^\[(?P<label>[^\]]+)\](?: - (?P<date>\d{4}-\d{2}-\d{2}))?"
    r"(?: \[YANKED\])?$"
)
REFERENCE_RE = re.compile(r"^\[(?P<label>[^\]]+)\]:\s+\S+\s*$")


def collect_headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """Collect Markdown headings from changelog lines.

    Parameters
    ----------
    lines : list of str
        Changelog lines.

    Returns
    -------
    list of tuple
        Tuples of one-based line number, heading level, and heading title.
    """
    headings = []
    for line_number, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if match:
            headings.append(
                (line_number, len(match.group("level")), match.group("title"))
            )
    return headings


def collect_reference_labels(lines: list[str]) -> set[str]:
    """Collect Markdown reference-link labels.

    Parameters
    ----------
    lines : list of str
        Changelog lines.

    Returns
    -------
    set of str
        Reference labels defined at the bottom of the changelog.
    """
    return {
        match.group("label") for line in lines if (match := REFERENCE_RE.match(line))
    }


def validate_release_heading(
    line_number: int, title: str
) -> tuple[str | None, str | None]:
    """Validate a Keep a Changelog release heading.

    Parameters
    ----------
    line_number : int
        One-based heading line number.
    title : str
        Heading text without Markdown hash markers.

    Returns
    -------
    tuple
        Release label and optional validation error.
    """
    match = RELEASE_RE.match(title)
    if not match:
        return (
            None,
            f"line {line_number}: use '## [Unreleased]' or '## [version] - YYYY-MM-DD'",
        )

    label = match.group("label")
    release_date = match.group("date")
    if label == "Unreleased":
        if release_date:
            return label, f"line {line_number}: Unreleased must not have a date"
        return label, None

    if not release_date:
        return label, f"line {line_number}: released versions need a date"

    try:
        date.fromisoformat(release_date)
    except ValueError:
        return label, f"line {line_number}: release date is not valid ISO"

    return label, None


def validate_changelog(path: Path = CHANGELOG_PATH) -> list[str]:
    """Validate a changelog file.

    Parameters
    ----------
    path : pathlib.Path
        Changelog path to validate.

    Returns
    -------
    list of str
        Validation errors.
    """
    if not path.exists():
        return [f"{path.name} does not exist"]

    lines = path.read_text(encoding="utf-8").splitlines()
    errors = []
    if not lines or lines[0].strip() != "# Changelog":
        errors.append("line 1: changelog must start with '# Changelog'")
    if not any("keepachangelog.com" in line.lower() for line in lines):
        errors.append("changelog should reference Keep a Changelog")

    release_headings = [
        (line_number, title)
        for line_number, level, title in collect_headings(lines)
        if level == 2
    ]
    if not release_headings:
        errors.append("changelog must include at least one release heading")
        return errors

    labels = []
    for line_number, title in release_headings:
        label, error = validate_release_heading(line_number, title)
        if label:
            labels.append(label)
        if error:
            errors.append(error)

    if labels and labels[0] != "Unreleased":
        errors.append("Unreleased must be the first release section")
    if "Unreleased" not in labels:
        errors.append("changelog must include '## [Unreleased]'")

    known_labels = set(labels)
    for label in collect_reference_labels(lines):
        if label not in known_labels:
            errors.append(f"reference link [{label}] has no release heading")

    return errors


def main() -> int:
    """Run changelog validation from the command line.

    Returns
    -------
    int
        Process exit code.
    """
    errors = validate_changelog()
    if errors:
        print("Changelog validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Changelog validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
