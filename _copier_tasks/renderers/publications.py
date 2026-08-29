"""Build public notes for associated project publications."""


def publication_url(publication):
    """Resolve one publication to a stable public URL when possible.

    Parameters
    ----------
    publication : dict
        Publication record from the normalized Copier context.

    Returns
    -------
    str
        Public publication URL, or an empty string when it cannot be derived.
    """
    doi = publication.get("doi", "")
    if doi:
        if doi.startswith(("http://", "https://")):
            return doi
        return f"https://doi.org/{doi}"

    url = publication.get("url", "")
    if url:
        return url

    pmcid = publication.get("pmcid", "")
    if pmcid:
        return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/"

    pmid = publication.get("pmid", "")
    if pmid:
        return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

    return ""


def publication_label(publication):
    """Build one compact publication label.

    Parameters
    ----------
    publication : dict
        Publication record from the normalized Copier context.

    Returns
    -------
    str
        Human-readable publication label.
    """
    if publication.get("title"):
        return publication["title"]
    if publication.get("citation"):
        return publication["citation"]
    if publication.get("doi"):
        return f"DOI {publication['doi']}"
    if publication.get("pmid"):
        return f"PMID {publication['pmid']}"
    if publication.get("pmcid"):
        return publication["pmcid"]
    if publication.get("url"):
        return publication["url"]

    return "Associated publication"


def select_primary_publication(publication_entries):
    """Select the publication to show in concise public notes.

    Parameters
    ----------
    publication_entries : list[dict]
        Publication records from the normalized Copier context.

    Returns
    -------
    dict
        Preferred publication, first populated publication, or an empty dict.
    """
    populated_publications = [
        publication
        for publication in publication_entries
        if any(
            publication.get(key)
            for key in ("title", "citation", "doi", "url", "pmid", "pmcid")
        )
    ]
    if not populated_publications:
        return {}

    for publication in populated_publications:
        if publication.get("preferred"):
            return publication

    return populated_publications[0]


def build_publication_note(publication_entries):
    """Build a compact associated publication note.

    Parameters
    ----------
    publication_entries : list[dict]
        Publication records from the normalized Copier context.

    Returns
    -------
    str
        One-line Markdown publication note, or an empty string.
    """
    publication = select_primary_publication(publication_entries)
    if not publication:
        return ""

    label = publication_label(publication)
    url = publication_url(publication)
    if url:
        return f"Publication: [{label}]({url})"

    return f"Publication: {label}"
