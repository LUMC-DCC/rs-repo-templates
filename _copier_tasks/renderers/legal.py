"""Build generated legal and licensing text."""


def build_license_label(license_value):
    """Build a human-readable license label.

    Parameters
    ----------
    license_value : str
        SPDX license identifier, custom license text, or an empty string.

    Returns
    -------
    str
        Markdown label for the selected license.
    """
    value = license_value.strip()
    if "\n" in value or " " in value:
        return "the custom terms in `LICENSE`"

    return f"`{value}`"


def build_legal_lines(license_value, compatibility_notes, license_path="LICENSE"):
    """Build generated legal and licensing lines.

    Parameters
    ----------
    license_value : str
        SPDX license identifier, custom license text, or an empty string.
    compatibility_notes : str
        Public notes about license compatibility.
    license_path : str, default="LICENSE"
        Repository path containing the complete human-readable terms.

    Returns
    -------
    list[str]
        Human-readable legal and licensing paragraphs.
    """
    lines = []
    if license_value.strip():
        label = build_license_label(license_value)
        lines.append(
            f"This project is licensed under {label}. "
            f"See `{license_path}` for the full license text."
        )
    if compatibility_notes:
        lines.append(compatibility_notes)

    return lines


def build_legal_section(
    license_value,
    compatibility_notes,
    license_path="LICENSE",
):
    """Build the generated legal and licensing section.

    Parameters
    ----------
    license_value : str
        SPDX license identifier, custom license text, or an empty string.
    compatibility_notes : str
        Public notes about license compatibility.
    license_path : str, default="LICENSE"
        Repository path containing the complete human-readable terms.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    lines = build_legal_lines(license_value, compatibility_notes, license_path)
    if not lines:
        return ""

    return "## Legal and Licensing\n\n" + "\n\n".join(lines)


def build_legal_page_content(
    license_value,
    compatibility_notes,
    regulatory_requirements=None,
    additional_regulatory_requirements="",
    license_path="LICENSE",
):
    """Build content for the generated legal documentation page.

    Parameters
    ----------
    license_value : str
        SPDX license identifier, custom license text, or an empty string.
    compatibility_notes : str
        Public notes about license compatibility.
    regulatory_requirements : list[str] or None, optional
        Controlled public regulatory and policy requirements.
    additional_regulatory_requirements : str, optional
        Additional public regulatory or policy requirements.
    license_path : str, default="LICENSE"
        Repository path containing the complete human-readable terms.

    Returns
    -------
    str
        Markdown content to append to a legal documentation page.
    """
    lines = build_legal_lines(license_value, compatibility_notes, license_path)
    if not lines:
        lines = ["No project license has been selected yet."]

    requirements = regulatory_requirements or []
    if requirements or additional_regulatory_requirements:
        requirement_lines = [
            "## Regulatory and policy requirements",
            "",
            *(f"- {requirement}" for requirement in requirements),
        ]
        if additional_regulatory_requirements:
            if requirements:
                requirement_lines.append("")
            requirement_lines.append(additional_regulatory_requirements)
        lines.append("\n".join(requirement_lines))

    return "\n\n" + "\n\n".join(lines) + "\n"
