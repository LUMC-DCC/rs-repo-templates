"""Render public interoperability summaries for generated documentation."""

from renderers.project_context.terms import (
    format_edam_term_label,
    format_function_io_label,
)


def format_programming_language_label(programming_language):
    """Format one public programming language record.

    Parameters
    ----------
    programming_language : dict
        Programming language record from the rendered Cookiecutter context.

    Returns
    -------
    str
        Human-readable programming language label.
    """
    name = programming_language.get("name", "")
    version_constraint = programming_language.get("version_constraint", "")
    role = programming_language.get("role", "")

    if not name:
        return ""

    label = name
    if version_constraint:
        label = f"{label} {version_constraint}"
    if role:
        label = f"{label} - {role}"

    return label


def format_software_function_label(software_function):
    """Format one public software function record.

    Parameters
    ----------
    software_function : dict
        Software-function record from the rendered Cookiecutter context.

    Returns
    -------
    str
        Human-readable software-function label.
    """
    operations = software_function.get("operation", [])
    inputs = software_function.get("input", [])
    outputs = software_function.get("output", [])
    command = software_function.get("cmd", "")
    note = software_function.get("note", "")

    if not any((operations, inputs, outputs, command, note)):
        return ""

    operation_labels = [
        label
        for operation in operations
        if (label := format_edam_term_label(operation))
    ]
    input_labels = [
        label
        for input_record in inputs
        if (label := format_function_io_label(input_record))
    ]
    output_labels = [
        label
        for output_record in outputs
        if (label := format_function_io_label(output_record))
    ]

    label = ", ".join(operation_labels) or "Function"
    details = []
    if input_labels:
        details.append(f"input: {', '.join(input_labels)}")
    if output_labels:
        details.append(f"output: {', '.join(output_labels)}")
    if command:
        details.append(f"command: `{command}`")
    if note:
        details.append(note)
    if details:
        label = f"{label} - {'; '.join(details)}"

    return label


def build_programming_languages_section(programming_language_entries):
    """Build the generated programming languages section.

    Parameters
    ----------
    programming_language_entries : list[dict]
        Programming language records from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    language_lines = [
        f"- {label}"
        for programming_language in programming_language_entries
        if (label := format_programming_language_label(programming_language))
    ]
    if not language_lines:
        return ""

    return "## Programming languages\n\n" + "\n".join(language_lines)


def format_operating_system_label(operating_system):
    """Format one public operating-system support record.

    Parameters
    ----------
    operating_system : dict
        Operating-system record from the rendered Cookiecutter context.

    Returns
    -------
    str
        Human-readable operating-system support label.
    """
    name = operating_system.get("name", "")
    specification = operating_system.get("specification", "")
    status = operating_system.get("status", "")

    if not name:
        return ""

    label = name
    if specification:
        label = f"{label} {specification}"
    if status:
        label = f"{label} - {status}"

    return label


def build_operating_systems_section(operating_system_entries):
    """Build the generated platform support section.

    Parameters
    ----------
    operating_system_entries : list[dict]
        Operating-system records from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    operating_system_lines = [
        f"- {label}"
        for operating_system in operating_system_entries
        if (label := format_operating_system_label(operating_system))
    ]
    if not operating_system_lines:
        return ""

    return "## Platform support\n\n" + "\n".join(operating_system_lines)


def format_external_dependency_label(external_dependency):
    """Format one public external-dependency record.

    Parameters
    ----------
    external_dependency : dict
        External-dependency record from the rendered Cookiecutter context.

    Returns
    -------
    str
        Human-readable external-dependency label.
    """
    name = external_dependency.get("name", "")
    version_constraint = external_dependency.get("version_constraint", "")
    url = external_dependency.get("url", "")
    license_value = external_dependency.get("license", "")
    purpose = external_dependency.get("purpose", "")

    if not name:
        return ""

    label = name
    if version_constraint:
        label = f"{label} {version_constraint}"
    if url:
        label = f"[{label}]({url})"

    details = []
    if purpose:
        details.append(purpose)
    if license_value:
        details.append(f"license: {license_value}")
    if details:
        label = f"{label} - {'; '.join(details)}"

    return label


