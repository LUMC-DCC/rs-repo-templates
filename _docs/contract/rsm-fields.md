# RSM field reference

Generated from the [published RSM schema](https://lumc-dcc.github.io/rsm-schema/schema/1.0.0/rsm.schema.json). Do not edit this page directly.

| Field | Shape | Required | Schema default | Description |
| --- | --- | --- | --- | --- |
| `project_name` | string | no | Not defined | Human-readable project title. |
| `project_slug` | string | yes | `"project"` | Machine-readable package and repository name. Consumers apply their own additional slug constraints. |
| `project_short_description` | string | no | Not defined | One-sentence description used in README and package metadata. |
| `project_long_description` | string | no | Not defined | Longer public description of the project motivation and scope. |
| `development_status` | string | no | Not defined | Current repostatus.org lifecycle status for the software. |
| `topics` | collection object | no | `{"entries":[]}` | Research domains the software applies to, as EDAM topic terms. Entries may include term and uri. Broader and controlled where keywords are free text. |
| `keywords` | collection object | no | `{"entries":[]}` | Public keywords used in package metadata, citation metadata, registries, and archives. |
| `contributors` | collection object | no | `{"entries":[]}` | Everyone credited for the software, each entry declaring one or more roles. Name and roles are required; entries may also include given_names, family_names, email, affiliations, orcid, and url. A non-empty list must credit at least one author, which is what citation metadata requires. |
| `funding` | collection object | no | `{"entries":[]}` | Public funding records. Entries may include funder, funder identifiers and URLs, award_number, award_title, grant_url, and project_code. |
| `motivation` | object | no | `{"categories":{"entries":[]}}` | Public purpose, purpose categories, problem statement, and value proposition. |
| `audiences` | collection object | no | `{"entries":[]}` | Intended users or stakeholder groups. |
| `related_software` | collection object | no | `{"entries":[]}` | Related or upstream tools. Entries may include name, url_or_doi, and relationship. |
| `urls` | object | no | `{}` | Canonical source repository, project homepage, and published documentation URLs. |
| `registries` | collection object | no | `{"entries":[]}` | Registry entries such as PyPI, CRAN, bio.tools, WorkflowHub, or institutional catalogues. Entries may include name, url_or_id, and notes. |
| `persistent_identifiers` | collection object | no | `{"entries":[]}` | Persistent identifiers. Each entry declares its CFF identifier type and value, with an optional associated version. |
| `publications` | collection object | no | `{"entries":[]}` | Associated publications. Entries may include title, type, authors, doi, pmid, pmcid, url, citation, note, and preferred. |
| `licensing` | object | no | `{}` | License text or SPDX identifier and the selected dependency-license compatibility method. |
| `access` | object | no | `{}` | How users can obtain or use the software, independently of its copyright license. |
| `include_metadata` | boolean | no | `false` | Whether the project publishes CodeMeta and Citation File Format metadata files alongside their validation workflow. |
| `documentation_builder` | string | no | Not defined | Optional documentation site generator. An empty selection means documentation is plain Markdown. |
| `documentation_types` | collection object | no | `{"entries":[]}` | SMP documentation categories the project provides. API and technical reference material are part of developer documentation. |
| `community_files` | collection object | no | `{"entries":[]}` | Standard root community files the project provides. CONTRIBUTING.md and SUPPORT.md imply the corresponding GitHub collaboration files. |
| `code_review_policy` | string | no | Not defined | Public code-review policy for proposed changes, including reviewer expectations, approval requirements, and merge conditions. Markdown is supported. |
| `support_routes` | collection object | no | `{"entries":[]}` | Public support, bug-reporting, or feature-request systems and their public URLs. |
| `contacts` | object | no | `{}` | Public contact routes for general community, code-of-conduct, and private security reports. |
| `governance_notes` | string | no | Not defined | Public governance and decision-making notes. |
| `programming_languages` | collection object | no | `{"entries":[]}` | Programming languages used by the project. Entries include a name and may include version_constraint and role from the SMP. |
| `software_functions` | collection object | no | `{"entries":[]}` | Functions or operations performed by the software. Entries may include operations, inputs, outputs, cmd, and note. |
| `interfaces` | collection object | no | `{"entries":[]}` | Interfaces exposed by the software. Type names the interface; specification and status describe it. |
| `operating_systems` | collection object | no | `{"entries":[]}` | Supported operating systems or platforms. Entries may include name, specification, and status from the SMP. |
| `external_dependencies` | collection object | no | `{"entries":[]}` | External software dependencies or standards. Entries may include name, version_constraint, url, license, and purpose. |
| `external_services` | collection object | no | `{"entries":[]}` | External public services, partners, or roles needed by the project. Entries may include name, provider, service_types, quantity, and cost_coverage. |
| `test_types` | collection object | no | `{"entries":[]}` | Types of tests used or desired. Supported values match the SMP testing checklist. |
| `test_frameworks` | collection object | no | `{"entries":[]}` | Testing frameworks used by the project. |
| `quality_tools` | object | no | `{}` | Optional primary formatter, linter, and static type checker. |
| `project_manager` | string | no | Not defined | Primary project and dependency manager, which determines setup, command execution, lockfile handling, and CI. |
| `versioning` | object | no | `{}` | Version value and public release policy. Empty properties leave the policy unspecified. |
| `distribution_channels` | collection object | no | `{"entries":[]}` | Controlled public distribution routes, including package registries, releases, archives, installers, and hosted services. |
| `containerization` | collection object | no | `{"entries":[]}` | Container recipes the project ships. Project managers and lockfiles are declared separately. |
| `resource_requirements` | string | no | Not defined | Public typical and worst-case memory, storage, compute, GPU, wall-clock, or scaling requirements. |
| `maintenance_level` | string | no | Not defined | Public maintenance commitment after active development winds down; leave empty when no commitment is declared. |
| `continuity_plan` | string | no | Not defined | Public continuity or handover plan. |
| `retirement_criteria` | collection object | no | `{"entries":[]}` | Public conditions under which the software may be retired. |
| `public_risk_notes` | string | no | Not defined | Public risk or mitigation notes. Sensitive security, privacy, or compliance details should not be included. |
| `regulatory_requirements` | object | no | `{"selected":{"entries":[]}}` | Controlled and additional public regulatory, quality, policy, or availability requirements. |
| `security_measures` | object | no | `{"selected":{"entries":[]}}` | Controlled and additional public security measures protecting the software and its data. |
| `data_management` | object | no | `{}` | Public sensitive-data statement and DMP reference or contact route. |

## Controlled values

### `development_status`

- `concept`, `wip`, `active`, `inactive`, `suspended`, `abandoned`, `unsupported`, `moved`

### `contributors`

- `entries[].roles[]`: `Original author`, `Co-author`, `Maintainer`, `Successor`, `Principal investigator`

### `funding`

- `entries[].funder_identifier_type`: `ror`, `crossref-funder-id`, `other`

### `motivation`

- `categories.entries[]`: `Data collection & instrumentation`, `Data analysis`, `Simulation`, `Visualization & dissemination`, `Software reuse`, `Integration & interfacing`

### `audiences`

- `entries[]`: `Researchers (academia)`, `Clinicians / healthcare professionals`, `Data stewards / data managers`, `Bioinformaticians / computational scientists`, `Lab scientists`, `Students / educators`, `Software developers / RSEs`, `Institutional IT staff / system administrators`, `Policy makers / funders`, `Industry users / pharma / biotech`, `General public / citizen scientists`

### `persistent_identifiers`

- `entries[].type`: `doi`, `url`, `swh`, `other`

### `publications`

- `entries[].authors[].roles[]`: `Original author`, `Co-author`, `Maintainer`, `Successor`, `Principal investigator`

### `licensing`

- `compatibility_check`: `Yes - automated tooling`, `Yes - manual check`

### `access`

- `type`: `free`, `free-with-restrictions`, `commercial`

### `documentation_builder`

- `mkdocs`, `pkgdown`, `sphinx`, `zensical`

### `documentation_types`

- `entries[]`: `user`, `deployment`, `developer`

### `community_files`

- `entries[]`: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `GOVERNANCE.md`, `SECURITY.md`, `SUPPORT.md`, `CHANGELOG.md`

### `interfaces`

- `entries[].type`: `Bioinformatics portal`, `Command-line tool`, `Database portal`, `Desktop application`, `Library`, `Ontology`, `Plug-in`, `Script`, `SPARQL endpoint`, `Suite`, `Web application`, `Web API`, `Web service`, `Workbench`, `Workflow`
- `entries[].status`: `Stable`, `Experimental`, `Internal`

### `operating_systems`

- `entries[].name`: `Linux`, `macOS`, `Windows`, `iOS`, `Android`, `HPC environments`, `Container`, `Platform independent`, `Other`
- `entries[].status`: `Officially supported`, `Expected to work`

### `external_services`

- `entries[].service_types[]`: `Institutional support (DCC, IT, library)`, `Hosted compute / storage`, `CI / CD minutes`, `SaaS subscription`, `Legal / contractual`, `External review or audit`, `Domain expertise`, `Other`
- `entries[].cost_coverage[]`: `Project budget`, `Departmental overhead`, `External grant`, `Free tier`, `In-kind / unfunded`

### `test_types`

- `entries[]`: `Smoke tests`, `Doctests`, `Unit tests`, `Integration tests`, `System / end-to-end tests`, `Regression tests`, `Property-based / fuzz`

### `test_frameworks`

- `entries[]`: `pytest`, `unittest`, `doctest`, `testthat`, `Catch2`, `GoogleTest`, `cargo test`, `JUnit 5`, `Vitest`, `Jest`, `bats-core`

### `quality_tools`

- `formatter`: `ruff`, `black`, `styler`, `prettier`, `rustfmt`, `clang-format`
- `linter`: `ruff`, `flake8`, `pylint`, `lintr`, `eslint`, `clippy`, `clang-tidy`
- `type_checker`: `mypy`, `pyright`, `basedpyright`, `pyre`, `tsc`, `rustc`, `Flow`

### `project_manager`

- `uv`, `poetry`, `pdm`, `hatch`, `pixi`, `pip`, `renv`, `rix`, `cargo`, `npm`, `pnpm`, `yarn`, `maven`, `gradle`, `cmake`

### `versioning`

- `scheme`: `SemVer`, `CalVer`, `Custom`
- `release_frequency`: `On demand (irregular/as needed)`, `After each major feature`, `After bug fixes or patches`, `On (fixed) schedule - automated`, `On (fixed) schedule`, `Single release - no updates`

### `distribution_channels`

- `entries[]`: `PyPI`, `conda-forge`, `CRAN`, `Bioconductor`, `npm`, `crates.io`, `Docker Hub`, `GitHub Container Registry`, `Quay`, `Apptainer Library`, `BioContainers`, `GitHub Releases`, `Zenodo`, `Institutional archive`, `Self-hosted installer`, `Hosted service`, `Other`

### `containerization`

- `entries[].type`: `Docker`, `OCI / Podman`, `Apptainer / Singularity`, `Other`

### `maintenance_level`

- `Active/routine maintenance`, `Security maintenance only`, `Best-effort maintenance / no timeline commitment`

### `retirement_criteria`

- `entries[]`: `Project completed`, `Replaced by successor software`, `Obsolete technology / architecture`, `Incompatible with current systems`, `Loss or end of funding`, `Lack of maintainers`, `Institutional shift in priorities`, `Retirement of critical dependencies`, `Discontinuation of hosting / infrastructure`, `Change in legal or regulatory requirements`, `Security / privacy risks`, `Lack of user demand or adoption`, `Declining utility or relevance`

### `regulatory_requirements`

- `selected.entries[]`: `GDPR - General Data Protection Regulation (EU data protection)`, `MDR / IVDR - EU Medical Device Regulation / In Vitro Diagnostic Regulation`, `Other EU or National Regulations (e.g., Dutch WMO, data processing agreements)`, `ISO/IEC 27001 - Information Security Management`, `ISO 13485 - Quality Management for Medical Devices`, `ISO/IEC 90003 - Software Engineering (guidelines for ISO 9001)`, `ISO/IEC 12207 - Software Lifecycle Processes`, `GxP / Good Clinical Practice`, `Ethical Approval / IRB Requirements`, `Funding Programme Requirements (e.g., Horizon Europe, NWO, ELIXIR)`, `Institutional Security Policies`, `Departmental SOP (Zenya / EDR)`, `Journal data/software-availability requirement`, `Commissie Good Research Practice (GRP)`

### `security_measures`

- `selected.entries[]`: `User authentication (e.g., password, OAuth, SSO)`, `Role-based access control (RBAC) or permissions system`, `Data encryption at rest`, `Data encryption in transit (e.g., HTTPS/TLS)`, `Regular dependency / library updates`, `Security patch management process`, `Vulnerability scanning (e.g., Snyk, Dependabot)`, `Secrets management (e.g., environment variables, vault)`, `Network security (e.g., firewalls, VPN, isolated subnets)`, `Secure configuration management (e.g., Infrastructure-as-Code, hardening)`, `Audit logging / intrusion detection`, `Penetration testing or security review`, `Follows institutional or regulatory security policies (e.g., ISO 27001, NEN 7510)`
