# LUMC research software templates

[![CI](https://github.com/LUMC-DCC/cookiecutter-templates/actions/workflows/ci.yml/badge.svg)](https://github.com/LUMC-DCC/cookiecutter-templates/actions/workflows/ci.yml) [![Documentation](https://img.shields.io/badge/docs-online-blue?labelColor=gray)](https://lumc-dcc.github.io/cookiecutter-templates/)

Service-agnostic Cookiecutter templates for creating maintainable, FAIR
research software repositories. The Python template is the current reference
implementation; shared policy and hooks support additional language
templates without coupling generation to a particular upstream service.

The public context is defined by
[rsm-schema](https://github.com/LUMC-DCC/rsm-schema), while reusable metadata,
legal, and community files are rendered by
[rs-files-templates](https://github.com/LUMC-DCC/rs-files-templates).

## Documentation

- [Use a generated project](https://lumc-dcc.github.io/cookiecutter-templates/users/)
- [Integrate a generation service](https://lumc-dcc.github.io/cookiecutter-templates/integrators/)
- [Develop the templates](https://lumc-dcc.github.io/cookiecutter-templates/developers/)
- [Understand the architecture](https://lumc-dcc.github.io/cookiecutter-templates/architecture/)

## Development

```bash
poetry install --with docs,dev
poetry run pre-commit install
poetry run python _scripts/sync_shared.py --write
poetry run python _scripts/build_field_usage_docs.py --write
poetry run pre-commit run --all-files
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest
poetry run python _scripts/check_generated_docs.py
poetry run zensical build --strict
```