def build_external_dependencies_section(external_dependency_entries):
    """Build the generated external dependencies section.

    Parameters
    ----------
    external_dependency_entries : list[dict]
        External-dependency records from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    dependency_lines = [
        f"- {label}"
        for external_dependency in external_dependency_entries
        if (label := format_external_dependency_label(external_dependency))
    ]
    if not dependency_lines:
        return ""

    return "## External dependencies\n\n" + "\n".join(dependency_lines)


def format_external_service_label(external_service):
    """Format one public external-service record.

    Parameters
    ----------
    external_service : dict
        External-service record from the rendered Cookiecutter context.

    Returns
    -------
    str
        Human-readable external-service label.
    """
    name = external_service.get("name", "")
    provider = external_service.get("provider", "")
    service_types = external_service.get("service_types", [])
    quantity = external_service.get("quantity", "")
    cost_coverage = external_service.get("cost_coverage", [])

    if not name:
        return ""

    details = []
    if provider:
        details.append(f"provider: {provider}")
    if service_types:
        details.append(f"type: {', '.join(service_types)}")
    if quantity:
        details.append(f"quantity: {quantity}")
    if cost_coverage:
        details.append(f"cost coverage: {', '.join(cost_coverage)}")
    if details:
        return f"{name} - {'; '.join(details)}"

    return name


def build_external_services_section(external_service_entries):
    """Build the generated external services section.

    Parameters
    ----------
    external_service_entries : list[dict]
        External-service records from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    service_lines = [
        f"- {label}"
        for external_service in external_service_entries
        if (label := format_external_service_label(external_service))
    ]
    if not service_lines:
        return ""

    return "## External services\n\n" + "\n".join(service_lines)


def build_software_functions_section(software_function_entries):
    """Build the generated functions and operations section.

    Parameters
    ----------
    software_function_entries : list[dict]
        Software-function records from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    function_lines = [
        f"- {label}"
        for software_function in software_function_entries
        if (label := format_software_function_label(software_function))
    ]
    if not function_lines:
        return ""

    return "## Functions and operations\n\n" + "\n".join(function_lines)


def build_function_details(software_function):
    """Build readable details for one software function.

    Parameters
    ----------
    software_function : dict
        Software-function record from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    label = ", ".join(
        operation.get("term", "")
        for operation in software_function.get("operation", [])
        if operation.get("term")
    )
    if not label:
        label = "Software function"

    sections = [f"## {label}"]

    operations = [
        format_edam_term_label(operation)
        for operation in software_function.get("operation", [])
        if format_edam_term_label(operation)
    ]
    if operations:
        sections.append(
            "**Operations**\n\n" + "\n".join(f"- {item}" for item in operations)
        )

    inputs = [
        format_function_io_label(input_record)
        for input_record in software_function.get("input", [])
        if format_function_io_label(input_record)
    ]
    if inputs:
        sections.append("**Inputs**\n\n" + "\n".join(f"- {item}" for item in inputs))

    outputs = [
        format_function_io_label(output_record)
        for output_record in software_function.get("output", [])
        if format_function_io_label(output_record)
    ]
    if outputs:
        sections.append("**Outputs**\n\n" + "\n".join(f"- {item}" for item in outputs))

    if software_function.get("cmd"):
        sections.append(f"**Command**\n\n```bash\n{software_function['cmd']}\n```")

    if software_function.get("note"):
        sections.append("**Notes**\n\n" + software_function["note"])

    return "\n\n".join(sections)


def build_software_functions_page(software_function_entries):
    """Build a generated functions documentation page.

    Parameters
    ----------
    software_function_entries : list[dict]
        Software-function records from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown page content, or an empty string.
    """
    function_sections = [
        section
        for software_function in software_function_entries
        if (section := build_function_details(software_function))
    ]
    if not function_sections:
        return ""

    intro = (
        "# Functions and operations\n\n"
        "This page describes the public operations exposed by the software, "
        "including supported inputs, outputs, and command examples."
    )
    return intro + "\n\n" + "\n\n".join(function_sections) + "\n"


