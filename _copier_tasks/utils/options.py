"""Interpret normalized Copier option values."""


def is_yes(ctx, value):
    """Check if a context value is a yes equivalent.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    value : str
        Context key to inspect.

    Returns
    -------
    bool
        Whether the value is truthy for template options.
    """
    raw_value = ctx.get(value, "")
    if isinstance(raw_value, bool):
        return raw_value
    return str(raw_value).strip().lower() in (
        "yes",
        "y",
        "true",
        "1",
        "on",
        "enabled",
        "include",
    )


def is_no(ctx, value):
    """Check if a context value is a no equivalent.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    value : str
        Context key to inspect.

    Returns
    -------
    bool
        Whether the value is falsey for template options.
    """
    raw_value = ctx.get(value, "")
    if isinstance(raw_value, bool):
        return not raw_value
    return str(raw_value).strip().lower() in ("no", "n", "false", "0", "none", "")
