"""Select controlled community files requested by the project context."""

from utils.context import entries

COMMUNITY_FILES = {
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "SECURITY.md",
    "SUPPORT.md",
}


def selected_community_files(ctx):
    """Return selected community files in stable order.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    set[str]
        Controlled repository paths selected in ``community_files``.
    """
    return set(entries(ctx, "community_files")) & COMMUNITY_FILES


def all_community_files():
    """Return all supported community file paths.

    Returns
    -------
    set[str]
        Repository paths controlled by ``community_files``.
    """
    return set(COMMUNITY_FILES)
