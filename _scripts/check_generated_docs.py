"""Render and build supported Python documentation scaffolds.

The check exercises the generated projects rather than only this repository's
documentation. Builds run in temporary directories and leave the workspace
unchanged.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from copier import run_copy

ROOT = Path(__file__).resolve().parent.parent
BUILD_COMMANDS = {
    "mkdocs": [sys.executable, "-m", "mkdocs", "build", "--strict"],
    "zensical": [sys.executable, "-m", "zensical", "build", "--strict"],
    "sphinx": [
        sys.executable,
        "-m",
        "sphinx",
        "-W",
        "-b",
        "html",
        "docs/source",
        "docs/build/html",
    ],
}


def render_project(builder: str, workspace: Path) -> Path:
    """Render one documented Python project.

    Parameters
    ----------
    builder : str
        Supported documentation builder name.
    workspace : pathlib.Path
        Temporary directory used for the generated project.

    Returns
    -------
    pathlib.Path
        Generated project root.
    """
    project_slug = f"generated_{builder}_docs"
    project_path = workspace / "output" / project_slug
    run_copy(
        str(ROOT),
        project_path,
        data={
            "template_type": "python",
            "project_name": f"Generated {builder.title()} Docs",
            "project_slug": project_slug,
            "project_short_description": ("Documentation build verification project."),
            "documentation_builder": builder,
            "documentation_types": {
                "entries": [
                    "user",
                    "deployment",
                    "developer",
                ]
            },
            "test_types": {"entries": []},
            "quality_tools": {
                "formatter": "",
                "linter": "",
                "type_checker": "",
            },
            "licensing": {"license": "", "compatibility_check": ""},
        },
        defaults=True,
        overwrite=True,
        quiet=True,
        unsafe=True,
    )
    return project_path


def build_documentation(builder: str) -> None:
    """Render and build one documentation variant.

    Parameters
    ----------
    builder : str
        Key from ``BUILD_COMMANDS``.

    Raises
    ------
    subprocess.CalledProcessError
        If the generated documentation does not build cleanly.
    """
    with tempfile.TemporaryDirectory(prefix=f"copier-{builder}-") as tmp_dir:
        project_path = render_project(builder, Path(tmp_dir))
        subprocess.run(BUILD_COMMANDS[builder], cwd=project_path, check=True)


def main() -> None:
    """Run the command-line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--builder",
        action="append",
        choices=sorted(BUILD_COMMANDS),
        dest="builders",
        help="Builder to check; repeat to select multiple builders.",
    )
    args = parser.parse_args()

    for builder in args.builders or sorted(BUILD_COMMANDS):
        print(f"[docs] Building generated {builder} documentation", flush=True)
        build_documentation(builder)


if __name__ == "__main__":
    main()
