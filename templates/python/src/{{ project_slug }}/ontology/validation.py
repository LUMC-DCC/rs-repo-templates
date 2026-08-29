"""Validation helpers for {{ (project_name or project_slug) }} ontology terms.

Validation returns messages instead of raising immediately so callers can show
all detected issues at once in a report, user-facing response, or test failure.
"""

from {{ project_slug }}.ontology.terms import OntologyTerm


def validate_terms(terms: list[OntologyTerm]) -> list[str]:
    """Validate the required fields for ontology terms.

    Parameters
    ----------
    terms : list[OntologyTerm]
        Terms to validate.

    Returns
    -------
    list[str]
        Validation messages. An empty list means validation passed.
    """
    messages = []
    identifiers = set()
    for term in terms:
        # Identifiers become part of term IRIs, so missing or duplicate values
        # would make the ontology ambiguous.
        if not term.identifier:
            messages.append("Term identifier is required.")
        if term.identifier in identifiers:
            messages.append(f"Duplicate term identifier: {term.identifier}")
        identifiers.add(term.identifier)

        # Labels and descriptions are the minimum useful human-facing metadata
        # for terms published in generated ontology documentation.
        if not term.label:
            messages.append(f"Term label is required for {term.identifier}.")
        if not term.description:
            messages.append(f"Term description is required for {term.identifier}.")
    return messages
