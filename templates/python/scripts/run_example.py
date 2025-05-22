"""Standalone example script for {{ (project_name or project_slug) }}.

Scripts are useful for small one-off commands, tutorials, or demonstrations.
Keep reusable behavior in package modules and let scripts act as thin wrappers.
"""

import argparse

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


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser for the script.

    Returns
    -------
    argparse.ArgumentParser
        Configured parser.
    """
    parser = argparse.ArgumentParser(
        description="Run the {{ (project_name or project_slug) }} example script.",
    )
    # The optional positional argument keeps the script usable with no input
    # while still allowing callers to pass a custom text value.
    parser.add_argument(
        "text",
        nargs="?",
        default="{{ (project_name or project_slug) }}",
        help="Text to process.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the example script.

    Parameters
    ----------
    argv : list[str] | None, optional
        Command-line arguments without the script name.
    """
    args = build_parser().parse_args(argv)
{% if has_runtime_configuration %}
    configure_logging()
{% endif %}
    # Scripts should call package code rather than duplicating project logic.
    result = process_text(args.text)
    print(result.output_text)


if __name__ == "__main__":
    main()
