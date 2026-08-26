"""FastAPI application adapter for {{ (cookiecutter.project_name or cookiecutter.project_slug) }}.

This module assembles API routes into a FastAPI application. Route modules
handle HTTP-specific concerns, while shared processing logic stays in the
service layer.
"""

from fastapi import FastAPI

{% set interface_types = namespace(values=[]) %}
{% for interface in cookiecutter.interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
from {{ cookiecutter.project_slug }}.adapters.api.routes import (
    health,
{% if "Web API" in interface_types.values %}
    processing,
{% endif %}
{% if "SPARQL endpoint" in interface_types.values %}
    sparql,
{% endif %}
)
from {{ cookiecutter.project_slug }}.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the web API application.

    Parameters
    ----------
    settings : Settings | None, optional
        Runtime settings. Cached environment settings are used when omitted.

    Returns
    -------
    fastapi.FastAPI
        Configured API application.
    """
    resolved_settings = settings or get_settings()

    # Application metadata is pulled from the generated project metadata so the
    # OpenAPI schema starts with useful names, versions, and descriptions.
    api = FastAPI(
        title="{{ (cookiecutter.project_name or cookiecutter.project_slug) }}",
        version="{{ (cookiecutter.versioning.version or "0.1.0") }}",
        description="{{ cookiecutter.project_short_description }}",
        servers=(
            [{"url": str(resolved_settings.public_base_url).rstrip("/")}]
            if resolved_settings.public_base_url
            else None
        ),
    )
    api.state.settings = resolved_settings

    # Register small route modules here. Keeping registration explicit makes it
    # easy to see which API surfaces are included for this generated project.
    api.include_router(health.router)
{% if "Web API" in interface_types.values %}
    api.include_router(processing.router)
{% endif %}
{% if "SPARQL endpoint" in interface_types.values %}
    api.include_router(sparql.router)
{% endif %}

    return api


# Uvicorn and other ASGI servers discover this module-level application object.
app = create_app()
