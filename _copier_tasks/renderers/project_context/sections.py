"""Compose generated public project-context sections."""

from renderers.project_context.basic import (
    build_access_section,
    build_audience_section,
    build_funding_section,
    build_problem_statement_section,
    build_purpose_categories_section,
    build_purpose_section,
    build_related_software_section,
    build_value_proposition_section,
)
from renderers.project_context.interoperability import (
    build_external_dependencies_section,
    build_external_services_section,
    build_interfaces_section,
    build_operating_systems_section,
    build_programming_languages_section,
    build_software_functions_section,
)
from utils.context import entries, object_entries, object_value


def build_project_context_sections(
    ctx,
    include_funding,
    include_interoperability=True,
    include_motivation_details=True,
):
    """Build public project context sections.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    include_funding : bool
        Whether to include funding acknowledgements.
    include_interoperability : bool, default=True
        Whether to include interoperability summaries.
    include_motivation_details : bool, default=True
        Whether to include the full problem and value statements.

    Returns
    -------
    str
        Combined Markdown sections.
    """
    sections = [
        build_purpose_section(object_value(ctx, "motivation", "purpose")),
        build_purpose_categories_section(
            object_entries(ctx, "motivation", "categories")
        ),
        build_audience_section(entries(ctx, "audiences")),
        build_related_software_section(entries(ctx, "related_software")),
        build_access_section(
            object_value(ctx, "access", "type"),
            object_value(ctx, "access", "details"),
        ),
    ]
    if include_motivation_details:
        sections[2:2] = [
            build_problem_statement_section(
                object_value(ctx, "motivation", "problem_statement")
            ),
            build_value_proposition_section(
                object_value(ctx, "motivation", "value_proposition")
            ),
        ]
    if include_interoperability:
        sections.extend(
            [
                build_programming_languages_section(
                    entries(ctx, "programming_languages")
                ),
                build_software_functions_section(entries(ctx, "software_functions")),
                build_interfaces_section(entries(ctx, "interfaces")),
                build_operating_systems_section(entries(ctx, "operating_systems")),
                build_external_dependencies_section(
                    entries(ctx, "external_dependencies")
                ),
                build_external_services_section(entries(ctx, "external_services")),
            ]
        )
    if include_funding:
        sections.append(build_funding_section(entries(ctx, "funding")))

    sections = [section for section in sections if section]
    if not sections:
        return ""

    return "\n\n" + "\n\n".join(sections) + "\n"
