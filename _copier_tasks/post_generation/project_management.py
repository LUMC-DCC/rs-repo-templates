"""Apply the selected project-manager command profile."""

from utils.project_management import (
    project_manager_profile,
    resolve_project_manager,
    setup_all_command,
    setup_group_command,
)

TEXT_SUFFIXES = {
    ".md",
    ".toml",
    ".yaml",
    ".yml",
}


def project_manager_replacements(ctx):
    """Build replacements for manager-aware generated text.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    dict[str, str]
        Placeholder-to-command mapping.
    """
    _, effective = resolve_project_manager(ctx)
    profile = project_manager_profile(ctx)
    lockfile = profile["lockfile"]
    if profile["setup_creates_lock"]:
        lock_guidance = (
            f"Running `{setup_all_command(ctx)}` creates or updates "
            f"`{lockfile}`. Commit the lockfile when the project requires "
            "reproducible development and deployment environments."
        )
    else:
        lock_guidance = (
            f"Installation does not create a lockfile. Run `{profile['lock']}` "
            f"to create `{lockfile}` when the project requires a reproducible "
            "development or deployment environment."
        )

    return {
        "@@PROJECT_MANAGER@@": effective,
        "@@PROJECT_RUN@@": profile["run_prefix"],
        "@@PROJECT_SETUP_ALL@@": setup_all_command(ctx),
        "@@PROJECT_SETUP_API@@": setup_group_command(ctx, "api"),
        "@@PROJECT_SETUP_DOCS@@": setup_group_command(ctx, "docs"),
        "@@PROJECT_SETUP_SOAP@@": setup_group_command(ctx, "soap"),
        "@@PROJECT_SETUP_WEB@@": setup_group_command(ctx, "web"),
        "@@PROJECT_ADD@@": profile["add"],
        "@@PROJECT_LOCK@@": profile["lock"],
        "@@PROJECT_LOCKFILE@@": lockfile,
        "@@PROJECT_LOCK_GUIDANCE@@": lock_guidance,
    }


def replace_project_manager_tokens(ctx, cwd):
    """Replace manager command tokens in generated text files.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    replace_text_tokens(cwd, project_manager_replacements(ctx))


def replace_text_tokens(cwd, replacements):
    """Replace command placeholders in generated text files.

    Parameters
    ----------
    cwd : pathlib.Path
        Generated project root.
    replacements : dict[str, str]
        Placeholder-to-command mapping.
    """
    for path in cwd.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue

        content = path.read_text(encoding="utf-8")
        rendered = content
        for placeholder, value in replacements.items():
            rendered = rendered.replace(placeholder, value)
        if rendered != content:
            path.write_text(rendered, encoding="utf-8")


def configure_project_manager(ctx, cwd):
    """Apply manager commands and warn about unsupported selections.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    requested, effective = resolve_project_manager(ctx)
    if requested and requested != effective:
        print(
            "[warning] "
            f"project_manager value {requested!r} is not supported for "
            f"{ctx['_template_name']!r}; using {effective!r}."
        )

    if str(ctx.get("_template_name", "")).strip().lower() == "python":
        replace_project_manager_tokens(ctx, cwd)
