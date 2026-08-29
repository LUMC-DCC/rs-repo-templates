"""Resolve generated security automation from public project metadata."""

from utils.context import object_entries

VULNERABILITY_SCANNING = "Vulnerability scanning (e.g., Snyk, Dependabot)"


def has_vulnerability_scanning(ctx):
    """Return whether automated vulnerability scanning is selected.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether the controlled security measure requests scanning automation.
    """
    return VULNERABILITY_SCANNING in object_entries(
        ctx,
        "security_measures",
        "selected",
    )
