"""Public ontology metadata helpers for {{ (project_name or project_slug) }}.

This module exposes small functions that callers can use to retrieve ontology
metadata or a serialized starter ontology document.
"""

from {{ project_slug }}.ontology.graph import ontology_graph
from {{ project_slug }}.ontology.serializers import graph_to_turtle
from {{ project_slug }}.ontology.terms import default_terms
from {{ project_slug }}.ontology.validation import validate_terms


def ontology_metadata() -> dict[str, str]:
    """Return ontology metadata for this project.

    Returns
    -------
    dict[str, str]
        Ontology metadata payload.
    """
    # Keep this payload simple and serializable so it can be consumed by
    # documentation pages, metadata export tools, or tests.
    return {
        "name": "{{ (project_name or project_slug) }} ontology",
        "description": "{{ project_short_description }}",
    }


def ontology_document() -> str:
    """Return the serialized starter ontology document.

    Returns
    -------
    str
        Turtle ontology document.
    """
    terms = default_terms()
    messages = validate_terms(terms)
    if messages:
        # Surface all validation messages together so users can fix terms in
        # one pass.
        raise ValueError("; ".join(messages))
    return graph_to_turtle(ontology_graph(terms))
