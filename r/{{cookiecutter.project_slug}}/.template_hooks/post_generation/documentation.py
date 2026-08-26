"""Select compatible documentation builder scaffolds."""

import shutil

from renderers.documentation_types import (
    optional_documentation_paths,
    selected_documentation_types,
    selected_optional_documentation_paths,
)
from utils.context import entries, resolve_choice
from utils.paths import remove_path


def resolve_documentation_builder(ctx):
    """Resolve a compatible documentation builder.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.

    Returns
    -------
    tuple[str, str]
        Requested and effective documentation builders.
    """
    requested, effective = resolve_choice(
        ctx,
        "documentation_builder",
        fallback="plain",
    )
    if not requested:
        effective = "plain"
    return requested, effective


def copy_builder_files(source, docs_dir):
    """Copy selected builder files into the docs directory.

    Parameters
    ----------
    source : pathlib.Path
        Builder-specific source directory.
    docs_dir : pathlib.Path
        Generated project documentation directory.
    """
    if not source.exists():
        return

    for item in source.iterdir():
        destination = docs_dir / item.name
        remove_path(destination)
        if item.is_dir():
            shutil.copytree(item, destination)
        else:
            shutil.copy2(item, destination)


def docs_source_dir(cwd):
    """Return the generated documentation source directory.

    Parameters
    ----------
    cwd : pathlib.Path
        Generated project root.

    Returns
    -------
    pathlib.Path
        Documentation source directory.
    """
    sphinx_source = cwd / "docs" / "source"
    if sphinx_source.exists():
        return sphinx_source
    return cwd / "docs"


def has_documentation(ctx):
    """Return whether generated documentation is selected.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.

    Returns
    -------
    bool
        Whether at least one documentation type was selected.
    """
    return bool(selected_documentation_types(entries(ctx, "documentation_types")))


def select_documentation_type_pages(ctx, cwd):
    """Remove optional documentation pages that were not selected.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.
    cwd : pathlib.Path
        Generated project root.
    """
    source_dir = docs_source_dir(cwd)
    documentation_types = entries(ctx, "documentation_types")
    selected = selected_documentation_types(documentation_types)
    keep_paths = selected_optional_documentation_paths(documentation_types)
    if "user" not in selected:
        remove_path(source_dir / "usage.md")
    for rel_path in optional_documentation_paths() - keep_paths:
        remove_path(source_dir / rel_path)


def select_documentation_builder(ctx, cwd):
    """Select documentation files for the effective builder.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.
    cwd : pathlib.Path
        Generated project root.
    """
    if not has_documentation(ctx):
        return

    docs_dir = cwd / "docs"
    builder_root = docs_dir / "_builders"
    shared_root = docs_dir / "_shared"
    requested, effective = resolve_documentation_builder(ctx)
    if effective in {"mkdocs", "zensical"}:
        copy_builder_files(builder_root / "site_generator", docs_dir)
    copy_builder_files(builder_root / effective, docs_dir)
    copy_builder_files(shared_root, docs_source_dir(cwd))
    remove_path(builder_root)
    remove_path(shared_root)
    select_documentation_type_pages(ctx, cwd)

    if effective not in {"mkdocs", "zensical", "sphinx"}:
        remove_path(cwd / ".github" / "workflows" / "docs.yml")

    if effective != "mkdocs":
        remove_path(cwd / "mkdocs.yml")
    if effective != "zensical":
        remove_path(cwd / "zensical.toml")

    if requested and requested != effective:
        print(
            "[warning] Documentation builder "
            f"{requested!r} is not supported for {ctx['_template_name']!r}; "
            f"using {effective!r}."
        )
