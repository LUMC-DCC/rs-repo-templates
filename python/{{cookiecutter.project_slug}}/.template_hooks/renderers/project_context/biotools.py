"""Render README bio.tools-compatible function metadata blocks."""

import json


def yaml_scalar(value):
    """Render a scalar as YAML-compatible JSON.

    Parameters
    ----------
    value : str
        Scalar value.

    Returns
    -------
    str
        Quoted scalar suitable for a YAML block.
    """
    return json.dumps(value)


def render_edam_term_yaml(term_record, indent):
    """Render one EDAM-like term record as YAML lines.

    Parameters
    ----------
    term_record : dict
        Term record with optional ``term`` and ``uri`` keys.
    indent : int
        Number of leading spaces.

    Returns
    -------
    list[str]
        YAML lines.
    """
    prefix = " " * indent
    lines = []
    if term_record.get("term"):
        lines.append(f"{prefix}term: {yaml_scalar(term_record['term'])}")
    if term_record.get("uri"):
        lines.append(f"{prefix}uri: {yaml_scalar(term_record['uri'])}")
    return lines


def render_term_list_yaml(key, term_records):
    """Render a YAML list of EDAM-like terms.

    Parameters
    ----------
    key : str
        YAML key.
    term_records : list[dict]
        Term records.

    Returns
    -------
    list[str]
        YAML lines.
    """
    if not term_records:
        return []

    lines = [f"{key}:"]
    for term_record in term_records:
        term_lines = render_edam_term_yaml(term_record, indent=2)
        if not term_lines:
            continue
        lines.append(f"- {term_lines[0].lstrip()}")
        lines.extend(term_lines[1:])
    return lines


def render_function_io_yaml(key, io_records):
    """Render function input or output records as YAML lines.

    Parameters
    ----------
    key : str
        YAML key, usually ``input`` or ``output``.
    io_records : list[dict]
        Function input or output records.

    Returns
    -------
    list[str]
        YAML lines.
    """
    if not io_records:
        return []

    lines = [f"{key}:"]
    for io_record in io_records:
        data_lines = render_edam_term_yaml(io_record.get("data", {}), indent=4)
        format_lines = render_term_list_yaml("format", io_record.get("format", []))

        if data_lines:
            lines.append("- data:")
            lines.extend(data_lines)
        else:
            lines.append("- data: {}")

        if format_lines:
            lines.append("  format:")
            for line in format_lines[1:]:
                lines.append(f"  {line}")
    return lines


def render_cmd_yaml(command):
    """Render a command field as YAML lines.

    Parameters
    ----------
    command : str
        Command or command block.

    Returns
    -------
    list[str]
        YAML lines.
    """
    if not command:
        return []
    if "\n" not in command:
        return [f"cmd: {yaml_scalar(command)}"]

    lines = ["cmd: |-"]
    lines.extend(f"  {line}" if line else "" for line in command.splitlines())
    return lines


def software_function_label(software_function):
    """Return a short display label for one software function.

    Parameters
    ----------
    software_function : dict
        Software-function record.

    Returns
    -------
    str
        Label for a details block.
    """
    operations = [
        operation.get("term", "")
        for operation in software_function.get("operations", [])
        if operation.get("term")
    ]
    if operations:
        return ", ".join(operations)

    return "Software function"


def build_biotools_function_block(software_function):
    """Build one README bio.tools-compatible function block.

    Parameters
    ----------
    software_function : dict
        Software-function record.

    Returns
    -------
    str
        Markdown details block, or an empty string.
    """
    yaml_lines = ["# biotools-function"]
    yaml_lines.extend(
        render_term_list_yaml("operation", software_function.get("operations", []))
    )
    yaml_lines.extend(
        render_function_io_yaml("input", software_function.get("inputs", []))
    )
    yaml_lines.extend(
        render_function_io_yaml("output", software_function.get("outputs", []))
    )
    yaml_lines.extend(render_cmd_yaml(software_function.get("cmd", "")))
    if software_function.get("note"):
        yaml_lines.append(f"note: {yaml_scalar(software_function['note'])}")

    if len(yaml_lines) == 1:
        return ""

    label = software_function_label(software_function)
    yaml_block = "\n".join(yaml_lines)
    return (
        f"<details>\n<summary>{label}</summary>\n\n"
        f"```yaml\n{yaml_block}\n```\n\n</details>"
    )


def build_biotools_function_blocks(software_function_entries):
    """Build README bio.tools-compatible function blocks.

    Parameters
    ----------
    software_function_entries : list[dict]
        Software-function records.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    blocks = [
        block
        for software_function in software_function_entries
        if (block := build_biotools_function_block(software_function))
    ]
    if not blocks:
        return ""

    return "## Functions\n\n" + "\n\n".join(blocks)
