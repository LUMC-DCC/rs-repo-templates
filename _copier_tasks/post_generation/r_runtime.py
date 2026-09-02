"""Apply R runtime metadata to generated package infrastructure."""

from __future__ import annotations

import re

from utils.context import entries

RUNTIME_PATHS = (
    "Dockerfile",
    "Containerfile",
    "Apptainer.def",
    "environment.R",
)
R_CONTAINER_VERSION_TOKEN = "@@R_CONTAINER_VERSION@@"
R_DEPENDS_VERSION_TOKEN = "@@R_DEPENDS_VERSION@@"
DEFAULT_R_VERSION = "4.3.0"
VERSION_RE = re.compile(
    r"(?P<operator>>=|<=|>|<|==|=)?\s*(?P<version>\d+\.\d+(?:\.\d+)?)"
)


def r_version_constraint(ctx):
    """Return the public R version constraint, when supplied."""
    for language in entries(ctx, "programming_languages"):
        if str(language.get("name", "")).strip().lower() != "r":
            continue
        return str(language.get("version_constraint", "")).strip()
    return ""


def concrete_r_version(ctx):
    """Choose a concrete container version from the lower R bound."""
    constraint = r_version_constraint(ctx)
    for match in VERSION_RE.finditer(constraint):
        if match.group("operator") not in {None, "=", "==", ">", ">="}:
            continue
        version = match.group("version")
        return version if version.count(".") == 2 else f"{version}.0"
    return DEFAULT_R_VERSION


def description_r_requirement(ctx):
    """Build one valid DESCRIPTION lower-bound requirement."""
    version = concrete_r_version(ctx)
    return f">= {version}"


def configure_r_runtime(ctx, cwd):
    """Synchronize DESCRIPTION and selected container recipes with R metadata."""
    if str(ctx.get("_template_name", "")).strip().lower() != "r":
        return

    replacements = {
        R_CONTAINER_VERSION_TOKEN: concrete_r_version(ctx),
        R_DEPENDS_VERSION_TOKEN: description_r_requirement(ctx),
    }
    paths = [cwd / "DESCRIPTION", *(cwd / relative for relative in RUNTIME_PATHS)]
    for path in paths:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        for token, value in replacements.items():
            content = content.replace(token, value)
        path.write_text(content, encoding="utf-8")
