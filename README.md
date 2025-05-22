# LUMC research software templates

[![CI](https://github.com/LUMC-DCC/rs-repo-templates/actions/workflows/ci.yml/badge.svg)](https://github.com/LUMC-DCC/rs-repo-templates/actions/workflows/ci.yml) [![Documentation](https://img.shields.io/badge/docs-online-blue?labelColor=gray)](https://lumc-dcc.github.io/rs-repo-templates/)

Copier templates for research-software repositories. The generic scaffold is
language-neutral; the Python and R scaffolds create installable packages that
follow their ecosystems' conventions.

The public input contract comes from
[rsm-schema](https://github.com/LUMC-DCC/rsm-schema). Reusable metadata, legal,
and community files come from
[rs-files-templates](https://github.com/LUMC-DCC/rs-files-templates).
That package also renders the metadata-based README and six Markdown documentation
pages. This repository selects those pages, adds badges, and supplies scaffold- and
documentation-builder-specific files.

Repository metadata output includes CodeMeta and CFF when minimum metadata is
enabled, `biotools.json` when bio.tools is selected as a registry, and
`.zenodo.json` when Zenodo is selected as a distribution channel.

## Generate a project

This trusted template runs finalization tasks. Use a released tag in production
and run Copier in an environment containing this repository's dependencies:

```bash
poetry install --with dev
poetry run copier copy --trust --vcs-ref HEAD . ../generated-project
```

Generated repositories commit `.copier-answers.yml`. After a template release,
they can receive compatible improvements with `copier update --trust` and
Copier's Git-aware three-way merge.

## Documentation

- [Use a generated project](https://lumc-dcc.github.io/rs-repo-templates/users/)
- [Integrate a generation service](https://lumc-dcc.github.io/rs-repo-templates/integrators/)
- [Develop the templates](https://lumc-dcc.github.io/rs-repo-templates/developers/)
- [Understand the architecture](https://lumc-dcc.github.io/rs-repo-templates/architecture/)

## Development

```bash
poetry install --with docs,dev
poetry run pre-commit install
poetry run python _scripts/maintain_repository.py --write
poetry run pre-commit run --all-files
poetry run pytest
poetry run python _scripts/check_generated_docs.py
poetry run zensical build --strict
```
