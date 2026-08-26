"""Render concise README badges from generated project capabilities."""

import re
from urllib.parse import quote, urlparse

from renderers.community_files import selected_community_files
from renderers.project_context.interoperability import interface_type_values
from utils.containerization import has_container_recipe
from utils.context import entries, object_value, resolve_choice, resolve_object_choice
from utils.release import has_python_distribution
from utils.security import has_vulnerability_scanning


def shields_badge_url(label, message, color="blue", label_color="gray"):
    """Build a Shields.io static badge URL.

    Parameters
    ----------
    label : str
        Left-hand badge text.
    message : str
        Right-hand badge text.
    color : str, default="blue"
        Right-hand badge color.
    label_color : str, default="gray"
        Left-hand badge color.

    Returns
    -------
    str
        Shields.io badge URL.
    """

    def escape_path_part(value):
        """Escape one Shields.io path segment.

        Parameters
        ----------
        value : str
            Badge path segment.

        Returns
        -------
        str
            Escaped path segment.
        """
        return quote(value.replace("-", "--"), safe="")

    return (
        "https://img.shields.io/badge/"
        f"{escape_path_part(label)}-"
        f"{escape_path_part(message)}-"
        f"{escape_path_part(color)}"
        f"?labelColor={quote(label_color, safe='')}"
    )


def markdown_badge(alt_text, image_url, link_url=""):
    """Render one linked or unlinked Markdown badge.

    Parameters
    ----------
    alt_text : str
        Accessible badge label.
    image_url : str
        Badge image URL.
    link_url : str, optional
        Destination opened by the badge.

    Returns
    -------
    str
        Markdown badge.
    """
    image = f"![{alt_text}]({image_url})"
    return f"[{image}]({link_url})" if link_url else image


def github_repository(repository_url):
    """Extract GitHub owner and repository names from a canonical URL.

    Parameters
    ----------
    repository_url : str
        Public source repository URL.

    Returns
    -------
    tuple[str, str] | None
        Owner and repository, or ``None`` for non-GitHub URLs.
    """
    parsed = urlparse(str(repository_url or "").strip())
    if parsed.hostname not in {"github.com", "www.github.com"}:
        return None

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2:
        return None
    return parts[0], re.sub(r"\.git$", "", parts[1])


def selected_channels(ctx):
    """Return normalized distribution channel names.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.

    Returns
    -------
    set[str]
        Lowercase selected channel names.
    """
    return {
        " ".join(str(channel).strip().lower().split())
        for channel in entries(ctx, "distribution_channels")
        if str(channel).strip()
    }


def primary_workflow(ctx):
    """Choose the main generated verification workflow for a CI badge.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.

    Returns
    -------
    str
        Workflow file name, or an empty string when CI is not generated.
    """
    is_python = str(ctx.get("_template_name", "")).strip().lower() == "python"
    if is_python:
        if entries(ctx, "test_types"):
            return "tests.yml"

        quality_choices = (
            resolve_object_choice(ctx, "quality_tools", "formatter")[1],
            resolve_object_choice(ctx, "quality_tools", "linter")[1],
            resolve_object_choice(ctx, "quality_tools", "type_checker")[1],
        )
        if any(quality_choices):
            return "quality.yml"
        requested_builder, documentation_builder = resolve_choice(
            ctx,
            "documentation_builder",
            fallback="plain",
        )
        if not requested_builder:
            documentation_builder = "plain"
        if entries(ctx, "documentation_types") and documentation_builder in {
            "mkdocs",
            "sphinx",
        }:
            return "docs.yml"
        if has_vulnerability_scanning(ctx):
            return "security.yml"
    if ctx.get("include_metadata", False):
        return "metadata.yml"
    if "CHANGELOG.md" in selected_community_files(ctx):
        return "changelog.yml"
    if (
        is_python
        and object_value(ctx, "licensing", "compatibility_check")
        == ("Yes - automated tooling")
        and str(object_value(ctx, "licensing", "license")).strip()
    ):
        return "license-compatibility.yml"
    if is_python and has_container_recipe(entries(ctx, "containerization")):
        return "containers.yml"
    if is_python and has_python_distribution(entries(ctx, "distribution_channels")):
        return "distribution.yml"
    return ""


def first_doi(ctx):
    """Return the first software DOI from persistent identifiers.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.

    Returns
    -------
    str
        Normalized DOI, or an empty string.
    """
    for identifier in entries(ctx, "persistent_identifiers"):
        if str(identifier.get("type", "")).strip().lower() != "doi":
            continue
        value = str(identifier.get("identifier", "")).strip()
        for prefix in (
            "https://doi.org/",
            "http://doi.org/",
            "http://dx.doi.org/",
            "doi:",
        ):
            if value.lower().startswith(prefix):
                value = value[len(prefix) :]
                break
        return value
    return ""


def build_readme_badges(ctx):
    """Build README badges supported by supplied project metadata.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.

    Returns
    -------
    str
        Space-separated Markdown badges.
    """
    badges = []
    repository_url = str(object_value(ctx, "urls", "repository")).rstrip("/")
    github = github_repository(repository_url)
    channels = selected_channels(ctx)
    distribution_name = str(ctx.get("project_slug", "")).replace("_", "-")

    workflow = primary_workflow(ctx)
    if github and workflow:
        workflow_url = f"{repository_url}/actions/workflows/{workflow}"
        badges.append(markdown_badge("CI", f"{workflow_url}/badge.svg", workflow_url))

    documentation_url = str(object_value(ctx, "urls", "documentation")).strip()
    if documentation_url:
        badges.append(
            markdown_badge(
                "Documentation",
                shields_badge_url("docs", "online"),
                documentation_url,
            )
        )

    if github and "github releases" in channels:
        owner, repository = github
        badges.append(
            markdown_badge(
                "GitHub release",
                f"https://img.shields.io/github/v/release/{owner}/{repository}",
                f"{repository_url}/releases/latest",
            )
        )

    if "pypi" in channels and distribution_name:
        package_name = quote(distribution_name, safe="-._")
        badges.append(
            markdown_badge(
                "PyPI",
                f"https://img.shields.io/pypi/v/{package_name}",
                f"https://pypi.org/project/{package_name}/",
            )
        )

    doi = first_doi(ctx)
    if doi:
        if "zenodo." in doi.lower():
            doi_badge_url = f"https://zenodo.org/badge/DOI/{quote(doi, safe='/')}.svg"
        else:
            doi_badge_url = shields_badge_url("DOI", doi)
        badges.append(
            markdown_badge(
                "DOI",
                doi_badge_url,
                f"https://doi.org/{quote(doi, safe='/')}",
            )
        )

    interface_types = interface_type_values(entries(ctx, "interfaces"))
    if interface_types:
        badges.append(
            markdown_badge(
                "Tool Type",
                shields_badge_url(
                    label="tool type",
                    message=" | ".join(interface_types),
                ),
            )
        )

    return " ".join(badges)
