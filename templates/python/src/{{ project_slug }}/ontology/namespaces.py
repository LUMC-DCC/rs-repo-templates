"""Namespace IRIs used by the {{ (project_name or project_slug) }} ontology.

Namespaces keep RDF identifiers consistent across terms, predicates, and
serialized ontology documents. Replace ``BASE_IRI`` with a stable project IRI
before publishing the ontology.
"""

from rdflib import Namespace
from rdflib.namespace import OWL, RDF, RDFS


# Use a project-specific base IRI so generated ontology terms do not collide
# with terms from other projects.
BASE_IRI = "https://example.org/{{ project_slug }}/ontology/"
EX = Namespace(BASE_IRI)
