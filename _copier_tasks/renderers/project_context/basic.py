"""Render general public project-context sections."""


def format_funding_label(funding):
    """Format one public funding record.

    Parameters
    ----------
    funding : dict
        Funding record from the normalized Copier context.

    Returns
    -------
    str
        Human-readable funding label.
    """
    funder = funding.get("funder", "")
    award_title = funding.get("award_title", "")
    award_number = funding.get("award_number", "")
    project_code = funding.get("project_code", "")
    grant_url = funding.get("grant_url", "")

    if funder:
        label = funder
        if award_title:
            label = f"{label}: {award_title}"
    elif award_title:
        label = award_title
    elif award_number:
        label = f"Award {award_number}"
    elif project_code:
        label = f"Project {project_code}"
    else:
        label = "Funding record"

    if award_number and funder and award_title:
        label = f"{label} (award {award_number})"
    if project_code:
        label = f"{label} (project {project_code})"
    if grant_url:
        label = f"{label} ([grant]({grant_url}))"

    return label


def format_related_software_label(software):
    """Format one related software record.

    Parameters
    ----------
    software : dict
        Related software record from the normalized Copier context.

    Returns
    -------
    str
        Human-readable related software label.
    """
    name = software.get("name", "")
    url_or_doi = software.get("url_or_doi", "")
    relationship = software.get("relationship", "")

    if name and url_or_doi:
        label = f"[{name}]({url_or_doi})"
    elif name:
        label = name
    elif url_or_doi:
        label = url_or_doi
    else:
        label = "Related software"

    if relationship:
        label = f"{label} - {relationship}"

    return label


def build_purpose_section(purpose):
    """Build the generated purpose section.

    Parameters
    ----------
    purpose : str
        Public statement of why the software exists.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    if not purpose:
        return ""

    return f"## Purpose\n\n{purpose}"


def build_problem_statement_section(problem_statement):
    """Build the generated problem statement section.

    Parameters
    ----------
    problem_statement : str
        Public description of the problem addressed by the software.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    if not problem_statement:
        return ""

    return f"## Problem\n\n{problem_statement}"


def build_value_proposition_section(value_proposition):
    """Build the generated project value section.

    Parameters
    ----------
    value_proposition : str
        Public explanation of the project's value and need.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    if not value_proposition:
        return ""

    return f"## Value and need\n\n{value_proposition}"


def build_purpose_categories_section(purpose_categories):
    """Build the generated purpose categories section.

    Parameters
    ----------
    purpose_categories : list[str]
        Public purpose categories from the normalized Copier context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    if not purpose_categories:
        return ""

    category_lines = [f"- {category}" for category in purpose_categories]
    return "## Purpose Categories\n\n" + "\n".join(category_lines)


def build_audience_section(audience_entries):
    """Build the generated audience section.

    Parameters
    ----------
    audience_entries : list[str]
        Intended audiences from the normalized Copier context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    if not audience_entries:
        return ""

    audience_lines = [f"- {audience}" for audience in audience_entries]
    return "## Intended Audience\n\n" + "\n".join(audience_lines)


def build_related_software_section(related_software_entries):
    """Build the generated related software section.

    Parameters
    ----------
    related_software_entries : list[dict]
        Related software records from the normalized Copier context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    if not related_software_entries:
        return ""

    software_lines = [
        f"- {format_related_software_label(software)}"
        for software in related_software_entries
    ]
    return "## Related Software\n\n" + "\n".join(software_lines)


def build_funding_section(funding_entries):
    """Build the generated funding section.

    Parameters
    ----------
    funding_entries : list[dict]
        Funding records from the normalized Copier context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    if not funding_entries:
        return ""

    funding_lines = [
        f"- {format_funding_label(funding)}" for funding in funding_entries
    ]
    return "## Funding\n\n" + "\n".join(funding_lines)
