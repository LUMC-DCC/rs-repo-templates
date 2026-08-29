"""Application logging configuration for {{ (project_name or project_slug) }}.

Library modules should create loggers with ``logging.getLogger(__name__)`` and
leave handler configuration to an application entry point. The generated entry
points call this module once before running project logic.
"""

import logging

from {{ project_slug }}.config import Settings, get_settings

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging(settings: Settings | None = None) -> logging.Logger:
    """Configure process logging and return the package logger.

    Parameters
    ----------
    settings : Settings | None, optional
        Validated runtime settings. The cached settings are used when omitted.

    Returns
    -------
    logging.Logger
        Logger at the root of the generated package namespace.
    """
    resolved_settings = settings or get_settings()
    logging.basicConfig(
        level=resolved_settings.log_level,
        format=LOG_FORMAT,
    )
    package_logger = logging.getLogger("{{ project_slug }}")
    package_logger.setLevel(resolved_settings.log_level)
    return package_logger
