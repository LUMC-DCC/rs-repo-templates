"""Validate Python version policy and release tags.

The generated distribution workflow calls this command before building or
publishing artifacts. Project metadata in ``pyproject.toml`` is the version
source of truth.
"""

import argparse
import re
import tomllib
from pathlib import Path

from packaging.version import InvalidVersion, Version

SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


def load_project_version(path=Path("pyproject.toml")):
    """Load project version and configured versioning policy.

    Parameters
    ----------
    path : pathlib.Path, default=Path("pyproject.toml")
        Python project metadata file.

    Returns
    -------
    tuple[str, str, str]
        Project version, versioning scheme, and policy details.
    """
    metadata = tomllib.loads(path.read_text(encoding="utf-8"))
    return (
        metadata["project"]["version"],
        {{ versioning.scheme | tojson }},
        {{ versioning.scheme_details | tojson }},
    )


def validate_version(version, scheme):
    """Validate a Python package version against its declared policy.

    Parameters
    ----------
    version : str
        Version from Python project metadata.
    scheme : str
        Public versioning policy from project context.

    Raises
    ------
    ValueError
        If the version is not PEP 440 compatible or violates SemVer.
    """
    try:
        Version(version)
    except InvalidVersion as error:
        raise ValueError(f"Version {version!r} is not PEP 440 compatible.") from error

    if "semver" in scheme.strip().lower() and not SEMVER_PATTERN.fullmatch(version):
        raise ValueError(
            f"Version {version!r} does not follow SemVer MAJOR.MINOR.PATCH."
        )


def validate_tag(version, tag):
    """Ensure a release tag matches project metadata exactly.

    Parameters
    ----------
    version : str
        Version from Python project metadata.
    tag : str
        Release tag, with an optional leading ``v``.

    Raises
    ------
    ValueError
        If the tag and project version differ.
    """
    normalized_tag = tag.removeprefix("v")
    if normalized_tag != version:
        raise ValueError(
            f"Release tag {tag!r} does not match project version {version!r}."
        )


def main():
    """Run release validation from the command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", help="Release tag to compare with project.version")
    args = parser.parse_args()

    version, scheme, scheme_details = load_project_version()
    validate_version(version, scheme)
    if args.tag:
        validate_tag(version, args.tag)

    policy = f"{scheme}: {scheme_details}" if scheme_details else scheme
    print(f"Release metadata is valid for version {version} ({policy}).")


if __name__ == "__main__":
    main()
