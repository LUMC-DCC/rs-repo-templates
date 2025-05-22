"""Unit tests for reusable processing behavior."""

{% set interface_types = namespace(values=[]) %}
{% for interface in interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set has_http_interface = "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values or "Web service" in interface_types.values or "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values or "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set has_openapi_interface = "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values or "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values or "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set configuration_security_measures = ["Secrets management (e.g., environment variables, vault)", "Secure configuration management (e.g., Infrastructure-as-Code, hardening)"] %}
{% set has_runtime_configuration = has_http_interface or security_measures.selected.entries | select("in", configuration_security_measures) | list | length > 0 %}
{% if has_runtime_configuration %}
import logging

{% endif %}
{% if has_runtime_configuration %}
from {{ project_slug }}.config import Settings
from {{ project_slug }}.logging_config import configure_logging
{% endif %}
from {{ project_slug }}.services.processing import make_upper, process_text


def test_process_text_returns_structured_result():
    """Ensure service processing preserves input and returns output."""
    result = process_text("abc")

    assert result.input_text == "abc"
    assert result.output_text == "ABC"


def test_make_upper_reuses_processing_service():
    """Ensure convenience helper follows service behavior."""
    assert make_upper("research") == "RESEARCH"
{% if has_runtime_configuration %}


def test_runtime_settings_read_project_environment(monkeypatch):
    """Ensure project-prefixed environment variables override defaults."""
    monkeypatch.setenv("{{ project_slug | upper }}_LOG_LEVEL", "DEBUG")

    settings = Settings(_env_file=None)

    assert settings.log_level == "DEBUG"


def test_logging_configuration_sets_package_level():
    """Ensure configured log levels apply to package module loggers."""
    settings = Settings(_env_file=None, log_level="DEBUG")

    package_logger = configure_logging(settings)

    assert package_logger.name == "{{ project_slug }}"
    assert (
        logging.getLogger(
            "{{ project_slug }}.services.processing"
        ).getEffectiveLevel()
        == logging.DEBUG
    )
{% endif %}
{% if has_http_interface %}


def test_http_server_settings_are_typed(monkeypatch):
    """Ensure HTTP bind and public URL settings are parsed and normalized."""
    monkeypatch.setenv("{{ project_slug | upper }}_SERVER_PORT", "9000")
    monkeypatch.setenv(
        "{{ project_slug | upper }}_SERVER_ROOT_PATH",
        "services/{{ project_slug }}/",
    )
{% if has_openapi_interface %}
    monkeypatch.setenv(
        "{{ project_slug | upper }}_PUBLIC_BASE_URL",
        "https://example.org/{{ project_slug }}/",
    )
{% endif %}

    settings = Settings(_env_file=None)

    assert settings.server_port == 9000
    assert settings.server_root_path == "/services/{{ project_slug }}"
{% if has_openapi_interface %}
    assert str(settings.public_base_url) == (
        "https://example.org/{{ project_slug }}/"
    )
{% endif %}
{% endif %}
