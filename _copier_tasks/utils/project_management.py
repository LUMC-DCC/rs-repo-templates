"""Resolve project-manager choices and native commands."""

import tomllib
from pathlib import Path

from utils.context import resolve_choice

PROJECT_MANAGER_PROFILES = {
    "uv": {
        "run_prefix": "uv run ",
        "setup": "uv sync --all-extras",
        "setup_group": "uv sync --extra {group}",
        "add": "uv add <package>",
        "lock": "uv lock",
        "lockfile": "uv.lock",
        "setup_creates_lock": True,
    },
    "poetry": {
        "run_prefix": "poetry run ",
        "setup": "poetry install --all-extras",
        "setup_group": 'poetry install --extras "{group}"',
        "add": "poetry add <package>",
        "lock": "poetry lock",
        "lockfile": "poetry.lock",
        "setup_creates_lock": True,
    },
    "pdm": {
        "run_prefix": "pdm run ",
        "setup": "pdm install -G :all",
        "setup_group": "pdm install -G {group}",
        "add": "pdm add <package>",
        "lock": "pdm lock",
        "lockfile": "pdm.lock",
        "setup_creates_lock": True,
    },
    "hatch": {
        "run_prefix": "hatch run ",
        "setup": "hatch env create",
        "setup_group": "hatch env create",
        "add": "Add the dependency to pyproject.toml, then run hatch env prune.",
        "lock": "hatch env lock default",
        "lockfile": "pylock.toml",
        "setup_creates_lock": True,
    },
    "pixi": {
        "run_prefix": "pixi run ",
        "setup": "pixi install",
        "setup_group": "pixi install",
        "add": "pixi add --pypi <package>",
        "lock": "pixi lock",
        "lockfile": "pixi.lock",
        "setup_creates_lock": True,
    },
    "pip": {
        "run_prefix": "",
        "setup_group": 'python -m pip install -e ".[{group}]"',
        "add": "Add the dependency to pyproject.toml, then install the project again.",
        "lock": "python -m pip lock -o pylock.toml -e .",
        "lockfile": "pylock.toml",
        "setup_creates_lock": False,
    },
}


def resolve_project_manager(ctx):
    """Resolve a compatible project manager for a template.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    tuple[str, str]
        Requested and effective normalized manager labels.
    """
    return resolve_choice(ctx, "project_manager", fallback="pip")


def project_manager_profile(ctx):
    """Return the native command profile for the effective manager.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    dict[str, object]
        Commands and lockfile metadata for the selected manager.
    """
    _, effective = resolve_project_manager(ctx)
    return PROJECT_MANAGER_PROFILES[effective]


def setup_group_command(ctx, group):
    """Build the native command that installs one optional dependency group.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    group : str
        Optional-dependency group name.

    Returns
    -------
    str
        Manager-specific setup command.
    """
    return project_manager_profile(ctx)["setup_group"].format(group=group)


def optional_dependency_groups(project_root: Path) -> list[str]:
    """Read optional dependency groups from rendered package metadata.

    Parameters
    ----------
    project_root
        Generated Python repository root.

    Returns
    -------
    list[str]
        Generated ``project.optional-dependencies`` group names.
    """
    metadata = tomllib.loads(
        (project_root / "pyproject.toml").read_text(encoding="utf-8")
    )
    return list(metadata.get("project", {}).get("optional-dependencies", {}))


def setup_all_command(ctx, project_root: Path):
    """Build the native command that installs all generated dependency groups.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    project_root
        Generated Python repository root.

    Returns
    -------
    str
        Manager-specific complete setup command.
    """
    _, effective = resolve_project_manager(ctx)
    if effective != "pip":
        return project_manager_profile(ctx)["setup"]

    extras = ",".join(optional_dependency_groups(project_root))
    return f'python -m pip install -e ".[{extras}]"'
