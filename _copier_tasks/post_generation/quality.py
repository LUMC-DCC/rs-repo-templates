"""Resolve quality-tool options for the selected language template."""

from utils.context import resolve_object_choice

QUALITY_FIELDS = (
    "formatter",
    "linter",
    "type_checker",
)


def resolve_quality_tool(ctx, field_name):
    """Resolve one compatible quality-tool selector.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    field_name : str
        Property name such as ``linter``.

    Returns
    -------
    tuple[str, str]
        Requested and effective normalized tool labels.
    """
    return resolve_object_choice(ctx, "quality_tools", field_name)


def has_formatter(ctx):
    """Return whether formatting checks should be kept.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a formatter is effective.
    """
    _, formatter_tool = resolve_quality_tool(ctx, "formatter")
    return bool(formatter_tool)


def has_linting(ctx):
    """Return whether linting checks should be kept.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a linter is effective.
    """
    _, linter_tool = resolve_quality_tool(ctx, "linter")
    return bool(linter_tool)


def has_type_checking(ctx):
    """Return whether type-checking checks should be kept.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a type checker is effective.
    """
    _, type_checker = resolve_quality_tool(ctx, "type_checker")
    return bool(type_checker)


def has_quality_checks(ctx):
    """Return whether any quality check should run.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether formatting, linting, or type checking is effective.
    """
    return has_formatter(ctx) or has_linting(ctx) or has_type_checking(ctx)


def select_quality_tools(ctx, cwd):
    """Warn when requested quality tools are not compatible.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    del cwd
    for field_name in QUALITY_FIELDS:
        requested, effective = resolve_quality_tool(ctx, field_name)
        if requested == effective:
            continue

        print(
            "[warning] "
            f"{field_name} value {requested!r} is not supported for "
            f"{ctx['_template_name']!r}; using {effective!r}."
        )
