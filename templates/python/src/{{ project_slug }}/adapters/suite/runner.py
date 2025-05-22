"""Suite command runner for {{ (project_name or project_slug) }}.

The runner provides a small public API for listing and executing suite
commands. It keeps lookup and error handling separate from individual command
implementations.
"""

from {{ project_slug }}.adapters.suite.commands import command_registry


def suite_commands() -> dict[str, str]:
    """Return suite command names and one-line descriptions.

    Returns
    -------
    dict[str, str]
        Command names mapped to short descriptions.
    """
    # Command docstrings provide compact descriptions without a second metadata
    # table to keep in sync.
    return {
        name: command.__doc__.splitlines()[0]
        for name, command in command_registry().items()
    }


def run_suite_command(name: str, text: str) -> str:
    """Run one suite command by name.

    Parameters
    ----------
    name : str
        Command name.
    text : str
        Text to process.

    Returns
    -------
    str
        Command output.

    Raises
    ------
    ValueError
        If the command is unknown.
    """
    registry = command_registry()
    if name not in registry:
        raise ValueError(f"Unknown suite command: {name}")
    # Commands all share the same simple callable shape in this starter suite:
    # one text input, one text output.
    return registry[name](text)
