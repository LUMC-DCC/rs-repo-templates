"""Typer command-line application for {{ (project_name or project_slug) }}.

The CLI adapter translates command-line input into calls to reusable project
services. Command modules stay small so they are easy to test separately from
terminal formatting.
"""

import typer

{% set interface_types = namespace(values=[]) %}
{% for interface in interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set has_http_interface = "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values or "Web service" in interface_types.values or "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values or "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set configuration_security_measures = ["Secrets management (e.g., environment variables, vault)", "Secure configuration management (e.g., Infrastructure-as-Code, hardening)"] %}
{% set has_runtime_configuration = has_http_interface or security_measures.selected.entries | select("in", configuration_security_measures) | list | length > 0 %}
from {{ project_slug }}.adapters.cli.commands import process
{% if has_runtime_configuration %}
from {{ project_slug }}.logging_config import configure_logging
{% endif %}

# The Typer app is the command registry. Add new commands by importing their
# modules and registering them below.
app = typer.Typer(help="{{ project_short_description }}")
app.command(name="process")(process.command)


def main() -> None:
    """Run the command-line application."""
{% if has_runtime_configuration %}
    configure_logging()
{% endif %}
    app()
