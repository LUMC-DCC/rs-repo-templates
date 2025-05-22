"""Plug-in hook contracts for {{ (project_name or project_slug) }}.

Protocols describe the methods external plug-ins must provide. They let type
checkers and tests validate plug-in compatibility without requiring inheritance
from a project-specific base class.
"""

from typing import Protocol


class TextProcessorPlugin(Protocol):
    """Contract implemented by text-processing plug-ins."""

    # Use a stable name so plug-ins can be listed in logs, configuration, or UI.
    name: str

    def process(self, text: str) -> str:
        """Process text through the plug-in.

        Parameters
        ----------
        text : str
            Text to process.

        Returns
        -------
        str
            Processed text.
        """
