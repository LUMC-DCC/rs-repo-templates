"""FastAPI web application for {{ (cookiecutter.project_name or cookiecutter.project_slug) }}.

The web adapter serves human-facing pages. Keep page routing and rendering here,
and keep reusable data processing in services.
"""

from fastapi import FastAPI

from {{ cookiecutter.project_slug }}.adapters.web.routes import index
from {{ cookiecutter.project_slug }}.config import Settings, get_settings


def create_web_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the web application.

    Parameters
    ----------
    settings : Settings | None, optional
        Runtime settings. Cached environment settings are used when omitted.

    Returns
    -------
    fastapi.FastAPI
        Configured web application.
    """
    resolved_settings = settings or get_settings()

    # Metadata appears in the generated OpenAPI page and browser tooling.
    web = FastAPI(
        title="{{ (cookiecutter.project_name or cookiecutter.project_slug) }}",
        version="{{ (cookiecutter.versioning.version or "0.1.0") }}",
        description="{{ cookiecutter.project_short_description }}",
        servers=(
            [{"url": str(resolved_settings.public_base_url).rstrip("/")}]
            if resolved_settings.public_base_url
            else None
        ),
    )
    web.state.settings = resolved_settings

    # Web routes are registered explicitly so the application surface is easy
    # to inspect as the project grows.
    web.include_router(index.router)

    return web


# ASGI servers can import this object directly.
app = create_web_app()
