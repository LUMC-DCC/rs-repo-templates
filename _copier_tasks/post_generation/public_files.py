"""Update generated public-facing project context files."""

from post_generation.documentation import (
    attach_repository_documentation,
    docs_source_dir,
    has_documentation,
)
from post_generation.repository_files import model_from_context, validate_models
from renderers.badges import build_readme_badges
from renderers.legal import build_legal_page_content
from renderers.project_context import (
    build_api_interfaces_section,
    build_developer_functions_section,
    build_developer_interfaces_section,
    build_external_dependencies_section,
    build_external_services_section,
    build_operating_systems_section,
    build_project_context_sections,
    build_resource_requirements_section,
    build_security_and_data_section,
    build_software_functions_page,
    build_sustainability_section,
    build_user_functions_section,
    build_user_interfaces_section,
)
from renderers.publications import build_publication_note
from renderers.release import (
    build_container_deployment_section,
    build_release_page,
)
from rs_files_templates import ReadmeModel, render_readme_text
from utils.context import entries, object_entries, object_value
from utils.markdown import append_sections, insert_before_first_marker

README_END_MARKER = "<!-- rs-files-templates:README:end -->"
README_CUSTOM_GUIDANCE = (
    "<!-- Add project-specific README content below this line; it is preserved "
    "when the generated README is refreshed. -->"
)


def overview_candidates(cwd):
    """Return possible generated overview paths.

    Parameters
    ----------
    cwd : pathlib.Path
        Generated project root.

    Returns
    -------
    tuple[pathlib.Path, ...]
        Overview paths used by supported documentation builders.
    """
    return (
        cwd / "docs" / "overview.md",
        cwd / "docs" / "source" / "overview.md",
    )


def legal_candidates(cwd):
    """Return possible generated legal documentation paths.

    Parameters
    ----------
    cwd : pathlib.Path
        Generated project root.

    Returns
    -------
    tuple[pathlib.Path, ...]
        Legal page paths used by supported documentation builders.
    """
    return (
        cwd / "docs" / "legal.md",
        cwd / "docs" / "source" / "legal.md",
    )


def insert_line_after(path, anchor, line):
    """Insert a line after the first matching line when absent.

    Parameters
    ----------
    path : pathlib.Path
        Text file to update.
    anchor : str
        Existing line after which ``line`` should be inserted.
    line : str
        Line to insert.
    """
    if not path.exists():
        return

    lines = path.read_text(encoding="utf-8").splitlines()
    if line in lines:
        return
    try:
        index = lines.index(anchor)
    except ValueError:
        return

    lines.insert(index + 1, line)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def update_overview(ctx, cwd):
    """Append public project context to the selected overview page.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    if not has_documentation(ctx):
        return

    publication_note = build_publication_note(entries(ctx, "publications"))
    sections = build_project_context_sections(ctx, include_funding=True)
    for overview_path in overview_candidates(cwd):
        if overview_path.exists():
            insert_before_first_marker(overview_path, publication_note, ("## ",))
            append_sections(overview_path, sections)
            return


def update_functions_page(ctx, cwd):
    """Write generated functions documentation when function metadata exists.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    if not has_documentation(ctx):
        return

    content = build_software_functions_page(entries(ctx, "software_functions"))
    if not content:
        return

    source_dir = docs_source_dir(cwd)
    (source_dir / "functions.md").write_text(content, encoding="utf-8")
    insert_line_after(
        source_dir / "index.md",
        "- [Project overview](overview.md)",
        "- [Functions and operations](functions.md)",
    )
    insert_line_after(source_dir / "index.md", "overview", "functions")
    insert_line_after(source_dir / ".pages", "  - overview.md", "  - functions.md")


def update_function_cross_references(ctx, cwd):
    """Append function cross-references to generated docs pages.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    if not has_documentation(ctx):
        return

    functions = entries(ctx, "software_functions")
    source_dir = docs_source_dir(cwd)
    append_sections(source_dir / "usage.md", build_user_functions_section(functions))
    append_sections(
        source_dir / "developer.md",
        build_developer_functions_section(functions),
    )


def update_interface_references(ctx, cwd):
    """Append interface summaries to generated docs pages.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    if not has_documentation(ctx):
        return

    interfaces = entries(ctx, "interfaces")
    source_dir = docs_source_dir(cwd)
    append_sections(source_dir / "usage.md", build_user_interfaces_section(interfaces))
    append_sections(
        source_dir / "developer.md",
        build_developer_interfaces_section(interfaces),
    )
    append_sections(
        source_dir / "reference.md",
        build_api_interfaces_section(interfaces),
    )


def update_platform_references(ctx, cwd):
    """Append platform support to generated usage documentation.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    if not has_documentation(ctx):
        return

    source_dir = docs_source_dir(cwd)
    append_sections(
        source_dir / "usage.md",
        build_operating_systems_section(entries(ctx, "operating_systems")),
    )


def update_dependency_references(ctx, cwd):
    """Append external dependency notes to generated usage documentation.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    if not has_documentation(ctx):
        return

    source_dir = docs_source_dir(cwd)
    append_sections(
        source_dir / "usage.md",
        build_external_dependencies_section(entries(ctx, "external_dependencies")),
    )
    append_sections(
        source_dir / "deployment.md",
        build_external_dependencies_section(entries(ctx, "external_dependencies")),
    )


