"""Integration tests for generated interface adapters."""

{% set interface_types = namespace(values=[]) %}
{% for interface in interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set has_cli = "Command-line tool" in interface_types.values %}
{% set has_api = "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values %}
{% set has_soap = "Web service" in interface_types.values %}
{% set has_script = "Script" in interface_types.values %}
{% set has_desktop = "Desktop application" in interface_types.values %}
{% set has_plugin = "Plug-in" in interface_types.values %}
{% set has_portal = "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values %}
{% set has_suite = "Suite" in interface_types.values %}
{% set has_web = "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set has_ontology = "Ontology" in interface_types.values or "SPARQL endpoint" in interface_types.values %}
{% set has_workflow = "Workflow" in interface_types.values %}
{% set http_adapter_count = (1 if has_api else 0) + (1 if has_soap else 0) + (1 if has_portal else 0) + (1 if has_web else 0) %}
{% if has_script %}
import importlib.util
from pathlib import Path

{% endif %}
{% if has_soap %}
from wsgiref.util import setup_testing_defaults

{% endif %}
import pytest

from {{ project_slug }}.services.processing import process_text


def test_service_integration_path_processes_text():
    """Ensure the reusable service path behaves consistently."""
    assert process_text("abc").output_text == "ABC"


{% if has_cli %}
def test_cli_application_processes_a_command():
    """Ensure the installed CLI surface reaches the service layer."""
    pytest.importorskip("typer")
    from typer.testing import CliRunner

    from {{ project_slug }}.adapters.cli.app import app

    result = CliRunner().invoke(app, ["process", "abc"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "ABC"


{% endif %}
{% if has_api %}
def test_api_application_serves_selected_routes():
    """Ensure API requests traverse routing, schemas, and services."""
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient

    from {{ project_slug }}.adapters.api.app import create_app

    client = TestClient(create_app())
    assert client.get("/health").json() == {"status": "ok"}
{% if "Web API" in interface_types.values %}
    response = client.post("/process", json={"text": "abc"})
    assert response.status_code == 200
    assert response.json()["output_text"] == "ABC"
{% endif %}
{% if "SPARQL endpoint" in interface_types.values %}
    response = client.get("/sparql")
    assert response.status_code == 200
    assert "results" in response.json()
{% endif %}


{% endif %}
{% if has_portal %}
def test_portal_application_serves_pages_and_records():
    """Ensure the portal composes views and structured records."""
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient

    from {{ project_slug }}.adapters.portal.app import create_portal_app

    client = TestClient(create_portal_app())

    assert client.get("/").status_code == 200
    records = client.get("/records")
    assert records.status_code == 200
    assert isinstance(records.json(), list)


{% endif %}
{% if has_web %}
def test_web_application_serves_a_browser_page():
    """Ensure the web adapter renders its human-facing route."""
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient

    from {{ project_slug }}.adapters.web.app import create_web_app

    response = TestClient(create_web_app()).get("/")

    assert response.status_code == 200
    assert "{{ (project_name or project_slug) }}" in response.text


{% endif %}
{% if http_adapter_count > 1 %}
def test_combined_server_mounts_selected_http_interfaces():
    """Ensure selected HTTP adapters coexist in one ASGI application."""
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient

    from {{ project_slug }}.adapters.server import app

    client = TestClient(app)
{% if has_api %}
    assert client.get("/api/health").status_code == 200
{% endif %}
{% if has_portal %}
    assert client.get("/portal/records").status_code == 200
{% endif %}
{% if has_web %}
    assert client.get("/").status_code == 200
{% endif %}


{% endif %}
{% if has_soap %}
def test_soap_application_publishes_wsdl():
    """Ensure the SOAP service exposes a usable WSDL contract."""
    pytest.importorskip("spyne")
    pytest.importorskip("a2wsgi")

    from {{ project_slug }}.adapters.soap.app import app, wsgi_app

    assert callable(app)

    environ = {}
    setup_testing_defaults(environ)
    environ.update(
        {
            "REQUEST_METHOD": "GET",
            "PATH_INFO": "/",
            "QUERY_STRING": "wsdl",
        }
    )
    response = {}

    def start_response(status, headers, exc_info=None):
        """Capture the WSGI status and headers for assertions."""
        response["status"] = status
        response["headers"] = headers

    body = b"".join(wsgi_app(environ, start_response))

    assert response["status"] == "200 OK"
    assert b"<wsdl:definitions" in body
    assert b'operation name="process"' in body


{% endif %}
{% if has_desktop %}
def test_desktop_view_model_processes_without_opening_a_window():
    """Ensure desktop behavior is testable without a display server."""
    from {{ project_slug }}.adapters.desktop.view_model import (
        build_view_model,
    )

    view_model = build_view_model("abc")

    assert view_model.message == "ABC"


{% endif %}
{% if has_plugin %}
def test_plugin_registry_returns_a_working_plugin():
    """Ensure the registered plug-in delegates to project services."""
    from {{ project_slug }}.adapters.plugin.registry import get_plugin

    plugin = get_plugin()

    assert plugin.process("abc") == "ABC"


{% endif %}
{% if has_suite %}
def test_suite_runner_dispatches_a_registered_command():
    """Ensure suite commands are discoverable and executable."""
    from {{ project_slug }}.adapters.suite.runner import (
        run_suite_command,
        suite_commands,
    )

    assert "process" in suite_commands()
    assert run_suite_command("process", "abc") == "ABC"


{% endif %}
{% if has_ontology %}
def test_ontology_document_is_valid_turtle():
    """Ensure the starter ontology can be serialized and parsed."""
    rdflib = pytest.importorskip("rdflib")

    from {{ project_slug }}.ontology.metadata import ontology_document

    graph = rdflib.Graph().parse(data=ontology_document(), format="turtle")

    assert len(graph) > 0


{% endif %}
{% if has_workflow %}
def test_workflow_pipeline_coordinates_selected_steps():
    """Ensure the workflow entry point returns a structured result."""
    from {{ project_slug }}.workflows.pipeline import run_workflow

    result = run_workflow("abc")

    assert result.input_text == "abc"
    assert result.output_text == "ABC"


{% endif %}
{% if has_script %}
def test_example_script_can_run_without_cli_process():
    """Ensure the generated script delegates to package code."""
    script_path = Path(__file__).parents[1] / "scripts" / "run_example.py"
    spec = importlib.util.spec_from_file_location("run_example", script_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.process_text("abc").output_text == "ABC"
{% endif %}
