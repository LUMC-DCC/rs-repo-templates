# Python template

The Python template creates a package-oriented repository with a `src/` layout.

## Project structure

`src/<project_slug>/` contains the importable Python package.

The generated package starts with a small layered structure:

- `services/` contains reusable project logic.
- `adapters/` contains interface-specific code.
- `ontology/` contains ontology-specific metadata helpers.
- `workflows/` contains workflow entry logic.
- `scripts/` contains standalone script entry points when a script interface is requested.

The package root exports a minimal library API. Shared project logic belongs in
`services/`, so selected entry points can call package code without importing
from another interface boundary.

Implementation code lives in named modules such as `app.py`, `runner.py`,
`registry.py`, `summary.py`, `metadata.py`, or `pipeline.py`. `__init__.py`
files are kept as package boundaries and should not contain substantial
implementation logic.

Interface packages use names that match the boundary they represent. HTTP
payload contracts live in `schemas.py`; command-line actions live in
`commands/`; UI-facing data lives in `view_model.py` or `views.py`; portal data
access lives behind `repository.py`; plug-in contracts live in `hooks.py`;
ontology code separates namespaces, terms, graph construction, serialization,
and validation; workflow orchestration separates config, IO, steps, and the
pipeline.

## Interface scaffolds

| Interface type | Minimal Python scaffold |
| --- | --- |
| `Library` | Public package API backed by `services/processing.py`. |
| `Command-line tool` | Typer app in `adapters/cli/app.py`, commands in `adapters/cli/commands/`, and a console script entry point. |
| `Script` | Thin script in `scripts/` calling reusable package code. |
| `Web API` | FastAPI app in `adapters/api/app.py`, schemas in `schemas.py`, routes in `routes/`. |
| `Web service` | Spyne SOAP 1.1 operations in `adapters/soap/`, generated WSDL, and an ASGI bridge. |
| `SPARQL endpoint` | FastAPI route scaffold in `adapters/api/routes/sparql.py`, backed by the RDF graph layer. |
| `Web application`, `Workbench` | FastAPI web app in `adapters/web/app.py`, routes in `routes/`, and rendering in `views.py`. |
| `Bioinformatics portal`, `Database portal` | FastAPI portal in `adapters/portal/app.py`, routes, record models, repository boundary, rendering, and summary view model. |
| `Desktop application` | Tkinter entry module in `adapters/desktop/app.py` with a separate view model. |
| `Plug-in` | Hook protocol, plug-in registry, and Python entry point metadata. |
| `Suite` | Command registry in `adapters/suite/commands.py` and runner in `runner.py`. |
| `Ontology` | RDFLib-backed namespace definitions, term model, graph builder, metadata helper, validation, and serializers. |
| `Workflow` | Top-level workflow definition folder plus Python config, IO, typed steps, and pipeline modules. |

`pyproject.toml` is the source for Python package metadata and optional
dependency groups such as `test`, `docs`, `quality`, `security`, and HTTP
interface extras.

HTTP-facing projects, and projects that explicitly select secrets or secure
configuration management, include a package-level typed settings module and
`.env.example`. The example contains only non-secret defaults; local `.env`
files stay ignored. `pyproject.toml` remains the Python dependency and project
environment specification.

Generated application entry points configure standard-library logging, while
package modules use named hierarchical loggers. HTTP projects add a `*-serve`
command that consumes the configured bind host, port, reverse-proxy root path,
reload mode, and log level. FastAPI-backed interfaces can additionally publish
an optional public base URL. Container entry points use the same command with a
container-safe bind address.

When HTTP-facing adapters are included, `pyproject.toml` includes optional
dependency groups for those adapters. When a command-line adapter is included,
`pyproject.toml` includes Typer as a package dependency and adds a console
script entry point. A desktop application adds a GUI script entry point.

The Python structure follows a few stable conventions: a `src/` layout for
importable package code, short package `__init__.py` files, `__main__.py` as a
thin entry point, Typer for command-line apps, FastAPI routers for HTTP
applications, Python entry points for plug-ins, RDFLib for RDF-facing
interfaces, and separate workflow folders for Python orchestration and
engine-specific definitions.

