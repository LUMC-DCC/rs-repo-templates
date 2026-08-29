"""Apply confirmed SPDX metadata to language-specific generated files."""

from __future__ import annotations

import json

from utils.paths import remove_path


def update_pyproject_license(cwd, spdx_id):
    """Set the generated Python license expression and file declaration.

    Parameters
    ----------
    cwd : pathlib.Path
        Generated project root.
    spdx_id : str or None
        SPDX identifier confirmed by ``rs-files-templates``.
    """
    path = cwd / "pyproject.toml"
    if not path.exists():
        return

    lines = []
    in_project = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("["):
            in_project = line == "[project]"
        if in_project and (
            line.startswith("license = ") or line.startswith("license-files = ")
        ):
            continue
        lines.append(line)

    declarations = []
    if spdx_id:
        declarations.append(f"license = {json.dumps(spdx_id)}")
    if (cwd / "LICENSE").exists():
        declarations.append('license-files = ["LICENSE"]')

    for index, line in enumerate(lines):
        if line.startswith("requires-python = "):
            lines[index + 1 : index + 1] = declarations
            break
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def remove_array_block(lines, assignment):
    """Remove one generated multi-line TOML array assignment.

    Parameters
    ----------
    lines : list[str]
        TOML source lines.
    assignment : str
        Assignment prefix to remove.

    Returns
    -------
    list[str]
        Lines without the selected block.
    """
    updated = []
    index = 0
    while index < len(lines):
        if lines[index].startswith(assignment):
            index += 1
            while index < len(lines) and lines[index] != "]":
                index += 1
            index += index < len(lines)
            continue
        updated.append(lines[index])
        index += 1
    return updated


def remove_toml_section(lines, section_name):
    """Remove one generated TOML table.

    Parameters
    ----------
    lines : list[str]
        TOML source lines.
    section_name : str
        Exact table heading.

    Returns
    -------
    list[str]
        Lines without the selected table.
    """
    updated = []
    index = 0
    while index < len(lines):
        if lines[index] == section_name:
            index += 1
            while index < len(lines) and not lines[index].startswith("["):
                index += 1
            continue
        updated.append(lines[index])
        index += 1
    return updated


def remove_license_check(cwd):
    """Remove SPDX-only compatibility checks for custom license text.

    Parameters
    ----------
    cwd : pathlib.Path
        Generated project root.
    """
    remove_path(cwd / ".github" / "workflows" / "license-compatibility.yml")
    path = cwd / "pyproject.toml"
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    lines = remove_array_block(lines, "license = [")
    lines = remove_toml_section(lines, "[tool.licensecheck]")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def update_container_license(cwd, spdx_id):
    """Set OCI license labels in selected container recipes.

    Parameters
    ----------
    cwd : pathlib.Path
        Generated project root.
    spdx_id : str or None
        Confirmed SPDX identifier.
    """
    for file_name in ("Containerfile", "Dockerfile"):
        path = cwd / file_name
        if not path.exists():
            continue
        lines = [
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if not line.startswith("LABEL org.opencontainers.image.licenses=")
        ]
        if spdx_id:
            runtime_index = next(
                index
                for index, line in enumerate(lines)
                if line.startswith("FROM ") and " AS runtime" in line
            )
            lines.insert(
                runtime_index + 1,
                "LABEL org.opencontainers.image.licenses=" + json.dumps(spdx_id),
            )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    path = cwd / "Apptainer.def"
    if not path.exists():
        return
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith("org.opencontainers.image.licenses ")
    ]
    if spdx_id:
        labels_index = lines.index("%labels")
        lines.insert(
            labels_index + 1,
            f"    org.opencontainers.image.licenses {spdx_id}",
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_license_integrations(cwd, spdx_id):
    """Apply license metadata outside the package-owned license file.

    Parameters
    ----------
    cwd : pathlib.Path
        Generated project root.
    spdx_id : str or None
        Confirmed SPDX identifier.
    """
    update_pyproject_license(cwd, spdx_id)
    update_container_license(cwd, spdx_id)
    if not spdx_id:
        remove_license_check(cwd)
