# Language-agnostic template

Select `template_type: generic` for a repository foundation that should not
commit to one implementation language. It is suitable for early project setup,
mixed-language work, documentation or metadata repositories, and projects whose
language-specific architecture is maintained separately.

## Always included

| File | Purpose |
| --- | --- |
| `.copier-answers.yml` | Records the template release and RSM answers for future updates. |
| `README.md` | Provides the concise public project entry point. |
| `.editorconfig`, `.gitattributes`, `.gitignore` | Standardize text files and exclude local output, caches, and secrets. |
| `.pre-commit-config.yaml` | Checks common repository files and unresolved merge conflicts. |
| `.github/workflows/repository.yml` | Runs the same repository checks in GitHub Actions. |
| `.github/dependabot.yml` | Proposes weekly updates to GitHub Actions. |

## Selected capabilities

The generic template uses the same RSM controls as the language templates:

- minimum metadata adds `codemeta.json`, `CITATION.cff`, and metadata CI;
- a license adds `LICENSE`;
- community choices add the selected community files, issue forms, pull request
  template, and changelog check;
- documentation types add only the requested pages;
- MkDocs, Zensical, and Sphinx add a self-contained documentation dependency
  file and strict documentation workflow;
- Zenodo adds `.zenodo.json`.

Reusable metadata and community content is rendered by
`rs-files-templates`, exactly as in the language-specific scaffolds.

## Implementation boundary

The template deliberately does not invent a source tree, package manifest,
runtime environment, tests, containers, or ecosystem-specific release commands.
Add those when the implementation architecture is known, or select a language
template when one already matches the project.

The generated developer guide documents the repository-level architecture and
continuous integration that actually exists. Public software functions,
interfaces, platforms, dependencies, services, sustainability, security, and
data-management context still appear in metadata and selected documentation
where applicable.
