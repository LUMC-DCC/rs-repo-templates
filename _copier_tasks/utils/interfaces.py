"""Classify public interface entries from the rendered context."""

from utils.context import entries

API_INTERFACE_TYPES = {
    "SPARQL endpoint",
    "Web API",
}
PROCESSING_API_INTERFACE_TYPES = {
    "Web API",
}
SOAP_INTERFACE_TYPES = {
    "Web service",
}
CLI_INTERFACE_TYPES = {
    "Command-line tool",
}
DESKTOP_INTERFACE_TYPES = {
    "Desktop application",
}
ONTOLOGY_INTERFACE_TYPES = {
    "Ontology",
}
PLUGIN_INTERFACE_TYPES = {
    "Plug-in",
}
PORTAL_INTERFACE_TYPES = {
    "Bioinformatics portal",
    "Database portal",
}
SCRIPT_INTERFACE_TYPES = {
    "Script",
}
SUITE_INTERFACE_TYPES = {
    "Suite",
}
WEB_INTERFACE_TYPES = {
    "Bioinformatics portal",
    "Database portal",
    "Web application",
    "Workbench",
}
HTTP_INTERFACE_TYPES = API_INTERFACE_TYPES | SOAP_INTERFACE_TYPES | WEB_INTERFACE_TYPES
WORKFLOW_INTERFACE_TYPES = {
    "Workflow",
}


def interface_text(interface):
    """Return searchable text for one interface entry.

    Parameters
    ----------
    interface : dict
        Interface record from the normalized Copier context.

    Returns
    -------
    str
        Lowercase text assembled from public interface fields.
    """
    return " ".join(
        [
            interface.get("type", ""),
            interface.get("specification", ""),
            interface.get("url", ""),
        ]
    ).lower()


def interface_types(ctx):
    """Return declared interface type values.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    set[str]
        Canonical interface type values.
    """
    return {
        interface.get("type", "")
        for interface in entries(ctx, "interfaces")
        if interface.get("type", "")
    }


def has_interface_type(ctx, supported_types):
    """Return whether any declared interface type is supported.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    supported_types : set[str]
        Canonical interface types to match.

    Returns
    -------
    bool
        Whether any matching interface type exists.
    """
    return bool(interface_types(ctx) & supported_types)


def has_api_interface(ctx):
    """Return whether the context declares an API-like interface.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether an API-like interface exists.
    """
    return has_interface_type(ctx, API_INTERFACE_TYPES)


def has_processing_api_interface(ctx):
    """Return whether the context declares a process-style API interface.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a process-style API interface exists.
    """
    return has_interface_type(ctx, PROCESSING_API_INTERFACE_TYPES)


def has_soap_interface(ctx):
    """Return whether the context declares a SOAP web service.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a machine-described SOAP service exists.
    """
    return has_interface_type(ctx, SOAP_INTERFACE_TYPES)


def has_http_interface(ctx):
    """Return whether the project exposes any HTTP-facing application.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether an ASGI or WSGI web surface exists.
    """
    return has_interface_type(ctx, HTTP_INTERFACE_TYPES)


def has_sparql_interface(ctx):
    """Return whether the context declares a SPARQL endpoint.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a SPARQL endpoint exists.
    """
    return has_interface_type(ctx, {"SPARQL endpoint"})


def has_cli_interface(ctx):
    """Return whether the context declares a command-line interface.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a command-line interface exists.
    """
    return has_interface_type(ctx, CLI_INTERFACE_TYPES)


def has_desktop_interface(ctx):
    """Return whether the context declares a desktop application.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a desktop application exists.
    """
    return has_interface_type(ctx, DESKTOP_INTERFACE_TYPES)


def has_ontology_interface(ctx):
    """Return whether the context declares an ontology interface.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether an ontology interface exists.
    """
    return has_interface_type(ctx, ONTOLOGY_INTERFACE_TYPES)


def has_plugin_interface(ctx):
    """Return whether the context declares a plug-in interface.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a plug-in interface exists.
    """
    return has_interface_type(ctx, PLUGIN_INTERFACE_TYPES)


def has_portal_interface(ctx):
    """Return whether the context declares a portal interface.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a portal interface exists.
    """
    return has_interface_type(ctx, PORTAL_INTERFACE_TYPES)


def has_script_interface(ctx):
    """Return whether the context declares a script interface.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a script interface exists.
    """
    return has_interface_type(ctx, SCRIPT_INTERFACE_TYPES)


def has_suite_interface(ctx):
    """Return whether the context declares a suite interface.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a suite interface exists.
    """
    return has_interface_type(ctx, SUITE_INTERFACE_TYPES)


def has_web_interface(ctx):
    """Return whether the context declares a web-facing application.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a web-facing application exists.
    """
    return has_interface_type(ctx, WEB_INTERFACE_TYPES)


def has_workflow_interface(ctx):
    """Return whether the context declares a workflow interface.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    bool
        Whether a workflow interface exists.
    """
    return has_interface_type(ctx, WORKFLOW_INTERFACE_TYPES)
