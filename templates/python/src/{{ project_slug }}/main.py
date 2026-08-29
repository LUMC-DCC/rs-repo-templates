"""Runtime entry point for ``python -m {{ project_slug }}``.

This module provides a tiny package-level command for quick smoke tests. Keep
larger runtime interfaces in dedicated modules.
"""

{% set interface_types = namespace(values=[]) %}
{% for interface in interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set has_http_interface = "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values or "Web service" in interface_types.values or "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values or "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set configuration_security_measures = ["Secrets management (e.g., environment variables, vault)", "Secure configuration management (e.g., Infrastructure-as-Code, hardening)"] %}
{% set has_runtime_configuration = has_http_interface or security_measures.selected.entries | select("in", configuration_security_measures) | list | length > 0 %}
{% if has_runtime_configuration %}
from {{ project_slug }}.logging_config import configure_logging
{% endif %}
from {{ project_slug }}.services.processing import process_text


def main(text: str = "{{ (project_name or project_slug) }}") -> None:
    """Run the package entry point.

    Parameters
    ----------
    text : str, default="{{ (project_name or project_slug) }}"
        Text to process.
    """
{% if has_runtime_configuration %}
    configure_logging()
{% endif %}
    # Delegate to the service layer so the entry point stays small and
    # testable.
    result = process_text(text)
    print(result.output_text)


if __name__ == "__main__":
    main()
