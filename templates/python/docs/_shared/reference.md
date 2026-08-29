{% set effective_documentation_builder = documentation_builder if documentation_builder and documentation_builder in template_supported_choices.documentation_builder else "plain" %}
{% set interface_types = namespace(values=[]) %}
{% for interface in interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set reference_modules = [project_slug, project_slug ~ ".services.processing"] %}
{% if "Command-line tool" in interface_types.values %}
{% set _ = reference_modules.append(project_slug ~ ".adapters.cli.commands.process") %}
{% endif %}
{% if "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values %}
{% set _ = reference_modules.append(project_slug ~ ".adapters.api.app") %}
{% endif %}
{% if "Desktop application" in interface_types.values %}
{% set _ = reference_modules.append(project_slug ~ ".adapters.desktop.view_model") %}
{% endif %}
{% if "Plug-in" in interface_types.values %}
{% set _ = reference_modules.append(project_slug ~ ".adapters.plugin.registry") %}
{% endif %}
{% if "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values %}
{% set _ = reference_modules.append(project_slug ~ ".adapters.portal.app") %}
{% endif %}
{% if "Suite" in interface_types.values %}
{% set _ = reference_modules.append(project_slug ~ ".adapters.suite.runner") %}
{% endif %}
{% if "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set _ = reference_modules.append(project_slug ~ ".adapters.web.app") %}
{% endif %}
{% if "Ontology" in interface_types.values or "SPARQL endpoint" in interface_types.values %}
{% set _ = reference_modules.append(project_slug ~ ".ontology.metadata") %}
{% endif %}
{% if "Workflow" in interface_types.values %}
{% set _ = reference_modules.append(project_slug ~ ".workflows.pipeline") %}
{% endif %}
# Technical reference

This reference is generated from the public Python docstrings in the selected
package modules.

{% for module in reference_modules %}
## `{{ module }}`

{% if effective_documentation_builder in ["mkdocs", "zensical"] %}
::: {{ module }}
    options:
      docstring_style: numpy
      members_order: source
      show_root_heading: true
      show_source: true
{% elif effective_documentation_builder == "sphinx" %}
```{eval-rst}
.. automodule:: {{ module }}
   :members:
   :show-inheritance:
```
{% else %}
{% if module == project_slug %}
See the docstrings in `src/{{ project_slug }}/__init__.py`.
{% else %}
See the docstrings in `src/{{ module | replace(".", "/") }}.py`.
{% endif %}
{% endif %}

{% endfor %}
