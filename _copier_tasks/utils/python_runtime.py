"""Resolve Python runtime constraints for generated infrastructure."""

from __future__ import annotations

import tomllib
from pathlib import Path

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version

MINIMUM_CONTAINER_MINOR = 12
MAXIMUM_CONTAINER_MINOR = 30
MAXIMUM_CONTAINER_PATCH = 50


def requires_python(project_root: Path) -> str:
    """Read the Python requirement from rendered package metadata.

    Parameters
    ----------
    project_root
        Generated Python repository root.

    Returns
    -------
    str
        PEP 440 Python version constraint.
    """
    metadata = tomllib.loads(
        (project_root / "pyproject.toml").read_text(encoding="utf-8")
    )
    return str(metadata["project"]["requires-python"])


def container_python_version(project_root: Path) -> str:
    """Choose the lowest Python 3.12+ image satisfying package metadata.

    Parameters
    ----------
    project_root
        Generated Python repository root.

    Returns
    -------
    str
        Concrete major/minor or major/minor/patch container tag.

    Raises
    ------
    ValueError
        If the requirement is invalid or excludes all supported candidates.
    """
    constraint = requires_python(project_root)
    try:
        specifier = SpecifierSet(constraint)
    except InvalidSpecifier as error:
        raise ValueError(
            f"Python version constraint {constraint!r} is not valid PEP 440."
        ) from error

    for minor in range(MINIMUM_CONTAINER_MINOR, MAXIMUM_CONTAINER_MINOR + 1):
        for patch in range(MAXIMUM_CONTAINER_PATCH + 1):
            candidate = Version(f"3.{minor}.{patch}")
            if candidate in specifier:
                return f"3.{minor}" if patch == 0 else str(candidate)
    raise ValueError(
        f"Python version constraint {constraint!r} does not permit a Python 3.12+ "
        "container runtime."
    )
