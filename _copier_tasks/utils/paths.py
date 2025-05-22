"""Filesystem helpers for Copier finalization tasks."""

import os
import shutil


def remove_path(path):
    """Remove a generated path when it exists.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to remove.
    """
    if not os.path.exists(path):
        return

    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)
