# For template developers

This section is for maintainers of the Copier composition and repository
scaffolds.

## Decide where a change belongs

| Change | Repository |
| --- | --- |
| Public field, nested shape, default, or controlled value | `rsm-schema` |
| Reusable file content or metadata mapping | `rs-files-templates` |
| Independent metadata-only Markdown page | `rs-files-templates` |
| Documentation builder, scaffold command, or generated-path guidance | this repository |
| CodeMeta/CFF consistency rules | `rs-metadata` |
| Repository scaffold, supported capability, generated workflow, or assembly | this repository |

Do not add a local public field to make one template work. Add general research
software metadata to RSM; keep implementation support and scaffold constraints
in local policy.

## Question workflow

`_scripts/maintain_repository.py` reads the schema bundled with the locked
`rsm-schema` dependency and writes `_config/copier_questions.yml`. It also
discovers the generator-only `template_type` choices from the directories under
`templates/`; `copier.yml` only contains orchestration settings and includes
the derived questions.

`_config/template_policies.json` adds three kinds of local information:

- the default and validation rules for each scaffold's `project_slug`;
- controlled RSM choices currently implemented by each repository scaffold;
- values exposed to Jinja and finalization as hidden computed answers.

The derived questions are a Copier adapter, not another public contract. Do not
edit them directly. Regenerate after an RSM dependency or policy change:

```bash
poetry run python _scripts/maintain_repository.py --write
```

That command also regenerates the schema field reference and field-usage page,
then checks the installed `rs-files-templates` model inventory and its RSM
contract compatibility. Generated artifacts carry a notice and must not be edited
directly.

## Finalization workflow

`copier.yml` renders one directory under `templates/`, then runs
`_copier_tasks/finalize.py` from the template checkout. The task:

1. reads `.copier-answers.yml` and validates `RSMMetadata`;
2. applies template-specific constraints and supported-choice fallbacks;
3. asks `rs-files-templates` to render selected reusable files;
4. renders selected Markdown pages and attaches builder configuration;
5. assembles interfaces, workflows, and local tooling;
6. removes optional paths not selected by the answers;
7. inserts verified badges into the metadata-rendered README.

Keep `finalize.py` limited to orchestration. Put filesystem actions in
`post_generation/`, content assembly in `renderers/`, and low-level adapters in
`utils/`. These helpers remain in the template source and are not copied into a
generated project.

Tasks must be deterministic and idempotent. Copier may execute them several
times while constructing the old, current, and new states used by an update.
Avoid user-specific state, timestamps, or unbounded side effects. Network
access is reserved for authoritative external content such as SPDX license
text, and failures must stop generation rather than silently fabricate output.

## Template ownership

Prefer ordinary Copier-rendered files for repository scaffolds. Copier can then
merge template releases with project changes. Use a task when output comes from
a typed upstream renderer, requires structured selection, or needs
post-rendering composition.

Do not use `_skip_if_exists` merely because a file will be edited by users; it
also prevents future template improvements from reaching that file. Copier's
three-way merge already preserves edits and reports genuine conflicts. Use
skip behavior only for artifacts that are explicitly one-time and permanently
project-owned.

`.copier-answers.yml` is always generated and committed. It is Copier-owned and
must not be hand-edited. Other generated files can be changed by project teams.

README has an explicit ownership marker. Its standard prefix is rendered
upstream using RSM metadata only; this repository inserts verified badges. Content
below `<!-- rs-files-templates:README:end -->` belongs to the generated project
and must survive finalization. Never add README-only controls to the RSM schema.

Documentation is also composed after Copier rendering. Do not add shared pages
under a scaffold's `docs/_shared/` directory: the six independent base pages
come from `rs-files-templates`. Keep builder configuration, navigation,
dependencies, and builder-specific entry points under `docs/_builders/`.
Builder command profiles and scaffold-specific API or path guidance live here.

## Development workflow

For an RSM field change:

1. make and test the schema change in `rsm-schema`;
2. refresh its `main` revision in `poetry.lock`;
3. run the repository maintenance command;
4. update `_contracts/field_usage.json`;
5. implement scaffold-specific effects and generation tests;
6. run the maintenance command again.

For a reusable file change, implement and test it in `rs-files-templates`, then
refresh the dependency lock here. The maintenance command fails if its public
model inventory or RSM overlap no longer matches this integration. Tests in
this repository cover model selection and complete-project integration, not
duplicate upstream prose.

Keep metadata-only reusable Markdown in `rs-files-templates`. Builder policy
and repository-specific documentation additions belong here.

## Releases and updates

Copier discovers update versions from PEP 440-compatible Git tags. Release
template changes with ordered tags such as `v1.0.0` and avoid rewriting tags.
Production integrators should pin those tags.

Every behavior change should be tested through generation. Changes that affect
existing projects should also be exercised through `copier update`; the
lifecycle test creates two temporary tagged template releases, preserves
project-owned work, changes answers, and verifies the merged repository.

## Field usage

Statuses in `_contracts/field_usage.json` are curated per template:

- `planned`: the RSM field is not consumed yet.
- `control`: it selects generated paths.
- `partial`: some intended targets are covered.
- `implemented`: intended targets are covered by generation tests.
- `external`: another component consumes it.

The generated [field-usage table](../contract/field-usage.md) is a reference,
not a second maintained list.

## Verification

```bash
poetry lock
poetry install --with dev,docs
poetry run python _scripts/maintain_repository.py --write
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

CI checks derived files without rewriting them, then runs every audit, quality,
test, generated-docs, and repository-docs gate. Third-party Actions remain
pinned to full commit SHAs and are updated through Dependabot.
