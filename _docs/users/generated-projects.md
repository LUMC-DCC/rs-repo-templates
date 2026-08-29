# Generated projects

Generated repositories are starting points that retain an update path to later
template releases. They include files that can be used immediately and files
that the project team should review, complete, and adapt.

## Review order

After generation, review the project in this order:

1. Read `README.md`.
2. Check `CITATION.cff` and `codemeta.json`, if metadata was included.
3. Review the selected license.
4. Open `docs/`, if documentation types were selected.
5. Run the commands shown in the generated project.

## Common files

`README.md` is the quick front door for the project. It should stay short and
help people understand what the project is and where to go next. Prefer project
background and scope in `docs/overview.md`. When software functions are
provided, the README includes collapsible `biotools-function` metadata blocks
for tool registries and other downstream services.

When minimum metadata is selected, `CITATION.cff` contains citation metadata and
`codemeta.json` contains FAIR software metadata for catalogues, archives, and
institutional tooling. The files are included or omitted together.

Programming language entries appear in project documentation and in
`codemeta.json`. Software function records describe operations, inputs, outputs,
formats, and command examples in project documentation when provided.
Interface entries describe how users access the software and appear in generated
overview, usage, developer, and technical reference documentation when those
pages exist. Interface status describes maturity or intended visibility; it
does not change the architecture selected by the interface type.
Operating-system entries appear as platform support in the README and generated
documentation, and supported platforms are included in `codemeta.json` when
provided.
External dependency entries appear in generated documentation and are included
in `codemeta.json` as software requirements when provided.
External service entries appear in generated overview and deployment
documentation when provided.
Templates may also use controlled interface entries to include minimal working
code for common access routes, such as command-line tools, web APIs, scripts,
web applications, plug-ins, workflows, ontologies, portals, and library entry
points.

Generated code is deliberately organized so reusable logic sits behind thin
interface layers. Treat package `__init__.py` files as import boundaries rather
than places for application logic.

When runtime configuration is relevant, `.env.example` inventories safe local
defaults and the package settings module validates project-prefixed environment
variables. Generated `.gitignore` rules keep `.env` and environment-specific
variants out of version control while preserving the example file.
HTTP projects use those settings through a generated `*-serve` command. The
same command is used locally and in generated containers, so host, port, proxy
path, reload mode, and log level have one runtime path. FastAPI-backed projects
can additionally publish a public base URL.

`LICENSE` is included when a license value was provided. Recognized SPDX
identifiers are written from SPDX metadata. Unrecognized license values are
written as custom license text.

`docs/` contains project documentation when one or more documentation types are
selected. Longer motivation, scope, funding acknowledgements, and context should
live in the documentation overview rather than making the README heavy.

`tests/` contains the generated test suite when one or more test types are
selected. The selected types control which starter test files are kept. Smoke
tests import selected interface entry points, while integration tests exercise
selected adapter behavior and composed HTTP routes.

`.github/workflows/` contains purpose-specific GitHub Actions configuration.
Each workflow is included only when its corresponding generated capability is
present. Some workflows are shared across templates, and some are
language-specific.

`.copier-answers.yml` records the template source, release, language scaffold,
and answers. Commit it without editing it manually. The small unconditional
`.pre-commit-config.yaml` catches unresolved template-update conflicts; selected
quality tools add their own hooks to the same file.

Python workflows read the supported Python version from `pyproject.toml`, so CI
and package metadata stay aligned when the runtime constraint changes.

| Workflow | Purpose |
| --- | --- |
| `metadata.yml` | Validates research software metadata and supported overlaps. |
| `changelog.yml` | Checks changelog structure when changelog support is included. |
| `license-compatibility.yml` | Checks dependency license compatibility when enabled. |
| `quality.yml` | Runs selected linting, formatting, and type-checking commands. |
| `security.yml` | Reviews dependency changes and runs CodeQL when vulnerability scanning is selected. |
| `docs.yml` | Builds documentation when a buildable docs scaffold is included. |
| `tests.yml` | Runs generated tests when tests are included. |
| `containers.yml` | Builds selected container recipes and publishes configured OCI registries on release tags. |
| `distribution.yml` | Builds Python distributions and publishes configured package or release channels on release tags. |

Python workflows share `.github/actions/setup-python-project/action.yml`, which
installs the selected project manager and prepares one consistent environment
for tests, documentation, quality, licensing, and distribution jobs.

`tools/` contains project-maintenance commands, such as changelog and release
checks. These are not importable package modules or analysis scripts.

Generated documentation includes a release page with the versioning scheme,
expected cadence, distribution destinations, channel setup, and release steps.
Container usage is documented in deployment notes when deployment documentation
is selected.

When relevant public context is supplied, generated documentation also contains
small pages for resource requirements, sustainability, and security and data.
If documentation is omitted, these sections are placed in `README.md` so the
information remains discoverable without duplicating it when docs are present.

MkDocs and Sphinx prefer CodeMeta when it is present and otherwise read matching
core values from `pyproject.toml`. The documentation workflow builds configured
sites in CI. When metadata is included, `rs-metadata` validates the LUMC profile
and compares supported package, citation, and container metadata.

See [Metadata](metadata.md) for how package metadata, CodeMeta, CFF, README
content, and documentation are expected to relate to each other.

## Community files

Community files are optional generated files for collaboration, support,
release notes, governance, and security reporting.

| File | Main context fields |
| --- | --- |
| `CONTRIBUTING.md` | `test_types`, `documentation_types`, quality selectors |
| `CODE_OF_CONDUCT.md` | `contacts.code_of_conduct`, `contributors` |
| `GOVERNANCE.md` | `contributors`, `governance_notes`, `continuity_plan`, `retirement_criteria` |
| `SECURITY.md` | `contacts.security`, `security_measures`, `regulatory_requirements`, `data_management`, `public_risk_notes` |
| `SUPPORT.md` | `urls.documentation`, `support_routes`, `maintenance_level` |
| `CHANGELOG.md` | `versioning`, `urls.repository`, `distribution_channels` |

Review these files before sharing the repository publicly, especially private
contact routes for community and security reports.

When `CONTRIBUTING.md` is included, generated projects also include a GitHub
pull request template in `.github/pull_request_template.md`.

When `SUPPORT.md` is included, generated projects also include structured
GitHub issue forms for bug reports and feature requests in
`.github/ISSUE_TEMPLATE/`.

When `CHANGELOG.md` is included, generated projects also include
`tools/check_changelog.py`. Generated CI calls this check from a shared
`changelog.yml` workflow.

## Generated guidance

Each generated project includes its own commands for installation, usage,
testing, and documentation builds.

Python projects use the selected `project_manager` consistently in those
commands and in language-specific CI. An empty manager selection uses standard
`pip` commands. Lockfiles are created by managers when requested; they are not
manufactured during template generation.

## Project changes

Project teams should update README sections, documentation, metadata, source,
examples, and tests as the project evolves. Copier later uses a three-way merge
to combine those edits with template releases. Project-only files remain
untouched; overlapping edits may require ordinary conflict resolution. See
[Template updates](template-updates.md).