See [Interface types](options/interface-types.md) for the full mapping from
context values to generated files, dependencies, metadata, and documentation.

## API, Web, And Portal Interfaces

These interface types overlap in transport but not in intent:

- `Web API` exposes REST-style HTTP endpoints and an OpenAPI description.
- `Web service` exposes SOAP 1.1 operations through a generated WSDL contract.
- `Web application` and `Workbench` expose a browser-facing interactive user
  interface.
- `Bioinformatics portal` and `Database portal` are browser-facing applications
  centered on curated records, search, browsing, or data access.

The generated Python scaffold reflects this by using route and schema modules
for APIs, route and view modules for web applications, and route, model,
repository, summary, and view modules for portals. When several HTTP-facing
types are selected, a server module mounts the adapters under separate paths.

## Ontology And Workflow Interfaces

Ontology scaffolds use RDFLib when `Ontology` or `SPARQL endpoint` is selected.
They separate namespace definitions, term definitions, graph construction,
validation, and serialization.

Workflow scaffolds separate importable Python orchestration from engine-specific
workflow definitions. Python code lives in `src/<project_slug>/workflows/`;
top-level `workflows/` is reserved for CWL, Snakemake, examples, test cases, and
engine configuration.

`README.md`, citation metadata, documentation, and tests follow the general
generated project conventions described in
[Generated projects](generated-projects.md).

Documentation layout depends on `documentation_builder`; see
[Documentation builders](options/documentation-builders.md).

Generated commands live in the generated `README.md` and, when docs are
included, the generated documentation pages.

Generated user, developer, and deployment documentation also follows the
selected interface types. The developer page describes the architecture of the
included scaffolds, the usage page shows relevant run commands, and the
deployment page includes only relevant runtime notes.
The Zensical, MkDocs, and Sphinx scaffolds generate technical reference pages
from public NumPy-style docstrings in the selected package modules.

## Project metadata

The generated project includes public metadata in the places where Python users
and research software registries usually expect it: package metadata,
documentation, README content, and citation metadata.
Python package links use PEP 753's well-known `Project-URL` labels for source,
homepage, documentation, issues, changelog, release notes, downloads, and
funding whenever the corresponding context is available.

When the corresponding metadata is available, the README presents compact
badges for the primary CI workflow, published documentation, GitHub releases,
PyPI, the project DOI, and selected interface types.

When `programming_languages` includes a Python entry with `version_constraint`,
that value is used for `project.requires-python` in `pyproject.toml`.
Selected container recipes derive their Python image version from the same
constraint, choosing the lowest compatible Python 3.12-or-newer runtime.
Without one, the Python template requires Python 3.12 or newer.

When `operating_systems` includes officially supported Linux, macOS, or Windows entries,
the Python template maps them to package operating-system classifiers and to the
tests workflow matrix when GitHub Actions tests are included. Platforms marked
`Expected to work` stay visible in generated documentation and metadata.

Smoke tests verify that selected interface construction points import. When
integration tests are selected, they exercise CLI commands, HTTP requests,
desktop view models, plug-ins, suites, ontologies, workflows, scripts, and SOAP
contracts as applicable to the selected interfaces.

When `external_dependencies` is provided, those entries are documented as
external requirements and added to CodeMeta `softwareRequirements`. They are not
added to `pyproject.toml` package dependencies because PEP 621 dependencies are
Python package requirements.

When `licensing.compatibility_check` selects automated tooling for a recognized SPDX license,
`pyproject.toml` includes a `license` checker extra and `licensecheck`
configuration, and generated CI runs the compatibility check in a dedicated
workflow.

Authors can include display names, structured given/family names, email
addresses, affiliations, ORCID identifiers, and websites.

