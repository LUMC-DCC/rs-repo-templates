"""Synchronize or verify shared assets in each language template.

Shared files live in ``_cc_shared`` and are copied into every template that has
a ``{{cookiecutter.project_slug}}`` project directory. Cookiecutter context
files are generated per template so language-specific defaults can differ.
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

from build_cookiecutter_context import (
    build_context,
    context_json,
    load_policies,
    write_context,
)

ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "_config" / "template_policies.json"

TEMPLATE_DIRS = sorted(
    (
        path
        for path in ROOT.iterdir()
        if path.is_dir()
        and not path.name.startswith((".", "_"))
        and (path / "{{cookiecutter.project_slug}}").exists()
    ),
    key=lambda path: path.name,
)

RELATIVE_SYNC_MAP = {
    "hooks": "hooks",
    "template_hooks": "{{cookiecutter.project_slug}}/.template_hooks",
    ".github/dependabot.yml": "{{cookiecutter.project_slug}}/.github/dependabot.yml",
    ".github/workflows/changelog.yml": (
        "{{cookiecutter.project_slug}}/.github/workflows/changelog.yml"
    ),
    ".github/workflows/metadata.yml": (
        "{{cookiecutter.project_slug}}/.github/workflows/metadata.yml"
    ),
    "tools/check_changelog.py": (
        "{{cookiecutter.project_slug}}/tools/check_changelog.py"
    ),
}

IGNORED_SYNC_NAMES = {
    ".DS_Store",
    "__pycache__",
}

IGNORED_SYNC_SUFFIXES = {
    ".pyc",
}


def should_ignore(path: Path):
    """Check whether a source path should be excluded from sync.

    Parameters
    ----------
    path : pathlib.Path
        Source path candidate.

    Returns
    -------
    bool
        Whether the path should be ignored.
    """
    return path.name in IGNORED_SYNC_NAMES or path.suffix in IGNORED_SYNC_SUFFIXES


def sync_cookiecutter_context(
    policies,
    template_name: str,
    dst: Path,
    *,
    write: bool,
):
    """Synchronize one template-specific Cookiecutter context file.

    Parameters
    ----------
    policies : dict
        Parsed language-specific template policies.
    template_name : str
        Template name used to resolve template-specific defaults.
    dst : pathlib.Path
        Destination ``cookiecutter.json`` path.
    write : bool
        Whether to update a mismatched destination.

    Returns
    -------
    bool
        Whether the context file changed.
    """
    context = build_context(policies=policies, template=template_name)
    if not write:
        expected = context_json(context)
        return not dst.is_file() or dst.read_text(encoding="utf-8") != expected
    return write_context(context, dst)


def remove_path(path: Path, *, write: bool):
    """Remove a path when writing, retrying transient filesystem failures.

    Parameters
    ----------
    path : pathlib.Path
        Path to remove.
    write : bool
        Whether filesystem changes are enabled.
    """
    if not write:
        return
    for attempt in range(3):
        try:
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()
            return
        except FileNotFoundError:
            return
        except OSError:
            if attempt == 2:
                raise
            time.sleep(0.1)


def copy_file_if_changed(src: Path, dst: Path, *, write: bool):
    """Compare one file and optionally update a mismatched destination.

    Parameters
    ----------
    src : pathlib.Path
        Source file.
    dst : pathlib.Path
        Destination file.
    write : bool
        Whether to update a mismatched destination.

    Returns
    -------
    bool
        Whether the destination file changed.
    """
    if dst.exists() and dst.is_file() and dst.read_bytes() == src.read_bytes():
        return False

    if write:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return True


def sync_dir(src: Path, dst: Path, *, write: bool):
    """Compare one directory and optionally mirror it to a destination.

    Parameters
    ----------
    src : pathlib.Path
        Source directory.
    dst : pathlib.Path
        Destination directory.
    write : bool
        Whether to update a mismatched destination.

    Returns
    -------
    bool
        Whether the destination directory changed.
    """
    if not dst.exists() or not dst.is_dir():
        if not write:
            return True
        if dst.exists():
            remove_path(dst, write=True)
        dst.mkdir(parents=True, exist_ok=True)
        changed = True
    else:
        changed = False

    src_entries = {entry.name for entry in src.iterdir() if not should_ignore(entry)}
    for dst_entry in dst.iterdir():
        if dst_entry.name not in src_entries:
            remove_path(dst_entry, write=write)
            changed = True

    for src_entry in src.iterdir():
        if should_ignore(src_entry):
            continue
        changed = sync_path(src_entry, dst / src_entry.name, write=write) or changed

    return changed


def sync_path(src: Path, dst: Path, *, write: bool):
    """Compare one path and optionally synchronize it.

    Parameters
    ----------
    src : pathlib.Path
        Source path.
    dst : pathlib.Path
        Destination path.
    write : bool
        Whether to update a mismatched destination.

    Returns
    -------
    bool
        Whether the destination path changed.
    """
    if should_ignore(src):
        return False

    if src.is_file():
        if dst.exists() and dst.is_dir():
            remove_path(dst, write=write)
        return copy_file_if_changed(src, dst, write=write)
    elif src.is_dir():
        return sync_dir(src, dst, write=write)
    else:
        print(f"[warning] Unknown source type: {src}")
        return False


def synchronize(*, write: bool):
    """Synchronize or verify every discovered language template.

    Parameters
    ----------
    write : bool
        Whether mismatched generated files should be updated.

    Returns
    -------
    list[pathlib.Path]
        Out-of-sync destination paths.
    """
    mismatches = []
    policies = load_policies(POLICY_PATH)

    for template_dir in TEMPLATE_DIRS:
        context_path = template_dir / "cookiecutter.json"
        if sync_cookiecutter_context(
            policies,
            template_dir.name,
            context_path,
            write=write,
        ):
            mismatches.append(context_path)

        for rel_src, rel_dst in RELATIVE_SYNC_MAP.items():
            src = ROOT / "_cc_shared" / rel_src
            dst = template_dir / rel_dst
            if sync_path(src, dst, write=write):
                mismatches.append(dst)

    return mismatches


def main():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="update derived files")
    mode.add_argument(
        "--check",
        action="store_true",
        help="report drift without changing files",
    )
    args = parser.parse_args()

    mismatches = synchronize(write=args.write)
    prefix = "[sync] Updated" if args.write else "[out-of-sync]"
    for path in mismatches:
        print(f"{prefix} {path.relative_to(ROOT)}")

    if mismatches and args.check:
        print("Run `poetry run python _scripts/sync_shared.py --write` to update them.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
