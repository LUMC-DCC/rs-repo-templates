# {{ (cookiecutter.project_name or cookiecutter.project_slug) }}

{{ cookiecutter.project_short_description }}

{% if cookiecutter.urls.homepage and cookiecutter.urls.homepage != cookiecutter.urls.repository %}
Homepage: {{ cookiecutter.urls.homepage }}
{% endif %}
{% if cookiecutter.urls.documentation and cookiecutter.urls.documentation != cookiecutter.urls.repository and cookiecutter.urls.documentation != cookiecutter.urls.homepage %}
Documentation: {{ cookiecutter.urls.documentation }}
{% endif %}
{% set effective_formatter_tool = cookiecutter.quality_tools.formatter if cookiecutter.quality_tools.formatter in cookiecutter._template_supported_choices.quality_tools.formatter else "" %}
{% set effective_linter_tool = cookiecutter.quality_tools.linter if cookiecutter.quality_tools.linter in cookiecutter._template_supported_choices.quality_tools.linter else "" %}
{% set effective_type_checker = cookiecutter.quality_tools.type_checker if cookiecutter.quality_tools.type_checker in cookiecutter._template_supported_choices.quality_tools.type_checker else "" %}
{% set has_quality_checks = effective_formatter_tool or effective_linter_tool or effective_type_checker %}
{% set has_tests = cookiecutter.test_types.entries | length > 0 %}
{% set has_local_checks = "CHANGELOG.md" in cookiecutter.community_files.entries or has_quality_checks or has_tests %}
{% set interface_types = namespace(values=[]) %}
{% for interface in cookiecutter.interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set has_api = "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values %}
{% set has_soap = "Web service" in interface_types.values %}
{% set has_portal = "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values %}
{% set has_web = "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set has_http = has_api or has_soap or has_portal or has_web %}
{% set configuration_security_measures = ["Secrets management (e.g., environment variables, vault)", "Secure configuration management (e.g., Infrastructure-as-Code, hardening)"] %}
{% set has_runtime_configuration = has_http or cookiecutter.security_measures.selected.entries | select("in", configuration_security_measures) | list | length > 0 %}

## Installation

Set up the project and its generated development tools from the repository root:

```bash
@@PROJECT_SETUP_ALL@@
```

## Usage

{% if interface_types.values %}
The selected interfaces provide these starting points:

| Interface | Start here |
| --- | --- |
{% if "Library" in interface_types.values %}
| Python library | Import `process_text` from `{{ cookiecutter.project_slug }}`. |
{% endif %}
{% if "Command-line tool" in interface_types.values %}
| Command line | `{{ cookiecutter.project_slug | replace('_', '-') }} process "example input"` |
{% endif %}
{% if "Script" in interface_types.values %}
| Script | `@@PROJECT_RUN@@python scripts/run_example.py "example input"` |
{% endif %}
{% if has_http %}
| HTTP interfaces | `@@PROJECT_RUN@@{{ cookiecutter.project_slug | replace('_', '-') }}-serve` |
{% endif %}
{% if "Desktop application" in interface_types.values %}
| Desktop application | `@@PROJECT_RUN@@{{ cookiecutter.project_slug | replace('_', '-') }}-desktop` |
{% endif %}
{% if "Plug-in" in interface_types.values %}
| Plug-in | Load entry points from `{{ cookiecutter.project_slug }}.plugins`. |
{% endif %}
{% if "Suite" in interface_types.values %}
| Suite | Call `adapters.suite.runner.run_suite_command`. |
{% endif %}
{% if "Ontology" in interface_types.values %}
| Ontology | Call `ontology.metadata.ontology_document`. |
{% endif %}
{% if "Workflow" in interface_types.values %}
| Workflow | Call `workflows.pipeline.run_workflow`. |
{% endif %}

{% if cookiecutter.documentation_types.entries %}
The generated user documentation contains installation details and complete
examples for each selected interface.
{% endif %}
{% else %}
Run the package smoke entry point inside the managed environment:

```bash
@@PROJECT_RUN@@python -m {{ cookiecutter.project_slug }}
```
{% endif %}

{% if has_runtime_configuration %}
### Configuration

Copy `.env.example` to `.env` for local values. Runtime settings are validated
by `{{ cookiecutter.project_slug }}.config.Settings`; keep secrets out of version
control. HTTP projects read their bind host, port, proxy root path, and reload
mode from these settings. API, web, and portal applications can also publish an
optional public base URL.

{% endif %}

{% if has_local_checks or cookiecutter.include_metadata %}
## Development

{% if has_local_checks %}
Run the checks that are configured for this project before opening a pull request:

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
{% if has_tests %}
@@PROJECT_RUN@@python -m pytest
{% endif %}
```
{% endif %}

{% if cookiecutter.include_metadata %}
Continuous integration also validates the project metadata.
{% endif %}
{% endif %}
