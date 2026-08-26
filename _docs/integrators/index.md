# For service integrators

Integration services map their own data to the published
[RSM 1.0.0 schema](https://lumc-dcc.github.io/rsm-schema/schema/1.0.0/rsm.schema.json).
SMP, DSW, form, and API conversion belongs in the integration service, outside
this repository.

```text
service data
-> RSM metadata
-> RSM Schema validation
-> Cookiecutter extra_context
```

The Cookiecutter process must have the generator dependencies installed. Until
they are published on PyPI, install the pinned Git revisions declared in this
repository's `pyproject.toml`. `rsm-schema` provides validation and
`rs-files-templates` renders reusable repository files.

## Calling a template

1. Select a template directory, such as `python` or `r`, in the calling service.
2. Validate the payload with the RSM JSON Schema or `RSMMetadata` model.
3. Pass the validated values through Cookiecutter `extra_context`.

Template selection is not a public context field. `programming_languages`
describes the generated software and may contain several languages; it does not
select the Cookiecutter directory.

Only `project_slug` is required. Omit optional scalar properties when no value
is available; use empty `entries` collections or schema defaults for structured
controls. Templates may use a valid technical baseline, such as package version
`0.1.0`, where an ecosystem file cannot be empty.

The selected template validates its own slug rules during generation. Python
uses a lowercase Python identifier. R uses a package name that starts with a
letter, contains letters, digits, or dots, and does not end with a dot.

## Structured values

Repeatable template-control values use an `entries` wrapper, including nested
controls such as `motivation.categories`. Arrays within one domain record, such
as person roles or function inputs, remain ordinary arrays:

```json
{
  "contributors": {
    "entries": [
      {
        "name": "Ada Lovelace",
        "given_names": "Ada",
        "family_names": "Lovelace",
        "orcid": "0000-0000-0000-0000",
        "affiliations": [
          {
            "name": "Example University",
            "identifier": "https://ror.org/012345678"
          }
        ],
        "roles": ["Original author", "Maintainer"]
      }
    ]
  }
}
```

Each contributor `name` and at least one controlled `roles` value are required.
Structured names, email, ORCID, URL, and affiliations are optional. Entry schemas use
one form shape, reject unknown properties, and require meaningful content.

Cohesive scalar settings use small objects:

```json
{
  "motivation": {
    "purpose": "Support reproducible analysis.",
    "categories": {"entries": ["Data analysis"]},
    "problem_statement": "Current analyses are difficult to reproduce.",
    "value_proposition": "A shared implementation reduces repeated work."
  },
  "urls": {
    "repository": "https://github.com/example/project",
    "homepage": "",
    "documentation": "https://example.org/project/docs"
  },
  "versioning": {
    "version": "1.0.0",
    "scheme": "SemVer",
    "scheme_details": "",
    "release_frequency": "On demand (irregular/as needed)"
  },
  "licensing": {
    "license": "MIT",
    "compatibility_check": "Yes - automated tooling"
  },
  "contacts": {
    "community": "mailto:community@example.org",
    "code_of_conduct": "mailto:conduct@example.org",
    "security": "mailto:security@example.org"
  }
}
```

`registries` and `persistent_identifiers` remain separate. A registry record
makes software discoverable in a catalogue; a DOI, SWHID, or other persistent
identifier identifies the software independently of catalogue membership.

Funding and similar records no longer use alternative schema branches. A
funding entry is one object whose known properties may be combined as available.

## Controlled capabilities

Controlled multi-selects use `entries`, including audiences, documentation
types, community files, test types, and distribution channels. Their allowed
values are available directly in the JSON Schema.

- `documentation_types.entries` selects `user`, `deployment`, and/or `developer`
  content. An empty list omits `docs/`.
- `documentation_builder` optionally selects a supported site generator. When
  omitted, selected documentation types are generated as plain Markdown.
- `community_files.entries` selects standard root files and defaults to empty.
- `test_types.entries` controls the generated test files and workflow. When
  tests are selected without a framework, the template uses its supported
  framework.
- `quality_tools` groups independently optional `formatter`, `linter`, and
  `type_checker` selectors. `project_manager` remains separate because it
  controls the project environment rather than code-quality policy.
- `interfaces.entries` uses controlled bio.tools tool types. Each selected type
  adds its compatible scaffold; optional specification and status values are
  rendered as public documentation.
- `operating_systems.entries[].name` uses controlled platform names. Officially
  supported desktop platforms define the generated Python CI matrix.

The Python template includes typed runtime configuration when an HTTP-facing
interface is selected or when `security_measures.selected.entries` contains
secrets management or secure configuration management. Other interface types
do not imply configuration files. HTTP selection also adds one configured
server command and environment keys for host, port, proxy root path, reload
mode, and log level. FastAPI-backed selections additionally accept a public base
URL for OpenAPI metadata. Notebook examples likewise require a future explicit
RSM control and are not inferred from `Library` or `Script`.

CI is derived from selected capabilities. Metadata, docs, tests, quality,
security scanning, changelog, licensing, containers, and distribution workflows
are included only when their corresponding inputs request them.

## Metadata and releases

`include_metadata` is one boolean for the minimum metadata set. `true` includes
`codemeta.json`, `CITATION.cff`, and the `rs-metadata` validation workflow;
`false` includes none of them.

`versioning` groups the current version and its policy. Scheme accepts `SemVer`,
`CalVer`, or `Custom` when supplied. Release frequency uses the SMP choices.

`distribution_channels.entries` is independent of registry records. It controls
release guidance and supported publishing workflows. Selecting `Zenodo` also
creates `.zenodo.json`. Selecting a package or container catalogue in
`registries` records discoverability without requesting publication automation.

README badges are derived from repository URLs, documentation URLs, generated
workflows, distribution channels, interface types, and persistent identifiers.

## Licensing and public risk

`licensing.license` accepts an SPDX identifier, custom license text, or an empty
string. Empty omits `LICENSE`. Recognized SPDX identifiers produce canonical
license text and machine-readable metadata. Other non-empty values are written
as custom license text.

`licensing.compatibility_check` optionally selects automated or manual checking.
Automated checking adds supported tooling and CI; manual checking is documented
without adding a checker.

Only public information belongs in `contacts`, `public_risk_notes`,
`security_measures`, `data_management`, and `regulatory_requirements`.
`security_measures` and `regulatory_requirements` both use `selected` and
`additional`; `data_management` groups the public sensitive-data statement and
DMP reference. Selecting vulnerability scanning adds the supported security
workflow. Selecting `CONTRIBUTING.md` adds a pull request template;
selecting `SUPPORT.md` adds structured issue forms.

Use `_contracts/field_usage.json` for the complete field-to-artifact map.
