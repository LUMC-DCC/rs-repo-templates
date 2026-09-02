"""Classify distribution channels used by generated release tooling."""

PYTHON_DISTRIBUTION_CHANNELS = {
    "conda-forge",
    "github release",
    "github releases",
    "pypi",
}

R_DISTRIBUTION_CHANNELS = {
    "bioconductor",
    "cran",
    "github release",
    "github releases",
}


def normalize_distribution_channel(value):
    """Normalize one distribution channel.

    Parameters
    ----------
    value : object
        Raw distribution channel value.

    Returns
    -------
    str
        Lowercase channel with normalized whitespace.
    """
    return " ".join(str(value or "").strip().lower().split())


def has_python_distribution(entries):
    """Return whether Python distribution artifacts should be built.

    Parameters
    ----------
    entries : list[str]
        Distribution channels from rendered context.

    Returns
    -------
    bool
        Whether a supported Python package channel is selected.
    """
    return any(
        normalize_distribution_channel(entry) in PYTHON_DISTRIBUTION_CHANNELS
        for entry in entries
    )


def has_r_distribution(entries):
    """Return whether R source-package distribution should be built.

    Parameters
    ----------
    entries : list[str]
        Distribution channels from rendered context.

    Returns
    -------
    bool
        Whether a supported R package channel is selected.
    """
    return any(
        normalize_distribution_channel(entry) in R_DISTRIBUTION_CHANNELS
        for entry in entries
    )
