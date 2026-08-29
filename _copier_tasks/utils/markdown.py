"""Update generated Markdown files from Copier finalization tasks."""


def append_sections(path, sections):
    """Append generated sections to a Markdown file.

    Parameters
    ----------
    path : pathlib.Path
        Markdown file to update.
    sections : str
        Generated Markdown sections.
    """
    if sections and path.exists():
        existing = path.read_text(encoding="utf-8").rstrip()
        addition = sections.strip()
        path.write_text(f"{existing}\n\n{addition}\n", encoding="utf-8")


def insert_before_first_marker(path, text, markers):
    """Insert text before the first matching Markdown marker.

    Parameters
    ----------
    path : pathlib.Path
        Markdown file to update.
    text : str
        Markdown text to insert.
    markers : tuple[str, ...]
        Line prefixes that mark the insertion point.
    """
    if not text or not path.exists():
        return

    lines = path.read_text(encoding="utf-8").splitlines()
    insert_at = len(lines)
    for index, line in enumerate(lines):
        if line.startswith(markers):
            insert_at = index
            break

    prefix = "\n".join(lines[:insert_at]).rstrip()
    suffix = "\n".join(lines[insert_at:]).lstrip("\n")
    content = f"{prefix}\n\n{text}\n\n{suffix}\n" if suffix else f"{prefix}\n\n{text}\n"

    path.write_text(content, encoding="utf-8")
