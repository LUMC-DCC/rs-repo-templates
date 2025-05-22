# Context reference

The public context is the published RSM JSON Schema. The generated
[RSM field reference](rsm-fields.md) shows the fields, shapes, requiredness,
defaults, descriptions, and controlled values from the exact locked schema.
Its [Python API](https://lumc-dcc.github.io/rsm-schema/api.html) provides the
matching `RSMMetadata` model and schema-inspection helpers.

Optional properties should be omitted when no value is available. Repeatable
values and nested shapes are defined by the schema; integrators should not
infer them from Copier's questionnaire.

Validate complete payloads with `rsm_schema.validate_document()` before
generation. Generated Pydantic models provide typed access, while the JSON
Schema helper additionally enforces conditional contract rules.

## Local policy

The generated Copier questions add hidden values from
`_config/template_policies.json`:

- template-specific `project_slug` constraints
- documentation builders supported by each template
- test frameworks, quality tools, and project managers supported by each
  template

These values describe generator capability and are not part of the RSM
contract. `programming_languages` describes the generated project and does not
select a template directory.

## Field usage

`_contracts/field_usage.json` records where each RSM field is used and its
status per repository template. The [field-usage table](field-usage.md) is
generated from that map.

Status meanings:

- `control`: selects generated files or directories.
- `implemented`: intended targets are covered.
- `partial`: some relevant targets are covered.
- `planned`: represented by RSM but not yet rendered by that template.
- `external`: consumed outside generated artifacts.

Statuses are curated. The audit verifies schema coverage and catches template
references still marked as planned; it does not guess implementation
completeness.

## Regeneration

After changing local policy or field usage, run:

```bash
poetry run python _scripts/maintain_repository.py --write
```

Public field changes belong in `rsm-schema`. Reusable-file changes belong in
`rs-files-templates`; refresh the dependency lock here after the upstream
change is released or committed.
