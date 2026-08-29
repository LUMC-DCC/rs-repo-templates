"""Render release and container guidance for generated projects."""

from utils.containerization import selected_container_types
from utils.context import entries, object_value
from utils.release import (
    has_python_distribution,
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

    version_guidance = (
        "`pyproject.toml` is the source of truth for the project version."
    )
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
            "1. Update `project.version` in `pyproject.toml`.",
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

    setup_notes = []
    if "pypi" in normalized_channels:
        setup_notes.append(
            "- **PyPI:** configure a trusted publisher for the GitHub `pypi` "
            "environment before the first tagged release."
        )
    if (
        "github releases" in normalized_channels
        or "github release" in normalized_channels
    ):
        setup_notes.append(
            "- **GitHub Releases:** tagged releases are created with source and "
            "Python distribution artifacts."
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
