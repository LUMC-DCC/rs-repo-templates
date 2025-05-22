"""Resolve whether a generated project needs runtime configuration."""

from utils.context import object_entries
from utils.interfaces import has_http_interface

CONFIGURATION_SECURITY_MEASURES = {
    "Secrets management (e.g., environment variables, vault)",
    "Secure configuration management (e.g., Infrastructure-as-Code, hardening)",
}


def has_runtime_configuration(ctx):
    """Return whether the project needs a typed runtime settings boundary.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether selected capabilities require runtime configuration.
    """
    security_measures = set(object_entries(ctx, "security_measures", "selected"))
    return any(
        (
            has_http_interface(ctx),
            bool(security_measures & CONFIGURATION_SECURITY_MEASURES),
        )
    )
