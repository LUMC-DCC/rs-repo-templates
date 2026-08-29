# Metadata

Generated projects expose the same public facts in the formats used by package
managers, citation tools, registries, archives, and container tooling.

## Metadata model

When minimum metadata is selected, `codemeta.json` is the cross-ecosystem
metadata anchor and `CITATION.cff` is its paired citation record. Python's
`pyproject.toml` remains authoritative for package installation and versioning.
OCI labels repeat only the values their consumers understand. README and
project documentation remain concise human-facing entry points.

The generated files follow the
[LUMC CodeMeta profile](https://lumc-dcc.github.io/rs-metadata/schema/1.0.0/codemeta-lumc.schema.json).
The [rs-metadata crosswalk](https://lumc-dcc.github.io/rs-metadata/developing/crosswalk.html)
defines which overlapping values must agree and which differences are merely
reported.

## After generation

Copier creates the initial metadata from one validated context. After
generation, maintain CodeMeta as the broad metadata anchor and package metadata
as the ecosystem source for package fields. Template updates merge changes to
these files; the validation workflow reports semantic drift between supported
formats.

Mandatory profile fields that cannot be inferred contain conspicuous replacement
placeholders in `codemeta.json`. Replace them with the project's real persistent
identifier, repository URL, and license before expecting metadata CI to pass.

The generated `metadata.yml` workflow uses the official `LUMC-DCC/rs-metadata`
action. It validates the LUMC profile, discovers supported ecosystem files, and
checks their semantic overlap with CodeMeta. `include_metadata` controls
CodeMeta, CFF, and this workflow as one set.
