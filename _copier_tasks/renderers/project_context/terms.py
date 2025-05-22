"""Render EDAM-like terms used in public interoperability sections."""


def format_edam_term_label(term_record):
    """Format one EDAM-like term record.

    Parameters
    ----------
    term_record : dict
        Term record with optional ``term`` and ``uri`` keys.

    Returns
    -------
    str
        Human-readable term label.
    """
    term = term_record.get("term", "")
    uri = term_record.get("uri", "")

    if term and uri:
        return f"[{term}]({uri})"
    return term or uri


def format_function_io_label(io_record):
    """Format one function input or output record.

    Parameters
    ----------
    io_record : dict
        Function input or output record.

    Returns
    -------
    str
        Human-readable input/output label.
    """
    data_label = format_edam_term_label(io_record.get("data", {}))
    format_labels = [
        label
        for format_record in io_record.get("format", [])
        if (label := format_data_format_label(format_record))
    ]

    if data_label and format_labels:
        return f"{data_label} ({', '.join(format_labels)})"
    if data_label:
        return data_label
    return ", ".join(format_labels)


def format_data_format_label(format_record):
    """Format one data-format record with its public constraints.

    Parameters
    ----------
    format_record : dict
        Format term with optional version, schema, and sample URL.

    Returns
    -------
    str
        Human-readable data-format label.
    """
    label = format_edam_term_label(format_record)
    if not label:
        return ""

    version_constraint = format_record.get("version_constraint", "")
    schema_constraints = format_record.get("schema_constraints", "")
    sample_url = format_record.get("sample_url", "")
    details = []
    if version_constraint:
        details.append(version_constraint)
    if schema_constraints:
        details.append(schema_constraints)
    if sample_url:
        details.append(f"[sample]({sample_url})")
    if details:
        label = f"{label} - {'; '.join(details)}"

    return label
