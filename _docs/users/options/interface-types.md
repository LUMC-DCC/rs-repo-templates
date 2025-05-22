# Interface types

The `interfaces.entries[].type` values describe how people or systems access
the generated software. The Python template uses those values to keep or remove
minimal scaffold files, dependencies, package metadata, and generated
documentation sections.

Only selected interface scaffolds are kept in the generated repository.

## Python effects

| Interface type | Generated Python effect |
| --- | --- |
| `Library` | Keeps the public package API and reusable service layer. |
| `Command-line tool` | Adds a Typer CLI under `adapters/cli/`, a console script in `pyproject.toml`, and the `typer` dependency. |
| `Script` | Adds a thin standalone script under `scripts/`. |
| `Web API` | Adds a FastAPI API app, route modules, Pydantic schemas, and the `api` optional dependency group. |
| `Web service` | Adds a Spyne SOAP 1.1 service, generated WSDL, WSGI app, ASGI bridge, and the `soap` optional dependency group. |
| `SPARQL endpoint` | Adds a FastAPI SPARQL route, keeps the RDF graph/ontology layer, and adds `rdflib`. |
| `Web application` | Adds a FastAPI browser-facing app with route and view modules, plus the `web` optional dependency group. |
| `Workbench` | Uses the same browser-facing backbone as `Web application`. |
| `Bioinformatics portal` | Adds a portal app with routes, record models, a repository boundary, summary helpers, and views. |
| `Database portal` | Uses the same portal backbone as `Bioinformatics portal`. |
| `Desktop application` | Adds a Tkinter desktop entry point and a separate view model. |
| `Plug-in` | Adds a plug-in protocol, registry, and Python entry point metadata. |
| `Suite` | Adds a command registry and runner for grouped commands. |
| `Ontology` | Adds RDFLib-backed namespace, term, graph, validation, serialization, and metadata helpers. |
| `Workflow` | Adds importable Python workflow modules and a top-level `workflows/` folder for engine-specific definitions. |

When several HTTP-facing types are selected, `adapters/server.py` composes
their applications under stable paths. Container entry points use this server
so the selected REST, SOAP, portal, and browser surfaces can run together.

Generated user, developer, and deployment docs are rendered from the selected
interface types. A project with only a CLI does not receive portal usage notes;
a project with a SPARQL endpoint receives RDF/SPARQL architecture notes.

## R effects

The R scaffold always provides an installable library boundary and exported
starter function. Interface selections are preserved in README, CodeMeta, and
the selected overview, usage, developer, deployment, and reference pages. More
specialized R adapters such as Shiny or plumber applications must be added by the
project; the template does not infer them from an interface label.

## Research guardrails

The Python backbone follows these public conventions and ecosystem references:

- Python package code uses the PyPA `src/` layout guidance.
- Command-line tools use Typer command modules.
- REST APIs, web applications, portals, and SPARQL endpoints use FastAPI
  application factories and route modules.
- SOAP web services use Spyne service declarations and WSDL 1.1.
- Plug-ins use Python entry point metadata.
- Ontology and SPARQL scaffolds use RDFLib and W3C RDF/SPARQL conventions.
- Workflow scaffolds separate importable Python orchestration from
  engine-specific files, matching the way CWL and Snakemake workflows are
  commonly organized.

References:

- [PyPA src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [PyPA entry points](https://packaging.python.org/en/latest/specifications/entry-points/)
- [Typer commands](https://typer.tiangolo.com/tutorial/commands/)
- [FastAPI bigger applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Spyne SOAP service guide](https://spyne.io/docs/2.10/manual/02_helloworld.html)
- [Python tkinter](https://docs.python.org/3/library/tkinter.html)
- [RDFLib graph construction](https://rdflib.readthedocs.io/en/stable/intro_to_creating_rdf/)
- [W3C SPARQL 1.1 Protocol](https://www.w3.org/TR/sparql11-protocol/)
- [Common Workflow Language user guide](https://www.commonwl.org/user_guide/)
- [Snakemake workflow catalog structure](https://snakemake.github.io/snakemake-workflow-catalog/docs/about/adding_workflows.html)
