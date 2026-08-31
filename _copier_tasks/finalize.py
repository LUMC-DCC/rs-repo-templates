"""Finalize a Copier-generated research software repository.

The entry point keeps orchestration small and delegates domain-specific work
to the modules in this package. It is executed from the versioned template
checkout and is never copied into generated repositories.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))


def finalize(project_root: Path, template_type: str) -> None:
    """Apply capability selection and render reusable repository files.

    Parameters
    ----------
    project_root
        Root of the generated or updated repository.
    template_type
        Selected language scaffold.

    Raises
    ------
    RuntimeError
        If the trusted generator environment lacks required packages.
    """
    try:
        from context import load_context
        from post_generation.community_files import select_community_files
        from post_generation.containerization import select_container_recipes
        from post_generation.documentation import select_documentation_builder
        from post_generation.license_integration import update_license_integrations
        from post_generation.optional_files import remove_optional_paths
        from post_generation.project_management import configure_project_manager
        from post_generation.public_files import update_public_context
        from post_generation.python_runtime import configure_python_runtime
        from post_generation.quality import select_quality_tools
        from post_generation.repository_files import render_repository_files
        from post_generation.testing import select_test_framework
        from post_generation.validation import validate_context
    except ModuleNotFoundError as error:
        if error.name not in {"rsm_schema", "rs_files_templates"}:
            raise
        message = (
            "The Copier environment is missing a generator dependency. Install "
            "this repository's pinned rsm-schema and rs-files-templates "
            "dependencies before generating or updating a project."
        )
        raise RuntimeError(message) from error

    ctx = load_context(project_root, template_type)

    validate_context(ctx)
    select_documentation_builder(ctx, project_root)
    select_container_recipes(ctx, project_root)
    select_community_files(ctx, project_root)
    spdx_id = render_repository_files(ctx, project_root)
    update_license_integrations(project_root, spdx_id)
    update_public_context(ctx, project_root)
    configure_python_runtime(ctx, project_root)
    configure_project_manager(ctx, project_root)
    select_quality_tools(ctx, project_root)
    select_test_framework(ctx, project_root)
    remove_optional_paths(ctx, project_root)


def main() -> None:
    """Run the Copier task command-line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", type=Path)
    parser.add_argument("template_type")
    args = parser.parse_args()
    finalize(args.project_root.resolve(), args.template_type)


if __name__ == "__main__":
    main()
