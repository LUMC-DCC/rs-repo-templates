"""Render and build documentation scaffolds for supported templates.

The check exercises generated projects rather than only this repository's
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
SUPPORTED_BUILDERS = {
    "generic": ("mkdocs", "sphinx", "zensical"),
    "python": ("mkdocs", "sphinx", "zensical"),
    "r": ("pkgdown",),
}
SUPPORTED_TEMPLATES = tuple(SUPPORTED_BUILDERS)
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
    "pkgdown": [
        "Rscript",
        "-e",
        "pkgdown::build_site()",
    ],
}


def render_project(template_type: str, builder: str, workspace: Path) -> Path:
    """Render one documented project.

    Parameters
    ----------
    template_type
        Repository scaffold to render.
    builder
        Supported documentation builder name.
    workspace
        Temporary directory used for the generated project.

    Returns
    -------
    pathlib.Path
        Generated project root.
    """
    separators = {"generic": "-", "python": "_", "r": "."}
    separator = separators[template_type]
    project_slug = separator.join(("generated", builder, "docs"))
    project_path = workspace / "output" / project_slug
    data = {
        "template_type": template_type,
        "project_name": f"Generated {builder.title()} Docs",
        "project_slug": project_slug,
        "project_short_description": "Documentation build verification project.",
        "urls": {
            "repository": f"https://github.com/example/{project_slug}",
            "homepage": "",
            "documentation": f"https://example.org/{project_slug}/docs",
        },
        "documentation_builder": builder,
        "documentation_types": {
            "entries": [
                "user",
                "deployment",
                "developer",
            ]
        },
        "licensing": {"license": "", "compatibility_check": ""},
    }
    if template_type == "python":
        data.update(
            {
                "test_types": {"entries": []},
                "quality_tools": {
                    "formatter": "",
                    "linter": "",
                    "type_checker": "",
                },
            }
        )
    elif template_type == "r":
        data.update(
            {
                "test_types": {"entries": []},
                "quality_tools": {
                    "formatter": "",
                    "linter": "",
                    "type_checker": "",
                },
                "programming_languages": {
                    "entries": [{"name": "R", "version_constraint": ">= 4.3"}]
                },
            }
        )

    run_copy(
        str(ROOT),
        project_path,
        data=data,
        defaults=True,
        overwrite=True,
        quiet=True,
        unsafe=True,
    )
    return project_path


def build_documentation(template_type: str, builder: str) -> None:
    """Render and build one documentation variant.

    Parameters
    ----------
    template_type
        Repository scaffold to render.
    builder
        Key from BUILD_COMMANDS.

    Raises
    ------
    subprocess.CalledProcessError
        If the generated documentation does not build cleanly.
    """
    prefix = f"copier-{template_type}-{builder}-"
    with tempfile.TemporaryDirectory(prefix=prefix) as tmp_dir:
        project_path = render_project(template_type, builder, Path(tmp_dir))
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
    parser.add_argument(
        "--template",
        action="append",
        choices=SUPPORTED_TEMPLATES,
        dest="templates",
        help="Template to check; repeat to select multiple templates.",
    )
    args = parser.parse_args()

    templates = args.templates or SUPPORTED_TEMPLATES
    for template_type in templates:
        builders = args.builders or SUPPORTED_BUILDERS[template_type]
        for builder in builders:
            if builder not in SUPPORTED_BUILDERS[template_type]:
                parser.error(
                    f"{builder!r} is not supported by the {template_type!r} template"
                )
            print(
                f"[docs] Building {template_type} {builder} documentation",
                flush=True,
            )
            build_documentation(template_type, builder)


if __name__ == "__main__":
    main()
