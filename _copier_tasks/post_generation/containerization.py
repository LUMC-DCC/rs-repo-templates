"""Select generated container recipe files."""

import shutil

from utils.containerization import has_container_type
from utils.context import entries
from utils.paths import remove_path


def select_container_recipes(ctx, cwd):
    """Keep and name recipes selected by the project context.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    container_entries = entries(ctx, "containerization")
    containerfile = cwd / "Containerfile"

    if has_container_type(container_entries, "docker") and containerfile.exists():
        shutil.copy2(containerfile, cwd / "Dockerfile")

    if not has_container_type(container_entries, "oci"):
        remove_path(containerfile)
