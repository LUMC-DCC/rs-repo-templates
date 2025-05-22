"""SPARQL endpoint routes for the web API adapter.

This starter route evaluates read-only SPARQL queries against the project's
starter RDF graph. It can later be replaced by a persistent RDF store while
keeping the route contract stable.
"""

from fastapi import APIRouter
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.query import Result

from {{ project_slug }}.ontology.graph import ontology_graph


router = APIRouter(tags=["sparql"])


def _binding(value: BNode | Literal | URIRef | None) -> dict[str, str]:
    """Convert an RDFLib term to a SPARQL JSON binding.

    Parameters
    ----------
    value : rdflib.term.BNode | rdflib.term.Literal | rdflib.term.URIRef | None
        RDF term returned by a query result row.

    Returns
    -------
    dict[str, str]
        SPARQL JSON binding object.
    """
    if value is None:
        return {"type": "literal", "value": ""}
    if isinstance(value, URIRef):
        return {"type": "uri", "value": str(value)}
    if isinstance(value, BNode):
        return {"type": "bnode", "value": str(value)}
    return {"type": "literal", "value": str(value)}


def _select_response(result: Result) -> dict[str, object]:
    """Convert a SELECT query result to SPARQL JSON format.

    Parameters
    ----------
    result : rdflib.query.Result
        SELECT query result.

    Returns
    -------
    dict[str, object]
        SPARQL JSON result payload.
    """
    variables = [str(variable) for variable in result.vars]
    bindings = []
    for row in result:
        bindings.append(
            {
                variable: _binding(row[index])
                for index, variable in enumerate(variables)
            }
        )
    return {"head": {"vars": variables}, "results": {"bindings": bindings}}


def _query_response(graph: Graph, query: str) -> dict[str, object]:
    """Run a SPARQL query and return a JSON-compatible response.

    Parameters
    ----------
    graph : rdflib.Graph
        RDF graph to query.
    query : str
        SPARQL query string.

    Returns
    -------
    dict[str, object]
        JSON-compatible SPARQL response.
    """
    result = graph.query(query)
    if result.type == "ASK":
        return {"boolean": bool(result.askAnswer)}
    if result.type == "SELECT":
        return _select_response(result)

    # CONSTRUCT and DESCRIBE queries return RDF graphs. Turtle keeps the starter
    # response inspectable without introducing content negotiation yet.
    return {
        "format": "text/turtle",
        "data": result.graph.serialize(format="turtle"),
    }


@router.get("/sparql")
def sparql(
    query: str = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 25",
) -> dict[str, object]:
    """Run a SPARQL query against the starter RDF graph.

    Parameters
    ----------
    query : str, default="SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 25"
        SPARQL query string.

    Returns
    -------
    dict[str, object]
        SPARQL response payload.
    """
    # Build the starter graph per request. Projects with larger datasets should
    # replace this with a configured RDF store or cached graph.
    return _query_response(ontology_graph(), query)
