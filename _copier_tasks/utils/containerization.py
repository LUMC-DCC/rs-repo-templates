"""Normalize container and environment specification selections."""

CONTAINER_TYPE_ALIASES = {
    "docker": "docker",
    "dockerfile": "docker",
    "oci": "oci",
    "oci podman": "oci",
    "podman": "oci",
    "containerfile": "oci",
    "apptainer": "apptainer",
    "apptainer singularity": "apptainer",
    "singularity": "apptainer",
    "other": "other",
}


def normalize_container_type(value):
    """Normalize one containerization type.

    Parameters
    ----------
    value : object
        Raw type value from a containerization entry.

    Returns
    -------
    str
        Canonical type used by generated-file selectors.
    """
    normalized = str(value or "").strip().lower()
    for token in ("_", "-", "/"):
        normalized = normalized.replace(token, " ")
    normalized = " ".join(normalized.split())
    return CONTAINER_TYPE_ALIASES.get(normalized, "")


def selected_container_types(entries):
    """Return canonical types selected by structured entries.

    Parameters
    ----------
    entries : list[dict]
        Containerization records from rendered context.

    Returns
    -------
    set[str]
        Canonical selected types.
    """
    return {
        normalized
        for entry in entries
        if isinstance(entry, dict)
        if (normalized := normalize_container_type(entry.get("type")))
    }


def has_container_type(entries, container_type):
    """Return whether one canonical container type is selected.

    Parameters
    ----------
    entries : list[dict]
        Containerization records from rendered context.
    container_type : str
        Canonical type to find.

    Returns
    -------
    bool
        Whether the requested type is selected.
    """
    return container_type in selected_container_types(entries)


def has_container_recipe(entries):
    """Return whether at least one executable container recipe is selected.

    Parameters
    ----------
    entries : list[dict]
        Containerization records from rendered context.

    Returns
    -------
    bool
        Whether Docker, OCI, or Apptainer recipe generation is selected.
    """
    return bool(selected_container_types(entries) & {"docker", "oci", "apptainer"})
