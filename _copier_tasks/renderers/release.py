"""Render release and container guidance for generated projects."""

from utils.containerization import selected_container_types
from utils.context import entries, object_value
from utils.release import (
    has_python_distribution,
    has_r_distribution,
    normalize_distribution_channel,
)


def format_specification(specification):
    """Format one container or environment specification.

    Parameters
    ----------
    specification : dict
        Structured containerization entry.

    Returns
    -------
    str
        Markdown bullet content.
    """
    specification_type = str(specification.get("type", "")).strip()
    if not specification_type:
        return ""

    details = []
    standard = str(specification.get("standard", "")).strip()
    file_url = str(specification.get("file_url", "")).strip()
    notes = " ".join(str(specification.get("details", "")).split())
    if standard:
        details.append(f"standard: {standard}")
    if file_url:
        details.append(f"[source specification]({file_url})")
    if notes:
        details.append(notes)

    suffix = f" - {'; '.join(details)}" if details else ""
    return f"- **{specification_type}**{suffix}"


def build_container_deployment_section(entries, project_slug):
    """Build container usage and environment-specification guidance.

    Parameters
    ----------
    entries : list[dict]
        Containerization records from rendered context.
    project_slug : str
        Generated project slug used in image names.

    Returns
    -------
    str
        Markdown deployment section, or an empty string.
    """
    if not entries:
        return ""

    selected = selected_container_types(entries)
    lines = ["## Containers and reproducible environments", ""]

    if "docker" in selected:
        lines.extend(
            [
                "Build and run the Docker image:",
                "",
                "```bash",
                f"docker build --tag {project_slug}:local .",
                f"docker run --rm {project_slug}:local",
                "```",
                "",
            ]
        )
    if "oci" in selected:
        lines.extend(
            [
                "Build and run the OCI image with Podman:",
                "",
                "```bash",
                f"podman build --file Containerfile --tag {project_slug}:local .",
                f"podman run --rm {project_slug}:local",
                "```",
                "",
            ]
        )
    if "apptainer" in selected:
        lines.extend(
            [
                "Build and run the Apptainer image:",
                "",
                "```bash",
                f"apptainer build {project_slug}.sif Apptainer.def",
                f"apptainer run {project_slug}.sif",
                "```",
                "",
                "SingularityCE users can use the equivalent `singularity build` and "
                "`singularity run` commands.",
                "",
            ]
        )

    specification_lines = [
        formatted
        for entry in entries
        if isinstance(entry, dict)
        if (formatted := format_specification(entry))
    ]
    if specification_lines:
        lines.extend(["Declared specifications:", "", *specification_lines])

    return "\n".join(lines).rstrip()


def build_release_page(ctx):
    """Build concise generated release documentation.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Returns
    -------
    str
        Complete Markdown release page.
    """
    version = object_value(ctx, "versioning", "version") or "0.1.0"
    scheme = object_value(ctx, "versioning", "scheme")
    scheme_details = object_value(ctx, "versioning", "scheme_details")
    frequency = object_value(ctx, "versioning", "release_frequency")
    channels = [
        str(channel).strip()
        for channel in entries(ctx, "distribution_channels")
        if str(channel).strip()
    ]
    normalized_channels = {
        normalize_distribution_channel(channel) for channel in channels
    }

    template_name = str(ctx.get("_template_name", "")).strip().lower()
    if template_name == "r":
        version_guidance = (
            "`DESCRIPTION` is the source of truth for the package version."
        )
        version_file = "DESCRIPTION"
        version_field = "Version"
    elif template_name == "python":
        version_guidance = (
            "`pyproject.toml` is the source of truth for the project version."
        )
        version_file = "pyproject.toml"
        version_field = "project.version"
    else:
        version_guidance = (
            "The version recorded in the project metadata is the release baseline."
        )
        version_file = "the project metadata"
        version_field = "version"
    if ctx.get("include_metadata", False):
        version_guidance += " The metadata workflow validates the software metadata."

    lines = [
        "# Releases",
        "",
        version_guidance,
        "",
        "| Policy | Value |",
        "| --- | --- |",
        f"| Current version | `{version}` |",
        *([f"| Versioning scheme | {scheme} |"] if scheme else []),
        *([f"| Versioning details | {scheme_details} |"] if scheme_details else []),
        *([f"| Expected cadence | {frequency} |"] if frequency else []),
    ]
    if channels:
        lines.extend(["", "## Distribution channels", ""])
        lines.extend(f"- {channel}" for channel in channels)

    lines.extend(
        [
            "",
            "## Release process",
            "",
            f"1. Update `{version_field}` in `{version_file}`.",
            "2. Move completed entries from `Unreleased` in `CHANGELOG.md` into a "
            "section for the new version.",
            "3. Run the metadata, test, documentation, and release checks configured "
            "for the project.",
        ]
    )
    if has_python_distribution(channels):
        lines.extend(
            [
                "4. Create and push a `v<version>` tag. The distribution workflow "
                "checks that the tag matches `project.version` before publishing.",
                "",
                "Run the release check locally with:",
                "",
                "```bash",
                "python tools/check_release.py",
                f"python tools/check_release.py --tag v{version}",
                "```",
            ]
        )
    elif template_name == "r" and has_r_distribution(channels):
        lines.extend(
            [
                "4. Run `Rscript tools/check_release.R`, then create and push a "
                "`v<version>` tag after the source package passes `R CMD check`.",
                "",
                "Run the release checks locally with:",
                "",
                "```bash",
                "Rscript tools/check_release.R",
                f"Rscript tools/check_release.R v{version}",
                "R CMD build .",
                "R CMD check --no-manual --as-cran *.tar.gz",
                "```",
            ]
        )

    setup_notes = []
    if "pypi" in normalized_channels:
        setup_notes.append(
            "- **PyPI:** configure a trusted publisher for the GitHub `pypi` "
            "environment before the first tagged release."
        )
    if "cran" in normalized_channels:
        setup_notes.append(
            "- **CRAN:** inspect the generated check results and submit the source "
            "package through CRAN's external submission process."
        )
    if "bioconductor" in normalized_channels:
        setup_notes.append(
            "- **Bioconductor:** follow the current Bioconductor package submission "
            "and review process after local and CI checks pass."
        )
    if (
        "github releases" in normalized_channels
        or "github release" in normalized_channels
    ):
        artifact_label = (
            "the checked R source package"
            if template_name == "r"
            else "source and Python distribution artifacts"
        )
        setup_notes.append(
            f"- **GitHub Releases:** tagged releases are created with {artifact_label}."
        )
    if normalized_channels & {"github container registry", "ghcr", "ghcr.io"}:
        setup_notes.append(
            "- **GitHub Container Registry:** tagged OCI images are published with "
            "the repository token."
        )
    if normalized_channels & {"docker hub", "dockerhub"}:
        setup_notes.append(
            "- **Docker Hub:** add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` as "
            "repository secrets before publishing."
        )
    automated = {
        "pypi",
        "github release",
        "github releases",
        "github container registry",
        "ghcr",
        "ghcr.io",
        "docker hub",
        "dockerhub",
        "cran",
        "bioconductor",
    }
    manual_channels = [
        channel
        for channel in channels
        if normalize_distribution_channel(channel) not in automated
    ]
    if manual_channels:
        setup_notes.append(
            "- **External channels:** configure publication separately for "
            + ", ".join(manual_channels)
            + "."
        )
    if setup_notes:
        lines.extend(["", "## Channel setup", "", *setup_notes])

    return "\n".join(lines).rstrip() + "\n"
