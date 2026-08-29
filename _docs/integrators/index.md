# For service integrators

Integration services map their own data to the published
[RSM 1.0.0 schema](https://lumc-dcc.github.io/rsm-schema/schema/1.0.0/rsm.schema.json).
SMP, DSW, form, and API conversion stays in the integration service.

```text
service data
-> RSM metadata
-> RSM validation
-> Copier data + template_type
-> generated repository
```

## Generator environment

Install Copier, `rsm-schema`, and `rs-files-templates` in the same Python
environment. This repository's `pyproject.toml` pins the tested revisions until
the upstream packages are published on PyPI.

The template runs source-side finalization tasks, so Copier requires
`--trust` on the command line or `unsafe=True` through its Python API. Trust
only the reviewed LUMC-DCC template repository and pin a release tag in
production. Branch heads are appropriate for development, not reproducible
generation.

## Copy API

Validate the public payload first, then add the separate generator selector:

```python
from pathlib import Path

from copier import run_copy
from rsm_schema import RSMMetadata


def generate_project(payload: dict, destination: Path, template_ref: str) -> Path:
    """Validate RSM metadata and render one trusted project template."""
    template_type = payload["template_type"]
    metadata = RSMMetadata.model_validate(
        {name: value for name, value in payload.items() if name != "template_type"}
    )
    run_copy(
        "https://github.com/LUMC-DCC/cookiecutter-templates.git",
        destination,
        data={"template_type": template_type, **metadata.model_dump(exclude_none=True)},
        vcs_ref=template_ref,
        defaults=True,
        overwrite=False,
        unsafe=True,
    )
    return destination
```

Use a unique empty destination for each request. Archive that directory only
after Copier returns successfully. Keep `.copier-answers.yml` in the archive:
it records the canonical template source, release, selected language scaffold,
and RSM answers needed for later updates.

`template_type` accepts `python` or `r` and is not part of RSM.
`programming_languages` describes the generated software and may contain
multiple languages; it does not select a template. Treat `template_type` as
immutable after generation. Moving a repository to another language scaffold
is a deliberate migration, not a template update.

Only `project_slug` is required by RSM. Omit unavailable optional properties.
Structured values and controlled choices come directly from the JSON Schema;
do not infer a separate contract from `copier.yml` or the derived questions.
The selected language adds its own slug constraint during prompting and again
during finalization.

## Update API

Generated repositories must be Git-tracked, clean, and contain their committed
answers file. A service can then apply a reviewed release and optionally update
answers:

```python
from pathlib import Path

from copier import run_update


def update_project(project: Path, changes: dict, template_ref: str) -> None:
    """Apply one trusted template release to a clean generated repository."""
    run_update(
        project,
        data=changes,
        vcs_ref=template_ref,
        defaults=True,
        overwrite=True,
        unsafe=True,
    )
```

An update may add or remove capability-driven files when answers change. Review
the resulting Git diff and resolve any conflict markers before committing. Do
not edit `.copier-answers.yml` directly.

## Capability controls

Controlled multi-selects use `entries`, including documentation types,
community files, test types, interfaces, distribution channels, and
containerization. Empty selections omit those capabilities. Scalar selectors,
such as `documentation_builder` and `project_manager`, may be empty; the
language policy chooses the documented baseline when generation still needs
one.

CI workflows are derived from selected capabilities. Metadata, docs, tests,
quality, security, changelog, licensing, containers, and distribution workflows
appear only when their corresponding inputs require them. The minimal
pre-commit file is unconditional because it protects template updates.

Use `_contracts/field_usage.json` for the complete field-to-artifact map.
