"""RDF graph construction for the {{ (project_name or project_slug) }} ontology.

This module converts validated term objects into an RDFLib graph. Keeping graph
construction separate from serialization makes the ontology easier to validate,
query, and publish.
"""

from rdflib import Graph, Literal, URIRef

from {{ project_slug }}.ontology import namespaces
from {{ project_slug }}.ontology.terms import OntologyTerm, default_terms


def ontology_graph(terms: list[OntologyTerm] | None = None) -> Graph:
    """Build the RDF graph for the ontology document.

    Parameters
    ----------
    terms : list[OntologyTerm] | None, optional
        Terms to include. Defaults to the generated starter terms when ``None``.

    Returns
    -------
    rdflib.Graph
        RDF graph containing ontology metadata and terms.
    """
    # The ontology itself is represented as a resource so tools can recognize
    # the generated Turtle document as an OWL ontology.
    graph = Graph()
    graph.bind("ex", namespaces.EX)
    graph.bind("owl", namespaces.OWL)
    graph.bind("rdf", namespaces.RDF)
    graph.bind("rdfs", namespaces.RDFS)

    ontology_iri = URIRef(str(namespaces.EX))
    graph.add((ontology_iri, namespaces.RDF.type, namespaces.OWL.Ontology))
    graph.add(
        (
            ontology_iri,
            namespaces.RDFS.label,
            Literal("{{ (project_name or project_slug) }} ontology"),
        )
    )

    selected_terms = default_terms() if terms is None else terms
    for term in selected_terms:
        # Terms are represented with stable project-local IRIs and human-facing
        # labels/comments. More predicates can be added as the ontology matures.
        subject = namespaces.EX[term.identifier]
        graph.add((subject, namespaces.RDFS.label, Literal(term.label)))
        graph.add((subject, namespaces.RDFS.comment, Literal(term.description)))

    return graph
