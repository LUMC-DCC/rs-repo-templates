# {{ (project_name or project_slug) }}

{{ project_short_description }}

```{toctree}
:maxdepth: 2
:caption: Contents

overview
{% if "user" in documentation_types.entries %}
usage
{% endif %}
{% if "deployment" in documentation_types.entries %}
deployment
{% endif %}
{% if "developer" in documentation_types.entries %}
developer
reference
{% endif %}
documentation
legal
```
