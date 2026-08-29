"""Compose the generated HTTP interfaces into one deployable application.

A project with one HTTP adapter exposes it at the root. When several adapters
are selected, stable path prefixes prevent their routes from colliding.
"""

{% set interface_types = namespace(values=[]) %}
{% for interface in interfaces.entries %}
{% if interface.type is defined and interface.type and interface.type not in interface_types.values %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set has_api = "SPARQL endpoint" in interface_types.values or "Web API" in interface_types.values %}
{% set has_soap = "Web service" in interface_types.values %}
{% set has_portal = "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values %}
{% set has_web = "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set adapter_count = (1 if has_api else 0) + (1 if has_soap else 0) + (1 if has_portal else 0) + (1 if has_web else 0) %}
{% if adapter_count > 1 %}
from fastapi import FastAPI

{% endif %}
{% if has_api %}
from {{ project_slug }}.adapters.api.app import app as api_app
{% endif %}
{% if has_soap %}
from {{ project_slug }}.adapters.soap.app import app as soap_app
{% endif %}
{% if has_portal %}
from {{ project_slug }}.adapters.portal.app import app as portal_app
{% endif %}
{% if has_web %}
from {{ project_slug }}.adapters.web.app import app as web_app
{% endif %}

{% if adapter_count == 1 %}
{% if has_api %}app = api_app
{% elif has_soap %}app = soap_app
{% elif has_portal %}app = portal_app
{% elif has_web %}app = web_app
{% endif %}
{% else %}
app = FastAPI(
    title="{{ (project_name or project_slug) }}",
    version="{{ (versioning.version or "0.1.0") }}",
    description="{{ project_short_description }}",
)

# Mount machine-facing contracts before the root web app. Mount order matters
# because the root app is a catch-all for remaining paths.
{% if has_api %}app.mount("/api", api_app, name="api")
{% endif %}
{% if has_soap %}app.mount("/soap", soap_app, name="soap")
{% endif %}
{% if has_portal %}app.mount("/portal", portal_app, name="portal")
{% endif %}
{% if has_web %}app.mount("/", web_app, name="web")
{% endif %}
{% endif %}
