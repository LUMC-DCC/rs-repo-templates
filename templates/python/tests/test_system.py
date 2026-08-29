"""System-level tests for the generated package entry point."""

import subprocess
import sys


def test_module_entry_point_runs_end_to_end():
    """Ensure ``python -m`` runs through the package entry point."""
    result = subprocess.run(
        [sys.executable, "-m", "{{ project_slug }}"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "{{ (project_name or project_slug) | upper }}" in result.stdout
