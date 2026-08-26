"""FastAPI portal application for {{ (cookiecutter.project_name or cookiecutter.project_slug) }}.

The portal adapter exposes browsable project records and summaries. It is kept
separate from the generic web app so portal-specific models, routes, and data
access can evolve without crowding simpler page routes.
"""

from fastapi import FastAPI

from {{ cookiecutter.project_slug }}.adapters.portal.routes import index, records
from {{ cookiecutter.project_slug }}.config import Settings, get_settings


def create_portal_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the portal application.

    Parameters
    ----------
    settings : Settings | None, optional
        Runtime settings. Cached environment settings are used when omitted.

    Returns
    -------
    fastapi.FastAPI
        Configured portal application.
    """
    resolved_settings = settings or get_settings()

    # Portal metadata is intentionally explicit because portals are often
    # indexed, linked, or embedded by external research infrastructure.
    portal = FastAPI(
        title="{{ (cookiecutter.project_name or cookiecutter.project_slug) }} portal",
        version="{{ (cookiecutter.versioning.version or "0.1.0") }}",
        description="{{ cookiecutter.project_short_description }}",
        servers=(
            [{"url": str(resolved_settings.public_base_url).rstrip("/")}]
            if resolved_settings.public_base_url
            else None
        ),
    )
    portal.state.settings = resolved_settings

    # Register portal route modules here. Add new route modules when new portal
    # record types or views are introduced.
    portal.include_router(index.router)
    portal.include_router(records.router)

    return portal


# ASGI servers can import this object directly.
app = create_portal_app()
