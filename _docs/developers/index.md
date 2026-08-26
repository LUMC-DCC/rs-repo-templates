# For template developers

This section is for maintainers of the Cookiecutter composition and language
scaffolds.

## Decide where a change belongs

| Change | Repository |
| --- | --- |
| Public field, nested shape, default, or controlled value | `rsm-schema` |
| Reusable file content or metadata mapping | `rs-files-templates` |
| CodeMeta/CFF consistency rules | `rs-metadata` |
| Language scaffold, capability selection, generated workflow, or assembly | this repository |

Do not add a local public field to make one template work. Add it to RSM when it
describes research software generally, or keep it in local policy when it only
describes generator capability.

## Context workflow

`_scripts/build_cookiecutter_context.py` reads the schema bundled with the pinned
`rsm-schema` dependency. It turns schema defaults and top-level scalar enums into
Cookiecutter defaults and prompts. `_config/template_policies.json` adds the
language-specific slug constraints and supported choices stored as private hook
metadata.

`_scripts/sync_shared.py --write` writes each language `cookiecutter.json` and
mirrors shared hooks and assets. These language contexts are derived template
inputs, not public contracts. Its `--check` mode reports drift without changing
the worktree and is used by pre-commit and CI.

The synchronized copies are intentional build artifacts. A template selected
with Cookiecutter's `directory` option must contain its own context, hooks, and
render tree. `pre_gen_project` runs only after that template and its context
have been selected, so it can validate generation but cannot supply missing
template-source files. Keep shared sources canonical under `_cc_shared/` and do
not edit their language copies directly.

At generation time, the post-generation hook:

1. normalizes empty Cookiecutter scalar sentinels and validates `RSMMetadata`;
2. applies language-specific slug and capability policy;
3. asks `rs-files-templates` to render selected reusable files;
4. assembles documentation, interface scaffolds, workflows, and other local
   files;
5. removes template-only helpers.

## Development workflow

For an RSM field change:

1. make and test the schema change in `rsm-schema`;
2. update its pinned commit in `pyproject.toml` and refresh `poetry.lock`;
3. update `_contracts/field_usage.json`;
4. implement the language-specific effects and generation tests;
5. regenerate synchronized files and field-usage docs.

For a reusable file change, make and test it in `rs-files-templates`, then update
the pinned commit here. Tests in this repository should cover selection,
schema-valid output where useful, and interactions with the generated project.
Do not duplicate exact prose snapshots.

Keep builder-neutral documentation under the language template's
`docs/_shared/`. Builder folders contain navigation, configuration, and
builder-specific entry points only. Keep `post_gen_project.py` limited to
orchestration; put actions in `post_generation/`, content assembly in
`renderers/`, and low-level adapters in `utils/`.

## Field usage

Statuses in `_contracts/field_usage.json` are curated per template:

- `planned` means the RSM field is not consumed yet.
- `control` means it selects generated paths.
- `partial` means some intended targets are covered.
- `implemented` means intended targets are covered by generation tests.
- `external` means another component consumes it.

Use short target names that explain the artifact role. The generated
[field-usage table](../contract/field-usage.md) is a reference, not a second
maintained list.

## Regeneration and verification

```bash
poetry lock
poetry install --with dev,docs
poetry run python _scripts/sync_shared.py --write
poetry run python _scripts/build_field_usage_docs.py --write
poetry run pre-commit run --all-files
poetry run ruff check .
poetry run ruff format --check .
poetry run python _scripts/audit_field_usage_status.py
poetry run python _scripts/audit_action_pins.py
poetry run pytest
poetry run python _scripts/check_generated_docs.py
poetry run zensical build --strict
git diff --check
```

CI checks derived files without rewriting them, then runs each audit, quality,
test, and documentation gate once. Third-party Actions remain pinned to full
commit SHAs and are updated through Dependabot.
