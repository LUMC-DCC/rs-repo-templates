# R template

The R template creates an installable package using conventional
`DESCRIPTION`, `NAMESPACE`, `R/`, `man/`, and `tests/testthat/` boundaries. The
starter `process_text()` function is exported and documented so a newly
generated package can be built immediately.

## Package structure

| Path | Purpose |
| --- | --- |
| `DESCRIPTION` | Package identity, version, R requirement, contributors, links, and selected development dependencies. |
| `NAMESPACE` | Initial exported API. Regenerate it with `man/` if the project adopts roxygen2. |
| `R/` | Reusable package implementation. |
| `man/` | Installed function reference documentation. |
| `tests/testthat/` | Starter files for the selected SMP test types. |
| `<package>.Rproj` | Portable RStudio and Positron package-project settings. |

`programming_languages` entries for R determine the lower R version used by
`DESCRIPTION` and generated container images. Contributors are mapped to
`Authors@R`; authors and maintainers receive the corresponding `aut` and `cre`
roles, while structured names, email addresses, and ORCID identifiers are
preserved.

For MIT projects, `LICENSE` uses the DCF copyright stub required by R package
checks while `LICENSE.md` preserves the complete SPDX license text for readers
and repository tooling. Repository-only files are excluded from source-package
builds through `.Rbuildignore`.

## Reproducible environments

`project_manager: renv` is the default. The generated setup command initializes
the project on first use and restores `renv.lock` thereafter. Commit that
lockfile after dependency resolution; the project library itself stays ignored.

Selecting `rix` retains `environment.R`. Running it generates a Nix expression
from the selected test, documentation, and quality dependencies, after which
development commands can run inside `nix-shell`.

## Tests and quality

Selecting test types keeps matching testthat files and adds `tests.yml`.
Officially supported Linux, macOS, and Windows entries determine the hosted
runner matrix; platforms marked “Expected to work” remain documented without
being promoted to required CI jobs.

The R scaffold supports `styler` for formatting and `lintr` for linting. Each
selection updates `DESCRIPTION`, local pre-commit hooks, contributor commands,
and `quality.yml`. R currently has no separate static type-checker choice in the
RSM controlled vocabulary.

## Documentation

Selecting pkgdown adds `_pkgdown.yml` and a pinned documentation workflow. The
site is written to `site/`, leaving narrative project pages under `docs/`
available for repository rendering and future template updates. With no builder,
the selected pages remain plain Markdown and no docs workflow is generated.

## Containers and releases

Docker, OCI/Podman, and Apptainer selections produce R package images based on
the declared R lower bound. Images build and install the source package, run as
a non-root container user where applicable, and expose a package smoke command.

CRAN, Bioconductor, and GitHub Releases add source-package build and check
automation. Tagged GitHub releases can attach the generated `.tar.gz`; CRAN and
Bioconductor remain review-driven external submissions. Zenodo continues to use
the shared `.zenodo.json` metadata integration.

## Shared repository features

The R template uses the same reusable CodeMeta, CFF, license, community,
governance, support, issue, and pull-request renderers as the other scaffolds.
Access terms, funding identifiers, code-review policy, sustainability, security,
data management, functions, interfaces, external dependencies, and services
therefore remain synchronized across README, documentation, and metadata.