The template generates `codemeta.json` as the metadata anchor and optionally
generates `CITATION.cff`. The `rs-metadata` workflow validates the LUMC profile
and compares CodeMeta with Python package, citation, and container metadata.
See [Metadata](metadata.md) for the repository-wide strategy. The generated
contributing guide summarizes the selected project manager, quality tools,
tests, documentation builder, metadata, and distribution capabilities.

When `CHANGELOG.md` is included, the Python template also includes
`tools/check_changelog.py`. GitHub Actions runs this check from the shared
`changelog.yml` workflow.

Python documentation and tests use purpose-specific workflows. `docs.yml` builds
the selected Python documentation scaffold when it has a builder, and
`tests.yml` runs pytest when tests are included. Selected `test_types` control
which sample test files are generated. The Python scaffold provides pytest samples
for smoke, doctest, unit, integration, system, regression, and property-based
testing.

Python quality tooling uses separate selectors for the formatter, linter, and
type checker. The current Python scaffold supports `ruff` and optional `mypy`.
Selected tools add local pre-commit hooks and a dedicated `quality.yml` workflow.
Without them, pre-commit retains repository hygiene and template-update conflict
checks.

When `security_measures.selected.entries` includes vulnerability scanning, the
template adds a `security` dependency group and `security.yml`, which audits the
installed environment, reviews dependency changes in pull requests, and runs
scheduled CodeQL analysis.

Workflow inclusion is derived from the selected capabilities; there is no
separate global CI switch. MkDocs derives project identity, description, and
repository links from `codemeta.json`; Sphinx derives project identity,
organization, and repository links from CodeMeta. Sphinx prefers installed
package metadata for the version and uses CodeMeta when building directly from
a source checkout. Documentation CI validates the resulting build.

Generated workflows pin third-party actions to immutable commits. Dependabot
checks those actions and Python project dependencies weekly and proposes updates
through pull requests.

`project_manager` selects the primary development and dependency workflow.
Python supports `uv`, `poetry`, `pdm`, `hatch`, `pixi`, and `pip`; `uv` is the
default. The selection controls generated setup and run commands,
manager-specific `pyproject.toml` configuration, and one reusable CI setup
action used by the Python workflows. Hatchling remains the package build
backend independently of this choice.

Generated repositories do not include a precomputed lockfile. Managers that
support locking create it during normal setup. CI resolves dependencies when no
lockfile exists and checks or uses a committed lockfile when one is present.

The `Library` and `Script` interfaces do not generate Jupyter notebooks. Notebook
generation requires its own controlled metadata value.

## Containers and distribution

Containerization entries use canonical types. `Docker` generates `Dockerfile`,
`OCI / Podman` generates `Containerfile`, and `Apptainer / Singularity`
generates `Apptainer.def`. Docker and OCI use one maintained multi-stage recipe,
run as a non-root user, and select a useful default command from the generated
interfaces. Apptainer includes a runscript and import test. Selected recipes are
built by `containers.yml`; tagged OCI images are published when GitHub Container
Registry or Docker Hub is selected.

`pyproject.toml` is the Python version source of truth. Generated release
documentation records the selected SemVer, CalVer, or custom policy, optional
policy details, release frequency, and controlled distribution channels. For
PyPI, GitHub Releases, or conda-forge, the template adds release dependencies,
`tools/check_release.py`, and `distribution.yml`.
The workflow validates the version and tag, builds and checks the wheel and
source distribution, and publishes the channels it can configure directly.
Selecting Zenodo also generates `.zenodo.json` for Zenodo's GitHub release
archiving, populated from the same authorship, project, recognized grant,
publication, keyword, version, and license context as the other metadata files.

Selecting bio.tools under `registries` generates `biotools.json`. It contains one
schema-compatible record built from the project's identity, homepage, version,
EDAM topics and functions, interfaces, platforms, language, license, access,
publications, contributors, and repository links.

The project manager configures the language-level development environment.
`containerization` separately selects Docker, OCI/Podman, or
Apptainer/Singularity recipes.

`src/<project_slug>/` is for package code. `tools/` is for local project
maintenance commands that may also be called from CI.
