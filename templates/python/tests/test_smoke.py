"""Smoke tests for the generated Python package."""

{% set interface_types = namespace(values=[]) %}
{% for interface in interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set needs_optional_imports = "Command-line tool" in interface_types.values or "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values or "Web service" in interface_types.values or "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values or "Web application" in interface_types.values or "Workbench" in interface_types.values or "Ontology" in interface_types.values %}
{% set has_http_interface = "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values or "Web service" in interface_types.values or "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values or "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set configuration_security_measures = ["Secrets management (e.g., environment variables, vault)", "Secure configuration management (e.g., Infrastructure-as-Code, hardening)"] %}
{% set has_runtime_configuration = has_http_interface or security_measures.selected.entries | select("in", configuration_security_measures) | list | length > 0 %}
{% if needs_optional_imports %}
import pytest

{% endif %}
from {{ project_slug }} import __version__, process_text
from {{ project_slug }}.main import main


def test_package_has_version():
    """Ensure the package exposes the generated version."""
    assert __version__ == "{{ (versioning.version or "0.1.0") }}"


def test_main_is_callable():
    """Ensure the runtime entry point can be imported."""
    assert callable(main)


def test_library_api_processes_text():
    """Ensure reusable service logic is available from the package API."""
    result = process_text("example")

    assert result.input_text == "example"
    assert result.output_text == "EXAMPLE"
{% if has_runtime_configuration %}


def test_runtime_settings_import():
    """Ensure the selected runtime settings boundary imports."""
    from {{ project_slug }}.config import Settings

    assert Settings(_env_file=None).log_level == "INFO"
{% endif %}
{% if has_http_interface %}


def test_http_server_runner_imports():
    """Ensure the configured HTTP server entry point imports."""
    pytest.importorskip("uvicorn")
    from {{ project_slug }}.adapters.server_runner import main

    assert callable(main)
{% endif %}
{% if "Command-line tool" in interface_types.values %}


def test_cli_entry_point_imports():
    """Ensure the selected command-line application imports."""
    pytest.importorskip("typer")
    from {{ project_slug }}.adapters.cli.app import app

    assert callable(app)
{% endif %}
{% if "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values %}


def test_api_entry_point_imports():
    """Ensure the selected API application factory imports."""
    pytest.importorskip("fastapi")
    from {{ project_slug }}.adapters.api.app import create_app

    assert callable(create_app)
{% endif %}
{% if "Web service" in interface_types.values %}


def test_soap_entry_point_imports():
    """Ensure the selected SOAP application imports."""
    pytest.importorskip("spyne")
    pytest.importorskip("a2wsgi")
    from {{ project_slug }}.adapters.soap.app import app

    assert callable(app)
{% endif %}
{% if "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values %}


def test_portal_entry_point_imports():
    """Ensure the selected portal application factory imports."""
    pytest.importorskip("fastapi")
    from {{ project_slug }}.adapters.portal.app import create_portal_app

    assert callable(create_portal_app)
{% endif %}
{% if "Web application" in interface_types.values or "Workbench" in interface_types.values %}


def test_web_entry_point_imports():
    """Ensure the selected web application factory imports."""
    pytest.importorskip("fastapi")
    from {{ project_slug }}.adapters.web.app import create_web_app

    assert callable(create_web_app)
{% endif %}
{% if "Desktop application" in interface_types.values %}


def test_desktop_entry_point_imports_without_opening_a_window():
    """Ensure the selected desktop view model imports without a display."""
    from {{ project_slug }}.adapters.desktop.view_model import (
        build_view_model,
    )

    assert callable(build_view_model)
{% endif %}
{% if "Plug-in" in interface_types.values %}


def test_plugin_entry_point_imports():
    """Ensure the selected plug-in registry imports."""
    from {{ project_slug }}.adapters.plugin.registry import get_plugin

    assert callable(get_plugin)
{% endif %}
{% if "Suite" in interface_types.values %}


def test_suite_entry_point_imports():
    """Ensure the selected suite runner imports."""
    from {{ project_slug }}.adapters.suite.runner import run_suite_command

    assert callable(run_suite_command)
{% endif %}
{% if "Ontology" in interface_types.values %}


def test_ontology_entry_point_imports():
    """Ensure the selected ontology document helper imports."""
    pytest.importorskip("rdflib")
    from {{ project_slug }}.ontology.metadata import ontology_document

    assert callable(ontology_document)
{% endif %}
{% if "Workflow" in interface_types.values %}


def test_workflow_entry_point_imports():
    """Ensure the selected workflow pipeline imports."""
    from {{ project_slug }}.workflows.pipeline import run_workflow

    assert callable(run_workflow)
{% endif %}
