"""Configured Uvicorn entry point for generated HTTP interfaces."""

import uvicorn

from {{ cookiecutter.project_slug }}.config import get_settings
from {{ cookiecutter.project_slug }}.logging_config import configure_logging

APPLICATION = "{{ cookiecutter.project_slug }}.adapters.server:app"


def main() -> None:
    """Run all selected HTTP interfaces with validated server settings."""
    settings = get_settings()
    configure_logging(settings)
    uvicorn.run(
        APPLICATION,
        host=settings.server_host,
        port=settings.server_port,
        root_path=settings.server_root_path,
        reload=settings.server_reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
