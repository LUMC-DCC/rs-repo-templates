"""Command registry for the suite adapter.

A suite groups several project commands behind one interface. Keeping command
registration here makes it clear which actions belong to the suite.
"""

from collections.abc import Callable

from {{ project_slug }}.services.processing import process_text


def process_command(text: str) -> str:
    """Run the suite's text-processing command.

    Parameters
    ----------
    text : str
        Text to process.

    Returns
    -------
    str
        Command output.
    """
    # Suite commands are thin wrappers around shared services, just like CLI
    # and API handlers.
    return process_text(text).output_text


def command_registry() -> dict[str, Callable[[str], str]]:
    """Return the suite command registry.

    Returns
    -------
    dict[str, collections.abc.Callable[[str], str]]
        Command names mapped to callables.
    """
    # Add new commands to this mapping when the suite gains another action.
    return {
        "process": process_command,
    }
