"""Remove community files that were not selected."""

from renderers.community_files import all_community_files, selected_community_files
from utils.paths import remove_path


def select_community_files(ctx, cwd):
    """Remove unselected community files from the generated project.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    selected_paths = selected_community_files(ctx)
    for rel_path in all_community_files() - selected_paths:
        remove_path(cwd / rel_path)
