{% set interface_types = namespace(values=[]) %}
{% for interface in cookiecutter.interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set has_api_app = "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values %}
{% set has_soap = "Web service" in interface_types.values %}
{% set has_portal = "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values %}
{% set has_web = "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set has_http = has_api_app or has_soap or has_portal or has_web %}
{% set has_openapi_interface = has_api_app or has_portal or has_web %}
{% set configuration_security_measures = ["Secrets management (e.g., environment variables, vault)", "Secure configuration management (e.g., Infrastructure-as-Code, hardening)"] %}
{% set has_runtime_configuration = has_http or cookiecutter.security_measures.selected.entries | select("in", configuration_security_measures) | list | length > 0 %}
# Deployment notes

## Package installation

Build and install the package in a clean environment before deployment:

```bash
python -m pip install .
```

{% if has_runtime_configuration %}
## Runtime configuration

`{{ cookiecutter.project_slug }}.config.Settings` validates environment and
logging settings. Use `.env.example` as the local configuration inventory. In
deployed environments, provide the same project-prefixed variables through the
platform configuration or secrets manager rather than shipping a `.env` file.
For HTTP projects, `SERVER_HOST` and `SERVER_PORT` control socket binding,
and `SERVER_ROOT_PATH` supports path-based reverse proxies.
{% if has_openapi_interface %}
`PUBLIC_BASE_URL` publishes the externally visible URL in OpenAPI metadata.
{% endif %}

{% endif %}

{% if has_http %}
## HTTP service

Install the selected optional dependencies, then run the composed application
with an ASGI server:

```bash
@@PROJECT_SETUP_ALL@@
@@PROJECT_RUN@@{{ cookiecutter.project_slug | replace('_', '-') }}-serve
```

Configure the production process manager, host, port, logging, and HTTPS
termination in the target environment.

{% endif %}
{% if has_soap %}
The SOAP adapter publishes its WSDL beside the service. Preserve the external
mount path in reverse-proxy configuration so generated service locations stay
reachable by clients.

{% endif %}
{% if has_web %}
## Web application

Configure static assets, authentication, and reverse-proxy settings when the
application grows beyond the starter page.

{% endif %}
{% if has_portal %}
## Portal

Replace the starter in-memory repository with the production data source before
publishing a real portal.

{% endif %}
{% if "Desktop application" in interface_types.values %}
## Desktop application

Desktop deployment means installing the package in the user's local Python
environment or bundling it with a desktop packaging tool. The starter entry
point is:

```bash
python -m {{ cookiecutter.project_slug }}.adapters.desktop.app
```

{% endif %}
{% if "Plug-in" in interface_types.values %}
## Plug-in

Deploy plug-ins by installing the package into the environment of the host
application that discovers the `{{ cookiecutter.project_slug }}.plugins` entry
point group.

{% endif %}
{% if "Script" in interface_types.values %}
## Script

Run scripts from a versioned environment with the package installed. For
scheduled runs, capture standard output, standard error, input paths, and the
installed package version.

{% endif %}
{% if "Workflow" in interface_types.values %}
## Workflow

Keep Python workflow orchestration in the package and deploy engine-specific
definitions from the top-level `workflows/` directory. Validate workflow
definitions with the selected workflow engine before production use.

{% endif %}
{% if "Ontology" in interface_types.values or "SPARQL endpoint" in interface_types.values %}
## RDF and ontology data

The starter RDF graph is built in memory. For larger ontology data or SPARQL
traffic, configure a persistent RDF store and keep exported ontology documents
versioned with the software release.

{% endif %}
