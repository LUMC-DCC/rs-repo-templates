# {{ (project_name or project_slug) }}

{{ project_short_description }}

The package website is built with pkgdown. Narrative project documentation is
kept in this directory; the generated site contains the package reference,
README, changelog, and links from `DESCRIPTION`.

## Contents

- [Project overview](overview.md)
{% if "user" in documentation_types.entries %}- [Usage](usage.md)
{% endif %}{% if "deployment" in documentation_types.entries %}- [Deployment notes](deployment.md)
{% endif %}{% if "developer" in documentation_types.entries %}- [Developer guide](developer.md)
- [Technical reference](reference.md)
{% endif %}- [Build the package website](documentation.md)
- [Legal and licensing](legal.md)
