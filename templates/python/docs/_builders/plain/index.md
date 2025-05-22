# {{ (project_name or project_slug) }}

{{ project_short_description }}

These Markdown pages can be read without a build tool.

## Contents

- [Project overview](overview.md)
{% if "user" in documentation_types.entries %}
- [Usage](usage.md)
{% endif %}
{% if "deployment" in documentation_types.entries %}
- [Deployment notes](deployment.md)
{% endif %}
{% if "developer" in documentation_types.entries %}
- [Developer guide](developer.md)
- [Technical reference](reference.md)
{% endif %}
- [Access and publish the documentation](documentation.md)
- [Legal and licensing](legal.md)
