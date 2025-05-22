"""Select compatible documentation builder scaffolds."""

import shutil

from post_generation.repository_files import model_from_context, validate_models
from renderers.documentation_types import (
    optional_documentation_paths,
    selected_documentation_types,
    selected_optional_documentation_paths,
)
from rs_files_templates import (
    DocumentationDeploymentModel,
    DocumentationDeveloperModel,
    DocumentationLegalModel,
    DocumentationOverviewModel,
    DocumentationReferenceModel,
    DocumentationUserModel,
    render_many,
)
from utils.context import entries, resolve_choice
from utils.documentation import documentation_builder_profile
from utils.paths import remove_path
from utils.project_management import project_manager_profile, setup_group_command


def resolve_documentation_builder(ctx):
    """Resolve a compatible documentation builder.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

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
        Normalized Copier context.

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
        Normalized Copier context.
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
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    if not has_documentation(ctx):
        return

    docs_dir = cwd / "docs"
    builder_root = docs_dir / "_builders"
    requested, effective = resolve_documentation_builder(ctx)
    if effective in {"mkdocs", "zensical"}:
        copy_builder_files(builder_root / "site_generator", docs_dir)
    copy_builder_files(builder_root / effective, docs_dir)
    remove_path(builder_root)
    remove_path(docs_dir / "_shared")

    if ctx.get("_template_name") == "python":
        setup = setup_group_command(ctx, "docs")
        run_prefix = str(project_manager_profile(ctx)["run_prefix"])
    elif ctx.get("_template_name") == "generic":
        setup = "python -m pip install --requirement docs/requirements.txt"
        run_prefix = ""
    else:
        setup = ""
        run_prefix = ""
    docs_commands = documentation_builder_profile(
        effective,
        setup=setup,
        run_prefix=run_prefix,
    )
    replacements = {
        "@@DOCS_SETUP@@": docs_commands["setup"],
        "@@DOCS_PREVIEW@@": docs_commands["preview"],
        "@@DOCS_BUILD@@": docs_commands["build"],
        "@@DOCS_OUTPUT@@": docs_commands["output"],
    }
    selected = set(selected_documentation_types(entries(ctx, "documentation_types")))
    model_types = [DocumentationOverviewModel]
    if "user" in selected:
        model_types.append(DocumentationUserModel)
    if "deployment" in selected:
        model_types.append(DocumentationDeploymentModel)
    if "developer" in selected:
        model_types.extend((DocumentationDeveloperModel, DocumentationReferenceModel))
    model_types.append(DocumentationLegalModel)
    models = [model_from_context(model_type, ctx) for model_type in model_types]
    validate_models(models)
    render_many(models, docs_source_dir(cwd))
    replace_documentation_tokens(docs_dir, replacements)
    select_documentation_type_pages(ctx, cwd)

    if effective not in {"mkdocs", "pkgdown", "zensical", "sphinx"}:
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


def replace_documentation_tokens(docs_dir, replacements):
    """Replace centralized builder-command tokens in attached builder files."""
    for path in docs_dir.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".rst"}:
            continue
        content = path.read_text(encoding="utf-8")
        rendered = content
        for placeholder, value in replacements.items():
            rendered = rendered.replace(placeholder, value)
        if rendered != content:
            path.write_text(rendered, encoding="utf-8")


def _append(path, section):
    """Append one repository-owned section when both values are present."""
    if not path.exists() or not section.strip():
        return
    content = path.read_text(encoding="utf-8").rstrip()
    path.write_text(f"{content}\n\n{section.strip()}\n", encoding="utf-8")


def _python_architecture(ctx):
    """Describe generated Python paths without adding them to reusable templates."""
    slug = str(ctx.get("project_slug", "project"))
    interface_types = {
        str(item.get("type", ""))
        for item in entries(ctx, "interfaces")
        if isinstance(item, dict)
    }
    adapter_types = interface_types - {"Library", "Ontology", "Workflow"}
    lines = [
        "## Project architecture",
        "",
        "The generated Python package uses a `src` layout.",
        "Runtime dependencies point inward: public entry points delegate reusable",
        "behavior to the service layer.",
        "",
        "```text",
        "public entry points",
    ]
    if adapter_types:
        lines.append("    -> adapters/")
    if "Script" in interface_types:
        lines.append("    -> scripts/")
    if "Workflow" in interface_types:
        lines.append("    -> workflows/")
    lines.extend(
        [
            "    -> services/",
            "```",
            "",
            "Services must not import interface adapters.",
            "",
            "Generated component paths:",
            f"- `src/{slug}/services/`",
        ]
    )
    if adapter_types:
        lines.append(f"- `src/{slug}/adapters/`")
    if "Script" in interface_types:
        lines.append("- `scripts/`")
    if "Workflow" in interface_types:
        lines.append(f"- `src/{slug}/workflows/`")
    if "Ontology" in interface_types or "SPARQL endpoint" in interface_types:
        lines.append(f"- `src/{slug}/ontology/`")
    if entries(ctx, "test_types"):
        lines.append("- `tests/`")
    for interface_type in sorted(interface_types):
        if interface_type == "Library":
            continue
        lines.extend(
            [
                "",
                f"### {interface_type}",
                "",
                "See the generated component paths above.",
            ]
        )
    return "\n".join(lines)


def _python_deployment(ctx):
    """Describe deployment entry points selected by repository interfaces."""
    slug = str(ctx.get("project_slug", "project"))
    command = slug.replace("_", "-")
    interface_types = {
        str(item.get("type", ""))
        for item in entries(ctx, "interfaces")
        if isinstance(item, dict)
    }
    http_types = {
        "Bioinformatics portal",
        "Database portal",
        "SPARQL endpoint",
        "Web API",
        "Web application",
        "Web service",
        "Workbench",
    }
    lines = []
    if interface_types & http_types:
        lines.extend(
            [
                "## HTTP service",
                "",
                "Run the generated composed application with:",
                "",
                "```bash",
                f"{command}-serve",
                "```",
            ]
        )
    if "Script" in interface_types:
        lines.extend(
            [
                "",
                "## Script",
                "",
                "Run scripts from a versioned environment with the package installed.",
            ]
        )
    if interface_types & {"Web application", "Workbench"}:
        lines.extend(
            ["", "## Web application", "", "Configure the generated web adapter."]
        )
    if interface_types & {"Bioinformatics portal", "Database portal"}:
        lines.extend(["", "## Portal", "", "Configure the generated portal adapter."])
    return "\n".join(lines)


def _python_api_reference(ctx, builder):
    """Return builder-specific Python API directives."""
    slug = str(ctx.get("project_slug", "project"))
    if builder in {"mkdocs", "zensical"}:
        return f"## Python API\n\n::: {slug}\n\n::: {slug}.services.processing"
    if builder == "sphinx":
        return (
            "## Python API\n\n"
            f".. automodule:: {slug}\n"
            "   :members:\n\n"
            f".. automodule:: {slug}.services.processing\n"
            "   :members:"
        )
    return ""


def _python_usage(ctx):
    """Return repository-specific commands for generated Python interfaces."""
    slug = str(ctx.get("project_slug", "project"))
    command = slug.replace("_", "-")
    run_prefix = str(project_manager_profile(ctx)["run_prefix"])
    interface_types = {
        str(item.get("type", ""))
        for item in entries(ctx, "interfaces")
        if isinstance(item, dict)
    }
    commands = []
    if "Command-line tool" in interface_types:
        commands.append(f'{command} process "example input"')
    if interface_types & {
        "Bioinformatics portal",
        "Database portal",
        "SPARQL endpoint",
        "Web API",
        "Web application",
        "Web service",
        "Workbench",
    }:
        commands.append(f"{run_prefix}{command}-serve")
    if "Script" in interface_types:
        commands.append(f'{run_prefix}python scripts/run_example.py "example input"')
    if not commands:
        return ""
    return "## Generated entry points\n\n```bash\n" + "\n".join(commands) + "\n```"


def attach_repository_documentation(ctx, cwd):
    """Attach builder, scaffold, and generated-file facts after RSM rendering."""
    if not has_documentation(ctx):
        return
    _, builder = resolve_documentation_builder(ctx)
    source_dir = docs_source_dir(cwd)
    if ctx.get("_template_name") == "python":
        _append(source_dir / "developer.md", _python_architecture(ctx))
        _append(source_dir / "reference.md", _python_api_reference(ctx, builder))
        _append(source_dir / "deployment.md", _python_deployment(ctx))
        _append(source_dir / "usage.md", _python_usage(ctx))

    workflow_dir = cwd / ".github" / "workflows"
    workflows = sorted(path.name for path in workflow_dir.glob("*.yml"))
    if workflows:
        section = "## Generated automation\n\n" + "\n".join(
            f"- `{name}`" for name in workflows
        )
        _append(source_dir / "developer.md", section)

    if ctx.get("_template_name") == "python":
        setup = setup_group_command(ctx, "docs")
        run_prefix = str(project_manager_profile(ctx)["run_prefix"])
    elif ctx.get("_template_name") == "generic":
        setup = "python -m pip install --requirement docs/requirements.txt"
        run_prefix = ""
    else:
        setup = ""
        run_prefix = ""
    commands = documentation_builder_profile(
        builder,
        setup=setup,
        run_prefix=run_prefix,
    )
    if commands["build"]:
        section = "## Documentation checks\n\n```bash\n"
        if commands["setup"]:
            section += commands["setup"] + "\n"
        section += commands["build"] + "\n```"
        _append(cwd / "CONTRIBUTING.md", section)
