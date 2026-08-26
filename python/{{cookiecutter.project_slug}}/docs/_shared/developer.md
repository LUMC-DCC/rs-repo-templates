{% set interface_types = namespace(values=[]) %}
{% for interface in cookiecutter.interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set has_processing_api = "Web API" in interface_types.values %}
{% set has_soap = "Web service" in interface_types.values %}
{% set has_portal = "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values %}
{% set has_web = "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set has_adapter = has_processing_api or has_soap or "SPARQL endpoint" in interface_types.values or "Command-line tool" in interface_types.values or has_web or has_portal or "Desktop application" in interface_types.values or "Plug-in" in interface_types.values or "Suite" in interface_types.values %}
{% set effective_formatter_tool = cookiecutter.quality_tools.formatter if cookiecutter.quality_tools.formatter in cookiecutter._template_supported_choices.quality_tools.formatter else "" %}
{% set effective_linter_tool = cookiecutter.quality_tools.linter if cookiecutter.quality_tools.linter in cookiecutter._template_supported_choices.quality_tools.linter else "" %}
{% set effective_type_checker = cookiecutter.quality_tools.type_checker if cookiecutter.quality_tools.type_checker in cookiecutter._template_supported_choices.quality_tools.type_checker else "" %}
{% set has_quality_checks = effective_formatter_tool or effective_linter_tool or effective_type_checker %}
{% set effective_documentation_builder = cookiecutter.documentation_builder if cookiecutter.documentation_builder and cookiecutter.documentation_builder in cookiecutter._template_supported_choices.documentation_builder else "plain" %}
{% set has_docs_workflow = cookiecutter.documentation_types.entries and effective_documentation_builder in ["mkdocs", "sphinx"] %}
{% set has_license_workflow = cookiecutter.licensing.compatibility_check == "Yes - automated tooling" and cookiecutter.licensing.license | trim %}
{% set has_security_workflow = "Vulnerability scanning (e.g., Snyk, Dependabot)" in cookiecutter.security_measures.selected.entries %}
{% set container_types = namespace(values=[]) %}
{% for container in cookiecutter.containerization.entries %}
{% if container.type is defined %}
{% set _ = container_types.values.append(container.type) %}
{% endif %}
{% endfor %}
{% set has_container_workflow = "Docker" in container_types.values or "OCI / Podman" in container_types.values or "Apptainer / Singularity" in container_types.values %}
{% set distribution_channels = namespace(values=[]) %}
{% for channel in cookiecutter.distribution_channels.entries %}
{% set _ = distribution_channels.values.append(channel | lower) %}
{% endfor %}
{% set has_distribution_workflow = "pypi" in distribution_channels.values or "github releases" in distribution_channels.values or "github release" in distribution_channels.values or "conda-forge" in distribution_channels.values %}
{% set has_http_interface = "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values or "Web service" in interface_types.values or "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values or "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set configuration_security_measures = ["Secrets management (e.g., environment variables, vault)", "Secure configuration management (e.g., Infrastructure-as-Code, hardening)"] %}
{% set has_runtime_configuration = has_http_interface or cookiecutter.security_measures.selected.entries | select("in", configuration_security_measures) | list | length > 0 %}
# Developer guide

## Architecture

{{ (cookiecutter.project_name or cookiecutter.project_slug) }} uses a small layered Python package.

Core project logic lives in `src/{{ cookiecutter.project_slug }}/services/`.
{% if has_adapter %}
Code that translates a public interface into service calls lives under
`src/{{ cookiecutter.project_slug }}/adapters/`. Keep those adapter modules thin:
they should parse input, call services, and format output.

{% endif %}
Reusable library functions should be exported from
`src/{{ cookiecutter.project_slug }}/__init__.py` when they are part of the
public Python API. Keep package `__init__.py` files as package boundaries and
put implementation in named modules such as `services/processing.py`.
{% if has_adapter or "Ontology" in interface_types.values or "Workflow" in interface_types.values %}
Interface-specific implementations use names such as `app.py`, `commands/`,
`views.py`, `repository.py`, `registry.py`, `metadata.py`, or `pipeline.py`.
{% endif %}

| Layer | Purpose |
| --- | --- |
| `services/` | Project behavior that is independent of a specific interface. |
{% if has_adapter %}
| `adapters/` | Interface-specific translation at the project boundary. |
{% endif %}
{% if "Script" in interface_types.values %}
| `scripts/` | Standalone script entry points. |
{% endif %}
{% if "Workflow" in interface_types.values %}
| `src/{{ cookiecutter.project_slug }}/workflows/` | Importable Python workflow orchestration. |
| `workflows/` | Engine-specific workflow definitions, examples, and workflow test inputs. |
{% endif %}
{% if "Ontology" in interface_types.values or "SPARQL endpoint" in interface_types.values %}
| `ontology/` | RDF graph construction, ontology metadata, validation, and serialization. |
{% endif %}

{% if interface_types.values %}
## Generated interface modules

| Interface type | Main modules |
| --- | --- |
{% if "Library" in interface_types.values %}
| Library | `__init__.py`, `services/processing.py` |
{% endif %}
{% if "Command-line tool" in interface_types.values %}
| Command-line tool | `adapters/cli/app.py`, `adapters/cli/commands/` |
{% endif %}
{% if "Script" in interface_types.values %}
| Script | `scripts/run_example.py` |
{% endif %}
{% if has_processing_api %}
| Web API | `adapters/api/app.py`, `adapters/api/routes/`, `adapters/api/schemas.py` |
{% endif %}
{% if has_soap %}
| Web service | `adapters/soap/app.py`, `adapters/soap/service.py` |
{% endif %}
{% if "SPARQL endpoint" in interface_types.values %}
| SPARQL endpoint | `adapters/api/routes/sparql.py`, `ontology/graph.py` |
{% endif %}
{% if has_web %}
| Web application or workbench | `adapters/web/app.py`, `adapters/web/routes/`, `adapters/web/views.py` |
{% endif %}
{% if has_portal %}
| Bioinformatics or database portal | `adapters/portal/app.py`, routes, models, repository, summary, and views |
{% endif %}
{% if "Desktop application" in interface_types.values %}
| Desktop application | `adapters/desktop/app.py`, `adapters/desktop/view_model.py` |
{% endif %}
{% if "Plug-in" in interface_types.values %}
| Plug-in | `adapters/plugin/hooks.py`, `adapters/plugin/registry.py` |
{% endif %}
{% if "Suite" in interface_types.values %}
| Suite | `adapters/suite/commands.py`, `adapters/suite/runner.py` |
{% endif %}
{% if "Ontology" in interface_types.values %}
| Ontology | `ontology/namespaces.py`, `terms.py`, `graph.py`, `serializers.py`, `validation.py`, `metadata.py` |
{% endif %}
{% if "Workflow" in interface_types.values %}
| Workflow | `workflows/config.py`, `io.py`, `steps.py`, `pipeline.py`, plus top-level `workflows/` |
{% endif %}

{% endif %}
## Development notes

{% if "Library" in interface_types.values %}
### Library

The package root exposes the public Python API. Keep long-running logic and
domain behavior in `services/`, then export only stable names from
`src/{{ cookiecutter.project_slug }}/__init__.py`.

{% endif %}
{% if "Command-line tool" in interface_types.values %}
### Command-line tool

The CLI uses Typer. Register new commands in `adapters/cli/app.py` and put each
command implementation in `adapters/cli/commands/`. Keep command functions
small: validate command-line input, call a service, and print the result.

{% endif %}
{% if "Script" in interface_types.values %}
### Script

The script in `scripts/` is a thin executable wrapper. Keep script-specific
argument parsing there, and put reusable behavior in package modules under
`src/{{ cookiecutter.project_slug }}/`.

{% endif %}
{% if has_processing_api %}
### Web API

The API uses FastAPI with explicit route modules. `adapters/api/app.py` creates
the application and registers routers. Route modules own URL paths and HTTP
payload mapping. Pydantic schemas in `adapters/api/schemas.py` define request
and response contracts.

{% endif %}
{% if has_soap %}
### Web service

The web-service adapter uses Spyne to declare SOAP 1.1 operations and generate
a WSDL contract. `adapters/soap/service.py` declares operations and types;
`adapters/soap/app.py` exposes both the native WSGI app and an ASGI wrapper.

{% endif %}
{% if (has_processing_api or "SPARQL endpoint" in interface_types.values) and (has_soap or has_web or has_portal) or has_soap and (has_web or has_portal) or has_web and has_portal %}
### HTTP composition

`adapters/server.py` mounts selected HTTP adapters under stable paths so REST,
SOAP, portal, and browser routes can run in one process without collisions.

{% endif %}
{% if "SPARQL endpoint" in interface_types.values %}
### SPARQL endpoint

The SPARQL route evaluates read-only queries against an RDFLib graph built by
`ontology/graph.py`. For larger datasets, replace the per-request starter graph
with a configured RDF store while keeping the route response shape stable.

{% endif %}
{% if has_web %}
### Web application and workbench

The web application uses FastAPI route modules and view helpers. Routes own URL
paths and response classes. View helpers prepare HTML output and escape dynamic
content before rendering.

{% endif %}
{% if has_portal %}
### Portal

The portal separates record models, data access, summaries, routes, and views.
`repository.py` is the data boundary. Replace the in-memory repository with a
database, file-backed store, or external service when the portal data source is
known.

{% endif %}
{% if "Desktop application" in interface_types.values %}
### Desktop application

The desktop app uses the Python standard-library Tkinter toolkit. GUI widget
construction lives in `adapters/desktop/app.py`; display-ready data lives in
`adapters/desktop/view_model.py` so behavior can be tested without opening a
window.

{% endif %}
{% if "Plug-in" in interface_types.values %}
### Plug-in

Plug-in contracts live in `adapters/plugin/hooks.py`. The package-provided
plug-in is exposed through Python entry point metadata and returned from
`adapters/plugin/registry.py`.

{% endif %}
{% if "Suite" in interface_types.values %}
### Suite

The suite adapter groups related commands behind a small registry. Add suite
commands in `adapters/suite/commands.py` and keep lookup and error handling in
`adapters/suite/runner.py`.

{% endif %}
{% if "Ontology" in interface_types.values %}
### Ontology

Ontology terms are plain Python data objects. `ontology/graph.py` converts those
terms into an RDFLib graph; `ontology/serializers.py` handles RDF
serialization. Keep validation rules in `ontology/validation.py`.

{% endif %}
{% if "Workflow" in interface_types.values %}
### Workflow

Python workflow orchestration lives in `src/{{ cookiecutter.project_slug }}/workflows/`.
Keep configuration, IO, steps, and pipeline coordination in separate modules.
Use the top-level `workflows/` directory for engine-specific workflow
definitions such as CWL or Snakemake files.

{% endif %}
{% if has_runtime_configuration %}
## Runtime configuration

The package-level `config.py` is the typed boundary for values that differ
between deployments. Add settings to `Settings`, add non-secret examples to
`.env.example`, and read configuration through `get_settings()` rather than
calling `os.environ` throughout the codebase. Secret values belong in local or
deployment environment configuration and must not be committed.

Application entry points call `logging_config.configure_logging()`. Package
modules create named loggers with `logging.getLogger(__name__)` and do not add
their own handlers. HTTP app factories accept a `Settings` instance for tests;
the generated server runner consumes bind, proxy, reload, and logging settings.

{% endif %}
{% if cookiecutter.test_types.entries %}
## Tests

This project includes pytest tests selected from the requested test types.
Starter tests cover the package entry point, reusable service logic, selected
interface adapters, and stable processing behavior where those test types were
included.

{% endif %}
## Local checks

Set up the complete development environment with `@@PROJECT_MANAGER@@`:

```bash
@@PROJECT_SETUP_ALL@@
```

@@PROJECT_LOCK_GUIDANCE@@

Run the applicable checks through the managed environment:

```bash
{% if "CHANGELOG.md" in cookiecutter.community_files.entries %}
@@PROJECT_RUN@@python tools/check_changelog.py
{% endif %}
{% if effective_linter_tool == "ruff" %}
@@PROJECT_RUN@@ruff check .
{% endif %}
{% if effective_formatter_tool == "ruff" %}
@@PROJECT_RUN@@ruff format --check .
{% endif %}
{% if effective_type_checker == "mypy" %}
@@PROJECT_RUN@@mypy src
{% endif %}
{% if has_quality_checks %}
@@PROJECT_RUN@@pre-commit run --all-files
{% endif %}
{% if cookiecutter.test_types.entries %}
@@PROJECT_RUN@@python -m pytest
{% endif %}
```

## Continuous integration

The generated workflows mirror the selected project capabilities:

| Workflow | Responsibility |
| --- | --- |
{% if cookiecutter.include_metadata %}
| `metadata.yml` | Validate `codemeta.json` and `CITATION.cff` with the LUMC `rs-metadata` profile. |
{% endif %}
{% if cookiecutter.test_types.entries %}
| `tests.yml` | Run the selected pytest suite on officially supported operating systems. |
{% endif %}
{% if has_quality_checks %}
| `quality.yml` | Run the selected formatter, linter, and type checker. |
{% endif %}
{% if has_docs_workflow %}
| `docs.yml` | Build the configured documentation with warnings treated as failures. |
{% endif %}
{% if "CHANGELOG.md" in cookiecutter.community_files.entries %}
| `changelog.yml` | Validate the Keep a Changelog structure. |
{% endif %}
{% if has_license_workflow %}
| `license-compatibility.yml` | Check dependency licenses against the project license. |
{% endif %}
{% if has_security_workflow %}
| `security.yml` | Review changed dependencies and run CodeQL analysis. |
{% endif %}
{% if has_container_workflow %}
| `containers.yml` | Build selected container recipes and publish selected registry images on tags. |
{% endif %}
{% if has_distribution_workflow %}
| `distribution.yml` | Validate releases, build distributions, and publish selected tagged releases. |
{% endif %}

Dependabot checks GitHub Actions and Python dependencies weekly and proposes
updates through pull requests.