def update_service_references(ctx, cwd):
    """Append external service notes to generated deployment documentation.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    if not has_documentation(ctx):
        return

    source_dir = docs_source_dir(cwd)
    append_sections(
        source_dir / "deployment.md",
        build_external_services_section(entries(ctx, "external_services")),
    )


def update_release_references(ctx, cwd):
    """Write release policy and append container deployment guidance.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    if not has_documentation(ctx):
        return

    source_dir = docs_source_dir(cwd)
    (source_dir / "release.md").write_text(
        build_release_page(ctx),
        encoding="utf-8",
    )
    insert_line_after(
        source_dir / "index.md",
        "- [Project overview](overview.md)",
        "- [Releases](release.md)",
    )
    insert_line_after(source_dir / "index.md", "overview", "release")
    insert_line_after(source_dir / ".pages", "  - overview.md", "  - release.md")
    append_sections(
        source_dir / "deployment.md",
        build_container_deployment_section(
            entries(ctx, "containerization"),
            ctx.get("project_slug", "project"),
        ),
    )


def update_policy_references(ctx, cwd):
    """Write resource, sustainability, security, and data documentation.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    if not has_documentation(ctx):
        return

    pages = [
        (
            "resource-requirements",
            "Resource requirements",
            build_resource_requirements_section(
                ctx.get("resource_requirements", ""),
                level=1,
            ),
        ),
        (
            "sustainability",
            "Sustainability",
            build_sustainability_section(
                ctx.get("maintenance_level", ""),
                ctx.get("continuity_plan", ""),
                entries(ctx, "retirement_criteria"),
                level=1,
            ),
        ),
        (
            "security-and-data",
            "Security and data",
            build_security_and_data_section(
                object_value(ctx, "contacts", "security"),
                object_entries(ctx, "security_measures", "selected"),
                object_value(ctx, "security_measures", "additional"),
                object_value(ctx, "data_management", "sensitive_data_statement"),
                ctx.get("public_risk_notes", ""),
                object_value(ctx, "data_management", "dmp_reference"),
                level=1,
            ),
        ),
    ]
    pages = [page for page in pages if page[2]]
    if not pages:
        return

    source_dir = docs_source_dir(cwd)
    for slug, _, content in pages:
        (source_dir / f"{slug}.md").write_text(
            content.rstrip() + "\n",
            encoding="utf-8",
        )

    # Insert in reverse because each item is placed directly after the overview.
    for slug, title, _ in reversed(pages):
        insert_line_after(
            source_dir / "index.md",
            "- [Project overview](overview.md)",
            f"- [{title}]({slug}.md)",
        )
        insert_line_after(source_dir / "index.md", "overview", slug)
        insert_line_after(
            source_dir / ".pages",
            "  - overview.md",
            f"  - {slug}.md",
        )


def license_compatibility_note(ctx, cwd):
    """Describe the effective dependency-license review mechanism.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.

    Returns
    -------
    str
        Public compatibility statement, or an empty string when not selected.
    """
    method = object_value(ctx, "licensing", "compatibility_check")
    if method == "Yes - manual check":
        return "Dependency license compatibility is reviewed manually."
    if method != "Yes - automated tooling":
        return ""

    workflow = cwd / ".github" / "workflows" / "license-compatibility.yml"
    if workflow.exists():
        return "Dependency license compatibility is checked automatically in CI."
    return (
        "Automated dependency-license checking is selected. Configure a "
        "compatible checker when implementation dependencies are added."
    )


def update_legal(ctx, cwd):
    """Append legal context to the selected legal documentation page.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    if not has_documentation(ctx):
        return

    compatibility_note = license_compatibility_note(ctx, cwd)
    license_path = (
        "LICENSE.md"
        if ctx.get("_template_name") == "r"
        and object_value(ctx, "licensing", "license") == "MIT"
        else "LICENSE"
    )
    content = build_legal_page_content(
        object_value(ctx, "licensing", "license"),
        compatibility_note,
        object_entries(ctx, "regulatory_requirements", "selected"),
        object_value(ctx, "regulatory_requirements", "additional"),
        license_path,
    )
    for legal_path in legal_candidates(cwd):
        if legal_path.exists():
            append_sections(legal_path, content)
            return


def update_readme(ctx, cwd):
    """Compose the reusable README and preserve project-owned trailing content.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    model = model_from_context(ReadmeModel, ctx)
    validate_models([model])
    rendered = render_readme_text(model).rstrip()
    badges = " ".join(build_readme_badges(ctx, cwd))
    if badges:
        title, remainder = rendered.split("\n", 1)
        rendered = f"{title}\n\n{badges}\n{remainder.lstrip()}"

    readme_path = cwd / "README.md"
    existing = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    if README_END_MARKER in existing:
        custom_content = existing.split(README_END_MARKER, 1)[1].lstrip("\n")
    else:
        custom_content = README_CUSTOM_GUIDANCE + "\n"
    readme_path.write_text(
        f"{rendered}\n\n{README_END_MARKER}\n{custom_content}",
        encoding="utf-8",
    )


def update_public_context(ctx, cwd):
    """Update generated public-facing context files.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    update_overview(ctx, cwd)
    update_functions_page(ctx, cwd)
    update_function_cross_references(ctx, cwd)
    update_interface_references(ctx, cwd)
    update_platform_references(ctx, cwd)
    update_dependency_references(ctx, cwd)
    update_service_references(ctx, cwd)
    update_release_references(ctx, cwd)
    update_policy_references(ctx, cwd)
    update_legal(ctx, cwd)
    attach_repository_documentation(ctx, cwd)
    update_readme(ctx, cwd)
