# {{ (cookiecutter.project_name or cookiecutter.project_slug) }}

{{ cookiecutter.project_short_description }}

## Contents

- [Project overview](overview.md)
{% if "user" in cookiecutter.documentation_types.entries %}
- [Usage](usage.md)
{% endif %}
{% if "deployment" in cookiecutter.documentation_types.entries %}
- [Deployment notes](deployment.md)
{% endif %}
{% if "developer" in cookiecutter.documentation_types.entries %}
- [Developer guide](developer.md)
- [Technical reference](reference.md)
{% endif %}
- [Build and view the documentation](documentation.md)
- [Legal and licensing](legal.md)
