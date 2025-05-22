"""Render operational, sustainability, security, and data guidance."""


def build_resource_requirements_section(resource_requirements, level=2):
    """Build a public resource requirements section.

    Parameters
    ----------
    resource_requirements : str
        Typical and worst-case runtime requirements.
    level : int, default=2
        Markdown heading level.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    if not resource_requirements:
        return ""

    return f"{'#' * level} Resource requirements\n\n{resource_requirements}"


def build_sustainability_section(
    maintenance_level,
    continuity_plan,
    retirement_criteria,
    level=2,
):
    """Build a public maintenance and continuity section.

    Parameters
    ----------
    maintenance_level : str
        Public maintenance commitment.
    continuity_plan : str
        Public continuity or handover plan.
    retirement_criteria : list[str]
        Conditions under which the project may be retired.
    level : int, default=2
        Markdown heading level.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    details = []
    subsection_level = level + 1
    if maintenance_level:
        details.append(
            f"{'#' * subsection_level} Maintenance commitment\n\n{maintenance_level}"
        )
    if continuity_plan:
        details.append(f"{'#' * subsection_level} Continuity\n\n{continuity_plan}")
    if retirement_criteria:
        criteria = "\n".join(f"- {criterion}" for criterion in retirement_criteria)
        details.append(f"{'#' * subsection_level} Retirement criteria\n\n{criteria}")
    if not details:
        return ""

    return f"{'#' * level} Sustainability\n\n" + "\n\n".join(details)


def build_security_and_data_section(
    security_contact,
    security_measures,
    additional_security_measures,
    sensitive_data_statement,
    public_risk_notes,
    dmp_reference,
    level=2,
):
    """Build public security, risk, and data-management guidance.

    Parameters
    ----------
    security_contact : str
        Private reporting route that may be published.
    security_measures : list[str]
        Controlled public security measures.
    additional_security_measures : str
        Additional public security measures.
    sensitive_data_statement : str
        Public sensitive-data statement.
    public_risk_notes : str
        Public risk and mitigation notes.
    dmp_reference : str
        Public DMP reference.
    level : int, default=2
        Markdown heading level.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    details = []
    subsection_level = level + 1
    if security_contact:
        details.append(
            f"{'#' * subsection_level} Security contact\n\n"
            f"Report suspected vulnerabilities privately to: {security_contact}"
        )
    if security_measures or additional_security_measures:
        content = "\n".join(f"- {measure}" for measure in security_measures)
        if additional_security_measures:
            content = "\n\n".join(
                part for part in (content, additional_security_measures) if part
            )
        details.append(f"{'#' * subsection_level} Security measures\n\n{content}")
    if sensitive_data_statement:
        details.append(
            f"{'#' * subsection_level} Sensitive data\n\n{sensitive_data_statement}"
        )
    if public_risk_notes:
        details.append(
            f"{'#' * subsection_level} Public risk notes\n\n{public_risk_notes}"
        )
    if dmp_reference:
        details.append(
            f"{'#' * subsection_level} Data management plan\n\n{dmp_reference}"
        )
    if not details:
        return ""

    return f"{'#' * level} Security and data\n\n" + "\n\n".join(details)
