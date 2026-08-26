"""Render reusable repository files through ``rs-files-templates``."""

from __future__ import annotations

import os
from typing import Any

from rs_files_templates import (
    ChangelogModel,
    CitationModel,
    CodeMetaModel,
    CodeOfConductModel,
    ContributingModel,
    GovernanceModel,
    IssueTemplateModel,
    LicenseModel,
    PullRequestTemplateModel,
    SecurityModel,
    SupportModel,
    ZenodoModel,
    render_many,
)
from rs_files_templates.external import spdx
from utils.context import entries, object_value
from utils.rsm import rsm_payload

COMMUNITY_MODELS = {
    "CHANGELOG.md": ChangelogModel,
    "CODE_OF_CONDUCT.md": CodeOfConductModel,
    "CONTRIBUTING.md": ContributingModel,
    "GOVERNANCE.md": GovernanceModel,
    "SECURITY.md": SecurityModel,
    "SUPPORT.md": SupportModel,
}

REPOSITORY_FILE_MODELS = (
    ChangelogModel,
    CitationModel,
    CodeMetaModel,
    CodeOfConductModel,
    GovernanceModel,
    IssueTemplateModel,
    LicenseModel,
    PullRequestTemplateModel,
    SecurityModel,
    SupportModel,
    ZenodoModel,
    ContributingModel,
)


def configure_spdx_endpoint():
    """Apply the generator's optional SPDX endpoint override."""
    base_url = os.environ.get("SPDX_LICENSE_API_BASE", "").rstrip("/")
    if not base_url:
        return
    spdx.SPDX_LICENSE_URL = base_url + "/{identifier}.json"
    spdx.fetch_spdx_license_text.cache_clear()


def model_from_context(model_type, ctx):
    """Build one file model from the RSM fields it declares.

    Parameters
    ----------
    model_type : type[rs_files_templates.FileTemplateModel]
        Concrete reusable file model.
    ctx : dict
        Rendered Cookiecutter context.

    Returns
    -------
    rs_files_templates.FileTemplateModel
        Validated model containing only fields used by the target file.
    """
    payload = rsm_payload(ctx, model_type.model_fields)
    return model_type.model_validate(payload)


def confirmed_spdx_identifier(ctx):
    """Return the selected license when SPDX recognizes it.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.

    Returns
    -------
    str or None
        Confirmed SPDX identifier, or ``None`` for custom terms.
    """
    value = str(object_value(ctx, "licensing", "license")).strip()
    if not value or "\n" in value:
        return None
    try:
        spdx.fetch_spdx_license_text(value)
    except spdx.UnknownSpdxLicense:
        return None
    return value


def uses_zenodo(ctx):
    """Return whether Zenodo is a selected distribution channel.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.

    Returns
    -------
    bool
        Whether Zenodo release metadata should be generated.
    """
    return any(
        " ".join(str(channel).strip().lower().split()) == "zenodo"
        for channel in entries(ctx, "distribution_channels")
    )


def selected_models(ctx, spdx_identifier=None):
    """Build all reusable file models selected by the context.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.
    spdx_identifier : str or None, optional
        License identifier confirmed against SPDX for constrained metadata.

    Returns
    -------
    list[rs_files_templates.FileTemplateModel]
        Models to render into the generated repository.
    """
    models: list[Any] = []
    if ctx.get("include_metadata", False):
        models.extend(
            (
                model_from_context(CodeMetaModel, ctx),
                model_from_context(CitationModel, ctx),
            )
        )

    license_value = str(object_value(ctx, "licensing", "license")).strip()
    if license_value:
        models.append(model_from_context(LicenseModel, ctx))

    selected_community_files = set(entries(ctx, "community_files"))
    models.extend(
        model_from_context(model_type, ctx)
        for file_name, model_type in COMMUNITY_MODELS.items()
        if file_name in selected_community_files
    )
    if "CONTRIBUTING.md" in selected_community_files:
        models.append(model_from_context(PullRequestTemplateModel, ctx))

    if uses_zenodo(ctx):
        zenodo_model = model_from_context(ZenodoModel, ctx)
        # Zenodo accepts SPDX identifiers, while the RSM contract also permits
        # custom license text. Keep custom terms in LICENSE without placing an
        # invalid value in Zenodo's controlled license field.
        zenodo_model.licensing.license = spdx_identifier or ""
        models.append(zenodo_model)
    return models


def render_issue_templates(ctx, cwd):
    """Render package-owned GitHub issue forms when support is selected.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.
    cwd : pathlib.Path
        Generated project root.
    """
    if "SUPPORT.md" not in set(entries(ctx, "community_files")):
        return

    model = model_from_context(IssueTemplateModel, ctx)
    target_root = cwd / ".github" / "ISSUE_TEMPLATE"
    target_root.mkdir(parents=True, exist_ok=True)
    for file_name, content in model.archive_entries().items():
        # Archive entries are package-owned basenames, but reject path
        # components defensively before writing into the repository.
        unsafe_name = (
            file_name in {"", ".", ".."} or "/" in file_name or "\\" in file_name
        )
        if unsafe_name:
            raise ValueError(f"Unsafe issue-template filename: {file_name!r}")
        (target_root / file_name).write_text(content, encoding="utf-8")


def render_repository_files(ctx, cwd):
    """Render selected package-owned files into a generated project.

    Parameters
    ----------
    ctx : dict
        Rendered Cookiecutter context.
    cwd : pathlib.Path
        Generated project root.

    Returns
    -------
    str or None
        Confirmed SPDX identifier for downstream Zenodo metadata.
    """
    configure_spdx_endpoint()
    spdx_identifier = None
    if object_value(ctx, "licensing", "license"):
        spdx_identifier = confirmed_spdx_identifier(ctx)

    models = selected_models(ctx, spdx_identifier)
    if models:
        render_many(models, cwd)
    render_issue_templates(ctx, cwd)
    return spdx_identifier
