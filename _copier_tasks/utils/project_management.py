"""Resolve project-manager choices and native commands."""

import tomllib
from pathlib import Path

from rs_files_templates import PROJECT_MANAGER_PROFILES
from utils.context import resolve_choice


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
    fallback = "renv" if ctx.get("_template_name") == "r" else "pip"
    return resolve_choice(ctx, "project_manager", fallback=fallback)


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
