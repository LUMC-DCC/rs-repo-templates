{% set interface_types = namespace(values=[]) %}
{% for interface in interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set has_processing_api = "Web API" in interface_types.values %}
{% set has_soap = "Web service" in interface_types.values %}
{% set has_api_app = has_processing_api or "SPARQL endpoint" in interface_types.values %}
{% set has_portal = "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values %}
{% set has_web = "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set http_adapter_count = (1 if has_api_app else 0) + (1 if has_soap else 0) + (1 if has_portal else 0) + (1 if has_web else 0) %}
{% set has_openapi_interface = has_api_app or has_portal or has_web %}
{% set configuration_security_measures = ["Secrets management (e.g., environment variables, vault)", "Secure configuration management (e.g., Infrastructure-as-Code, hardening)"] %}
{% set has_runtime_configuration = http_adapter_count or security_measures.selected.entries | select("in", configuration_security_measures) | list | length > 0 %}
# Usage

## Installation

Install the package from source during development:

```bash
@@PROJECT_SETUP_ALL@@
```

{% if has_api_app %}
Install API dependencies before running the API application:

```bash
@@PROJECT_SETUP_API@@
```

{% endif %}
{% if has_web or has_portal %}
Install web dependencies before running browser-facing applications:

```bash
@@PROJECT_SETUP_WEB@@
```

{% endif %}
{% if has_soap %}
Install SOAP dependencies before running the web service:

```bash
@@PROJECT_SETUP_SOAP@@
```

{% endif %}
## Run

The package-level smoke command is:

```bash
@@PROJECT_RUN@@python -m {{ project_slug }}
```

{% if has_runtime_configuration %}
## Configuration

For local development, copy `.env.example` to `.env` and change the values that
apply to your environment. `{{ project_slug }}.config.Settings`
validates the project-specific environment variables when the application
loads them. Do not commit `.env` or secret values.
{% if http_adapter_count %}

HTTP projects use the generated `*-serve` command. Its host, port, proxy root
path, and reload mode come from `.env`. Set
`{{ project_slug | upper }}_SERVER_RELOAD=true` for local
auto-reloading.
{% if has_openapi_interface %}
API, web, and portal applications can also use `PUBLIC_BASE_URL` to publish the
externally visible URL in OpenAPI metadata.
{% endif %}
{% endif %}

{% endif %}

{% if "Library" in interface_types.values %}
Use the public Python API from another Python module:

```python
from {{ project_slug }} import process_text

result = process_text("example input")
print(result.output_text)
```

{% endif %}
{% if "Command-line tool" in interface_types.values %}
Run the command-line interface:

```bash
{{ project_slug | replace('_', '-') }} process "example input"
```

{% endif %}
{% if "Script" in interface_types.values %}
Run the standalone script:

```bash
python scripts/run_example.py "example input"
```

{% endif %}
{% if http_adapter_count %}
Run all selected HTTP interfaces through the deployable application:

```bash
@@PROJECT_RUN@@{{ project_slug | replace('_', '-') }}-serve
```

{% endif %}
{% if has_processing_api %}
Send a processing request:

```bash
curl -X POST http://127.0.0.1:8000{% if http_adapter_count > 1 %}/api{% endif %}/process \
  -H "Content-Type: application/json" \
  -d '{"text": "example input"}'
```

{% endif %}
{% if has_soap %}
The WSDL contract is available at
`http://127.0.0.1:8000{% if http_adapter_count > 1 %}/soap/{% else %}/{% endif %}?wsdl`.
SOAP clients use that document to discover the generated `process` operation.

{% endif %}
{% if "SPARQL endpoint" in interface_types.values %}
Query the starter RDF graph:

```bash
curl "http://127.0.0.1:8000{% if http_adapter_count > 1 %}/api{% endif %}/sparql?query=SELECT%20?s%20?p%20?o%20WHERE%20%7B%20?s%20?p%20?o%20%7D%20LIMIT%2025"
```

{% endif %}
{% if has_web %}
Open `http://127.0.0.1:8000/` in a browser.

{% endif %}
{% if has_portal %}
Open `http://127.0.0.1:8000{% if http_adapter_count > 1 %}/portal{% endif %}/` in a browser, or fetch records from
`http://127.0.0.1:8000{% if http_adapter_count > 1 %}/portal{% endif %}/records`.

{% endif %}
{% if "Desktop application" in interface_types.values %}
Run the desktop application:

```bash
@@PROJECT_RUN@@{{ project_slug | replace('_', '-') }}-desktop
```

{% endif %}
{% if "Plug-in" in interface_types.values %}
Inspect the package-provided plug-in entry point:

```python
from importlib.metadata import entry_points

plugins = entry_points(group="{{ project_slug }}.plugins")
print([plugin.name for plugin in plugins])
```

{% endif %}
{% if "Suite" in interface_types.values %}
Run a suite command from Python:

```python
from {{ project_slug }}.adapters.suite.runner import run_suite_command

print(run_suite_command("process", "example input"))
```

{% endif %}
{% if "Ontology" in interface_types.values %}
Render the starter ontology document:

```python
from {{ project_slug }}.ontology.metadata import ontology_document

print(ontology_document())
```

{% endif %}
{% if "Workflow" in interface_types.values %}
Run the Python workflow:

```python
from {{ project_slug }}.workflows.pipeline import run_workflow

result = run_workflow("example input")
print(result.output_text)
```

{% endif %}
