# Primers for additional rs-files-templates files

These remaining GitHub-facing files are reusable across language templates and
are good candidates for `rs-files-templates`. Pull request and issue templates
are already package-owned. Keep language package code, language test
implementations, documentation-builder configuration, container recipes, and
language environment setup in the repository generator.

For every model below:

- use `FileTemplateModel` or `rsm_template_base` with `extra="forbid"`;
- render through the package `StrictUndefined` environment;
- use concise NumPy-style module and function docstrings;
- test model validation, exact output paths, YAML parsing where applicable,
  conditional sections, and a trailing newline;
- export the model from `rs_files_templates.models` and document it in the API
  inventory.

## Dependabot configuration

- **Output:** `.github/dependabot.yml`
- **Suggested model:** `DependabotModel`
- **RSM fields:** `programming_languages`, `project_manager`
- **Content:** always update pinned GitHub Actions; add only package ecosystems
  that can be derived confidently from the selected manager or languages.
- **Source to migrate:** `templates/*/.github/dependabot.yml`
- **Important behavior:** keep weekly grouped updates, deduplicate ecosystems,
  and do not guess an ecosystem for unsupported managers. A small package-local
  mapping is preferable to exposing generator-private fields.

## Metadata validation workflow

- **Output:** `.github/workflows/metadata.yml`
- **Suggested model:** `MetadataWorkflowModel`
- **RSM fields:** `include_metadata`
- **Content:** read-only permissions, push and pull-request triggers,
  concurrency cancellation, a job timeout, checkout, and the immutable
  `LUMC-DCC/rs-metadata` action reference.
- **Source to migrate:** `templates/*/.github/workflows/metadata.yml`
- **Important behavior:** the consumer omits this file when metadata is not
  selected. Keep action references in one tested constants module so automated
  dependency updates can refresh them.

## Changelog validation command

- **Output:** `tools/check_changelog.py`
- **Suggested model:** `ChangelogCheckModel`
- **RSM fields:** none required.
- **Content:** validate Keep a Changelog headings, release dates, Unreleased
  ordering, and reference labels without deciding whether a change deserves an
  entry.
- **Source to migrate:** `templates/*/tools/check_changelog.py`
- **Important behavior:** keep the validator importable for unit tests and the
  `main()` function usable by CI. Test valid, missing, malformed, and yanked
  release headings.

## Changelog validation workflow

- **Output:** `.github/workflows/changelog.yml`
- **Suggested model:** `ChangelogWorkflowModel`
- **RSM fields:** `community_files`
- **Content:** read-only permissions, push and pull-request triggers,
  concurrency cancellation, a job timeout, Python setup, and execution of the
  generated changelog checker.
- **Source to migrate:** `templates/*/.github/workflows/changelog.yml`
- **Important behavior:** the consumer emits both the checker and workflow only
  when `CHANGELOG.md` is selected.

## Security workflow

- **Output:** `.github/workflows/security.yml`
- **Suggested model:** `SecurityWorkflowModel`
- **RSM fields:** `programming_languages`, `security_measures`
- **Content:** dependency review on pull requests and scheduled CodeQL analysis
  for languages supported by CodeQL, with minimal permissions, concurrency,
  timeouts, and immutable action references.
- **Source to migrate:**
  `templates/python/.github/workflows/security.yml`
- **Important behavior:** emit only when vulnerability scanning is selected;
  map controlled language names to CodeQL identifiers; omit unsupported
  languages rather than guessing; omit the CodeQL job when no selected language
  is supported while retaining dependency review.

## Suggested migration order

1. Metadata and changelog workflow bundle.
2. Dependabot configuration.
3. Security workflow after the language-to-CodeQL mapping is agreed.

After each upstream release, replace the matching local templates here with
package rendering and keep one generation-level integration test per migrated
file family.
