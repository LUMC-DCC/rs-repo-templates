"""Build and normalize documentation-type content."""

DOCUMENTATION_TYPES = {
    "user": {
        "label": "User guide",
        "path": "usage.md",
        "description": (
            "installation, configuration, usage instructions, and runnable examples"
        ),
        "optional": True,
    },
    "deployment": {
        "label": "Deployment notes",
        "path": "deployment.md",
        "description": (
            "environment setup, deployment steps, and operational assumptions"
        ),
        "optional": True,
    },
    "developer": {
        "label": "Developer guide",
        "path": "developer.md",
        "description": (
            "architecture, local development, tests, contribution workflow, and "
            "technical reference"
        ),
        "optional": True,
    },
}

DOCUMENTATION_TYPE_ALIASES = {
    "api documentation": "developer",
    "api docs": "developer",
    "api reference": "developer",
    "deployment documentation": "deployment",
    "deployment docs": "deployment",
    "developer documentation": "developer",
    "developer docs": "developer",
    "developer guide": "developer",
    "dev": "developer",
    "reference docs": "developer",
    "user documentation": "user",
    "user docs": "user",
    "user guide": "user",
}


def normalize_documentation_type(value):
    """Normalize one documentation type label.

    Parameters
    ----------
    value : str
        Documentation type from rendered context.

    Returns
    -------
    str
        Canonical documentation type, or an empty string when unsupported.
    """
    normalized = value.strip().lower().replace("_", " ").replace("-", " ")
    normalized = " ".join(normalized.split())
    normalized = DOCUMENTATION_TYPE_ALIASES.get(normalized, normalized)
    if normalized in DOCUMENTATION_TYPES:
        return normalized
    return ""


def selected_documentation_types(entries):
    """Return selected documentation types in stable order.

    Parameters
    ----------
    entries : list[str]
        Documentation type entries from rendered context.

    Returns
    -------
    list[str]
        Canonical documentation type names.
    """
    selected = []
    for entry in entries:
        doc_type = normalize_documentation_type(entry)
        if doc_type and doc_type not in selected:
            selected.append(doc_type)
    return selected


def selected_optional_documentation_paths(entries):
    """Return optional documentation paths to keep.

    Parameters
    ----------
    entries : list[str]
        Documentation type entries from rendered context.

    Returns
    -------
    set[str]
        Optional documentation paths selected by context.
    """
    selected = selected_documentation_types(entries)
    paths = {
        DOCUMENTATION_TYPES[doc_type]["path"]
        for doc_type in selected
        if DOCUMENTATION_TYPES[doc_type]["optional"]
    }
    if "developer" in selected:
        paths.add("reference.md")
    return paths


def optional_documentation_paths():
    """Return all optional documentation paths.

    Returns
    -------
    set[str]
        Optional documentation paths controlled by ``documentation_types``.
    """
    paths = {
        details["path"]
        for details in DOCUMENTATION_TYPES.values()
        if details["optional"]
    }
    paths.add("reference.md")
    return paths


def build_readme_documentation_section(entries):
    """Build the generated README documentation overview section.

    Parameters
    ----------
    entries : list[str]
        Documentation type entries from rendered context.

    Returns
    -------
    str
        Markdown section, or an empty string when no types are selected.
    """
    selected = selected_documentation_types(entries)
    if not selected:
        return ""

    lines = ["Documentation source files are in `docs/`.", "", "Expected content:"]
    for doc_type in selected:
        details = DOCUMENTATION_TYPES[doc_type]
        lines.append(f"- {details['label']}: {details['description']}.")

    return "## Documentation\n\n" + "\n".join(lines)
