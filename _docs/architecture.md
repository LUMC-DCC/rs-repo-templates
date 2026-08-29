# Architecture

This repository composes language-aware Copier projects from a published
metadata contract and reusable repository-file renderers. Python is the
reference implementation; R is an early extension target.

## Ownership boundaries

| Component | Responsibility |
| --- | --- |
| [rsm-schema](https://github.com/LUMC-DCC/rsm-schema) | Public fields, JSON Schema, defaults, controlled values, and Pydantic models. |
| [rs-files-templates](https://github.com/LUMC-DCC/rs-files-templates) | Typed rendering of reusable, language-independent repository files. |
| This repository | Copier orchestration, language policy, source scaffolds, generated CI, and cross-component integration. |
| [rs-metadata](https://github.com/LUMC-DCC/rs-metadata) | Validation of generated research-software metadata and cross-file consistency. |

The published RSM JSON Schema is the sole public input contract. Its current
canonical URL and contents are exposed through the generated
[RSM field reference](contract/rsm-fields.md); this repository does not
maintain a second schema.

`rs-files-templates` renders CodeMeta, CFF, license, Zenodo, changelog,
community, issue, and pull request files. Their prose and format mappings are
owned upstream. This repository selects models and verifies them inside a
complete generated project.

## Generation flow

```text
RSM payload + template_type
    |
    v
RSM validation
    |
    v
Copier questions + language policy
    |
    v
language scaffold rendering
    |
    v
source-side finalization task
    |-- validates the recorded answers again
    |-- renders reusable files with rs-files-templates
    `-- selects docs, tests, CI, tools, and interface scaffolds
    |
    v
generated repository + .copier-answers.yml
```

`template_type` is the one generator-only answer. It selects `templates/python`
or `templates/r`; `programming_languages` continues to describe the software
itself and may contain several languages.

`_scripts/maintain_repository.py` derives the complete question include and RSM
field reference from the installed schema. It discovers `template_type` choices
from `templates/`; `_config/template_policies.json` contributes only
language-specific slug constraints and supported implementation choices. The
same command verifies that every public `rs-files-templates` model is integrated
and remains compatible with RSM.

## Generator dependencies

`rsm-schema` and `rs-files-templates` are intentional generator dependencies,
not generated-project dependencies. They are pinned to reviewed Git commits in
the repository lock file, imported only by source-side finalization, and do not
appear in generated package manifests.

This boundary keeps public schema ownership and reusable file rendering out of
the language scaffolds. Its trade-off is that generation needs those packages
installed and can fail when an upstream API changes. The maintenance check
detects missing, stale, duplicate, or contract-incompatible file models before
generation changes are merged; runtime imports also fail with an actionable
dependency error.

## Update model

Released Git tags make generated repositories updateable. Copier recreates the
old and new template results, computes their difference, and applies it to the
project with a Git-aware three-way merge.

| Generated content | Update behavior |
| --- | --- |
| `.copier-answers.yml` | Copier-owned record; commit it and never edit it manually. |
| CI, package configuration, metadata, and standard repository files | Template-managed but merge-aware; local edits are preserved or surfaced as conflicts. |
| Generated source, tests, and narrative docs | Starting code that project teams may freely evolve; template changes merge when possible. |
| Files created only by the project | Not known to Copier and left untouched. |
| Files intentionally deleted by the project | Remain deleted unless explicitly configured otherwise. |

The finalization task is deterministic and idempotent because Copier may execute
it for old, current, and new renders during an update. It remains in this
template repository and is not copied into generated projects.

Because tasks execute template code, generation and updates require explicit
trust. Integrators should trust only this repository at reviewed release tags.
Generated pre-commit configuration includes a merge-conflict check so unresolved
update markers cannot be committed accidentally.

## Repository layout

- `copier.yml` is the single generation entry point.
- `_config/` contains the derived Copier questions and small language policies.
- `_contracts/field_usage.json` tracks implementation status and targets.
- `_copier_tasks/` contains finalization actions, renderers, and utilities.
- `templates/python/` and `templates/r/` contain language scaffolds.
- `_scripts/` contains repository maintenance and verification commands.
- `tests/` covers schema derivation, generated behavior, and tagged updates.

## Verification

CI checks every derived artifact and generator dependency, audits immutable
GitHub Action pins, runs repository quality checks, renders representative
projects, verifies tagged Copier updates, runs generated tests, builds every
supported Python documentation variant, and builds these docs strictly.

Reusable file content is tested upstream. Integration tests here cover
selection, schema-valid output where useful, and interactions with the rest of
the generated repository.