def build_user_functions_section(software_function_entries):
    """Build a user-facing functions section.

    Parameters
    ----------
    software_function_entries : list[dict]
        Software-function records from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    if not software_function_entries:
        return ""

    return (
        "## Available functions\n\n"
        "See [Functions and operations](functions.md) for supported operations, "
        "inputs, outputs, and command examples."
    )


def build_developer_functions_section(software_function_entries):
    """Build a developer-facing functions section.

    Parameters
    ----------
    software_function_entries : list[dict]
        Software-function records from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    if not software_function_entries:
        return ""

    return (
        "## Function metadata\n\n"
        "The public function descriptions in "
        "[Functions and operations](functions.md) should stay aligned with the "
        "implemented commands, accepted inputs, emitted outputs, and README "
        "`biotools-function` metadata blocks."
    )


def format_interface_label(interface):
    """Format one public interface record.

    Parameters
    ----------
    interface : dict
        Interface record from the rendered Cookiecutter context.

    Returns
    -------
    str
        Human-readable interface label.
    """
    interface_type = interface.get("type", "")
    specification = interface.get("specification", "")
    status = interface.get("status", "")

    if not any((interface_type, specification, status)):
        return ""

    label = interface_type or "Interface"
    if status:
        label = f"{label} ({status})"

    details = []
    if specification:
        details.append(specification)
    if details:
        label = f"{label} - {'; '.join(details)}"

    return label


def interface_type_values(interface_entries):
    """Return sorted public interface type values.

    Parameters
    ----------
    interface_entries : list[dict]
        Interface records from the rendered Cookiecutter context.

    Returns
    -------
    list[str]
        Sorted unique interface type values.
    """
    return sorted(
        {
            interface.get("type", "").strip()
            for interface in interface_entries
            if interface.get("type", "").strip()
        }
    )


def api_like_interface(interface):
    """Return whether an interface belongs in API documentation.

    Parameters
    ----------
    interface : dict
        Interface record from the rendered Cookiecutter context.

    Returns
    -------
    bool
        Whether the interface type or specification describes an API-like surface.
    """
    return interface.get("type", "") in {
        "SPARQL endpoint",
        "Web API",
        "Web service",
    }


def build_interfaces_list(interface_entries):
    """Build Markdown bullets for interface entries.

    Parameters
    ----------
    interface_entries : list[dict]
        Interface records from the rendered Cookiecutter context.

    Returns
    -------
    list[str]
        Markdown bullet lines.
    """
    return [
        f"- {label}"
        for interface in interface_entries
        if (label := format_interface_label(interface))
    ]


def build_interfaces_section(interface_entries):
    """Build the generated overview interfaces section.

    Parameters
    ----------
    interface_entries : list[dict]
        Interface records from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    interface_lines = build_interfaces_list(interface_entries)
    if not interface_lines:
        return ""

    return "## Interfaces\n\n" + "\n".join(interface_lines)


def build_user_interfaces_section(interface_entries):
    """Build a user-facing interfaces section.

    Parameters
    ----------
    interface_entries : list[dict]
        Interface records from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    interface_lines = build_interfaces_list(interface_entries)
    if not interface_lines:
        return ""

    return "## Access interfaces\n\n" + "\n".join(interface_lines)


def build_developer_interfaces_section(interface_entries):
    """Build a developer-facing interfaces section.

    Parameters
    ----------
    interface_entries : list[dict]
        Interface records from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    detailed_interfaces = [
        interface
        for interface in interface_entries
        if any(
            interface.get(field, "").strip()
            for field in ("specification", "url", "status")
        )
    ]
    if not detailed_interfaces:
        return ""

    interface_lines = build_interfaces_list(detailed_interfaces)
    if not interface_lines:
        return ""

    intro = (
        "## Interface contracts\n\n"
        "Keep public interface descriptions aligned with implementation files, "
        "documentation, and stability status.\n\n"
    )
    return intro + "\n".join(interface_lines)


def build_api_interfaces_section(interface_entries):
    """Build an API-page interfaces section.

    Parameters
    ----------
    interface_entries : list[dict]
        Interface records from the rendered Cookiecutter context.

    Returns
    -------
    str
        Markdown section, or an empty string.
    """
    api_interfaces = [
        interface for interface in interface_entries if api_like_interface(interface)
    ]
    interface_lines = build_interfaces_list(api_interfaces)
    if not interface_lines:
        return ""

    return "## API interfaces\n\n" + "\n".join(interface_lines)
