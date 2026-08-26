# Architecture

This repository composes language-aware Cookiecutter projects from a published
metadata contract and reusable repository-file renderers. The Python template
is the reference implementation; R is an early extension target.

## Ownership boundaries

| Component | Responsibility |
| --- | --- |
| [rsm-schema](https://github.com/LUMC-DCC/rsm-schema) | Public fields, JSON Schema, defaults, controlled values, and Pydantic models. |
| [rs-files-templates](https://github.com/LUMC-DCC/rs-files-templates) | Typed rendering of reusable, language-independent repository files. |
| This repository | Cookiecutter orchestration, language policy, source scaffolds, generated CI, and cross-component integration. |
| [rs-metadata](https://github.com/LUMC-DCC/rs-metadata) | Validation of generated research-software metadata and cross-file consistency. |

The published [RSM 1.0.0 JSON Schema](https://lumc-dcc.github.io/rsm-schema/schema/1.0.0/rsm.schema.json)
is the public input contract. This repository does not maintain or generate a
copy.

`rs-files-templates` currently renders:

- `CITATION.cff` and `codemeta.json`
- `LICENSE`
- `CHANGELOG.md` and `CODE_OF_CONDUCT.md`
- `GOVERNANCE.md`, `SECURITY.md`, and `SUPPORT.md`
- `.zenodo.json`
- `CONTRIBUTING.md`

Their prose, metadata mappings, SPDX behavior, and output-schema tests belong in
that package. This repository tests that the right model is selected and that
the complete generated project works.

GitHub collaboration files, workflows, and language-specific package files
remain here. Issue forms and the pull-request template could also move when
their models can represent repository-hosting choices without depending on a
language scaffold.

## Generation flow

```text
service payload
    |
    v
RSM Schema validation
    |
    v
Cookiecutter defaults + _config/template_policies.json
    |
    v
language scaffold rendering
    |
    v
post-generation RSM validation and assembly
    |-- rs-files-templates renders reusable files
    `-- local hooks select language, docs, CI, and interface scaffolds
```

`_config/template_policies.json` is deliberately small. It contains only rules
that cannot be part of service-agnostic metadata: language-specific slug
constraints and the builders or tools supported by each template.

Cookiecutter represents an unselected scalar prompt as an empty string. Before
RSM validation, the hook adapter omits those empty properties, matching JSON
Schema semantics for optional fields. It does not rename fields or maintain a
second metadata model.

## Repository layout

- `_config/` contains language-specific generation policy.
- `_contracts/field_usage.json` tracks implementation status and targets for
  published RSM fields.
- `_cc_shared/` contains orchestration and assets shared by language templates.
- `_scripts/` contains maintenance and synchronization commands.
- `python/` and `r/` contain language scaffolds.
- `tests/` renders projects and checks their selected capabilities.

The post-generation entry point remains orchestration-only. Its helpers are
split into actions under `post_generation/`, content assembly under
`renderers/`, and low-level adapters under `utils/`.

## Verification

CI regenerates Cookiecutter contexts and field-usage documentation, checks that
synchronized copies are committed, checks Python quality, audits field
references and immutable Action pins, renders representative projects, runs
generated tests, builds Zensical, MkDocs, and Sphinx variants, and builds these
repository docs strictly.

Reusable file content is tested upstream. Integration tests here may validate
its schema-backed outputs, but should not duplicate exact prose or whitespace
snapshots.
