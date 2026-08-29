"""Desktop application entry logic for {{ (project_name or project_slug) }}.

The desktop adapter builds a small graphical interface around project service
logic. GUI code is kept separate from the view model so display text can be
tested without opening a window.
"""

import tkinter as tk

{% set interface_types = namespace(values=[]) %}
{% for interface in interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set has_http_interface = "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values or "Web service" in interface_types.values or "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values or "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set configuration_security_measures = ["Secrets management (e.g., environment variables, vault)", "Secure configuration management (e.g., Infrastructure-as-Code, hardening)"] %}
{% set has_runtime_configuration = has_http_interface or security_measures.selected.entries | select("in", configuration_security_measures) | list | length > 0 %}
from {{ project_slug }}.adapters.desktop.view_model import build_view_model
{% if has_runtime_configuration %}
from {{ project_slug }}.logging_config import configure_logging
{% endif %}


def create_window(text: str = "{{ (project_name or project_slug) }}") -> tk.Tk:
    """Create the desktop application window.

    Parameters
    ----------
    text : str, default="{{ (project_name or project_slug) }}"
        Text to process.

    Returns
    -------
    tkinter.Tk
        Configured desktop window.
    """
    # The view model prepares text for the UI. Keeping that separate avoids
    # mixing project logic with toolkit-specific widgets.
    view_model = build_view_model(text)
    root = tk.Tk()
    root.title(view_model.title)

    # Tkinter is from the Python standard library, so this starter desktop app
    # does not add an extra GUI dependency.
    frame = tk.Frame(root, padx=24, pady=24)
    frame.pack(fill="both", expand=True)

    title = tk.Label(frame, text=view_model.title, font=("TkDefaultFont", 16, "bold"))
    title.pack(anchor="w")

    message = tk.Label(frame, text=view_model.message)
    message.pack(anchor="w", pady=(12, 0))

    return root


def main() -> None:
    """Run the desktop application event loop."""
{% if has_runtime_configuration %}
    configure_logging()
{% endif %}
    create_window().mainloop()


if __name__ == "__main__":
    main()
