"""Plug-in registration for {{ (project_name or project_slug) }}.

This module exposes the package-provided plug-in through the entry point
declared in ``pyproject.toml``. External applications can load the entry point
without importing internal project modules directly.
"""

from dataclasses import dataclass

from {{ project_slug }}.services.processing import process_text


@dataclass(frozen=True)
class ExamplePlugin:
    """Package-provided text-processing plug-in."""

    # The plug-in name is namespaced with the package slug to avoid collisions
    # when multiple projects are installed in the same environment.
    name: str = "{{ project_slug }}.example"

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
        # Plug-ins should delegate to services so extension behavior uses the
        # same project logic as the built-in implementation.
        return process_text(text).output_text


def get_plugin() -> ExamplePlugin:
    """Return the package-provided plug-in.

    Returns
    -------
    ExamplePlugin
        Plug-in instance.
    """
    return ExamplePlugin()
