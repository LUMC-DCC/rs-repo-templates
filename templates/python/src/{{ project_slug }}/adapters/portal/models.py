"""Portal data models for {{ (project_name or project_slug) }}.

Models describe the structured records shown by the portal. They are kept
separate from routes and views so portal data can come from files, databases, or
APIs later.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PortalRecord:
    """Record displayed by the portal.

    Parameters
    ----------
    identifier : str
        Stable record identifier.
    label : str
        Human-readable label.
    description : str
        Short record description.
    """

    identifier: str
    label: str
    description: str
