"""Input and output helpers for {{ (project_name or project_slug) }} workflows.

Small IO helpers keep file handling separate from processing logic. This makes
workflow steps easier to test because most steps can operate on Python objects
instead of reading from or writing to disk directly.
"""

from pathlib import Path


def read_text(path: Path) -> str:
    """Read a UTF-8 text file for use as workflow input.

    Parameters
    ----------
    path : pathlib.Path
        Path to the input text file.

    Returns
    -------
    str
        Text content without leading or trailing whitespace.
    """
    # UTF-8 is the safest default for research software because it preserves
    # non-ASCII names, labels, and metadata across operating systems.
    return path.read_text(encoding="utf-8").strip()


def write_text(path: Path, text: str) -> None:
    """Write UTF-8 text output from a workflow step.

    Parameters
    ----------
    path : pathlib.Path
        Path where the output text should be written.
    text : str
        Text content to write.
    """
    # Create parent directories here so workflow steps can focus on data
    # transformation and do not need to repeat filesystem setup code.
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")
