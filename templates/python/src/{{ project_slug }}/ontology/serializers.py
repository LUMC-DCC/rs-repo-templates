"""Serializers for {{ (project_name or project_slug) }} ontology data.

The starter serializer writes a Turtle document from an RDFLib graph. Keeping
serialization in one module makes it straightforward to add formats such as RDF
XML, JSON-LD, or N-Triples later.
"""

from rdflib import Graph


def graph_to_turtle(graph: Graph) -> str:
    """Serialize an RDF graph as Turtle.

    Parameters
    ----------
    graph : rdflib.Graph
        RDF graph to serialize.

    Returns
    -------
    str
        Turtle document.
    """
    # RDFLib owns the Turtle syntax details, including escaping, prefixes, and
    # literal formatting.
    return graph.serialize(format="turtle")


def graph_to_json_ld(graph: Graph) -> str:
    """Serialize an RDF graph as JSON-LD.

    Parameters
    ----------
    graph : rdflib.Graph
        RDF graph to serialize.

    Returns
    -------
    str
        JSON-LD document.
    """
    return graph.serialize(format="json-ld")
