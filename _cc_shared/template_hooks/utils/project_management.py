"""Resolve project-manager choices and native commands."""

from utils.context import entries, object_value, resolve_choice, resolve_object_choice
from utils.release import has_python_distribution

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
        "setup": 'python -m pip install -e ".[metadata,test,quality,release,docs]"',
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
        Rendered Cookiecutter context.

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
        Rendered Cookiecutter context.

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
        Rendered Cookiecutter context.
    group : str
        Optional-dependency group name.

    Returns
    -------
    str
        Manager-specific setup command.
    """
    return project_manager_profile(ctx)["setup_group"].format(group=group)


def optional_dependency_groups(ctx):
    """Return optional dependency groups present in a Python project.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.

    Returns
    -------
    list[str]
        Generated ``project.optional-dependencies`` group names.
    """
    groups = []
    interfaces = {
        entry.get("type", "")
        for entry in entries(ctx, "interfaces")
        if isinstance(entry, dict)
    }
    if (
        object_value(ctx, "licensing", "compatibility_check")
        == "Yes - automated tooling"
        and str(object_value(ctx, "licensing", "license")).strip()
    ):
        groups.append("license")
    if interfaces & {"SPARQL endpoint", "Web API"}:
        groups.append("api")
    if "Web service" in interfaces:
        groups.append("soap")
    if interfaces & {
        "Bioinformatics portal",
        "Database portal",
        "Web application",
        "Workbench",
    }:
        groups.append("web")
    if entries(ctx, "test_types"):
        groups.append("test")

    quality_fields = ("formatter", "linter", "type_checker")
    if any(
        bool(resolve_object_choice(ctx, "quality_tools", field_name)[1])
        for field_name in quality_fields
    ):
        groups.append("quality")

    if has_python_distribution(entries(ctx, "distribution_channels")):
        groups.append("release")

    _, effective_builder = resolve_choice(ctx, "documentation_builder")
    if entries(ctx, "documentation_types") and effective_builder in {
        "mkdocs",
        "zensical",
        "sphinx",
    }:
        groups.append("docs")

    return groups


def setup_all_command(ctx):
    """Build the native command that installs all generated dependency groups.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.

    Returns
    -------
    str
        Manager-specific complete setup command.
    """
    _, effective = resolve_project_manager(ctx)
    if effective != "pip":
        return project_manager_profile(ctx)["setup"]

    extras = ",".join(optional_dependency_groups(ctx))
    return f'python -m pip install -e ".[{extras}]"'
