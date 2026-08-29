"""Refresh or verify every artifact derived from authoritative sources.

This command is the repository's single maintenance entry point. It derives
Copier questions and documentation, and verifies that the pinned reusable-file
models still match both the RSM contract and this generator's integration.
"""

from __future__ import annotations

import argparse
import inspect
import sys
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any

import build_copier_questions
import build_field_usage_docs
import build_rsm_reference
import rs_files_templates
from rs_files_templates import FileTemplateModel, validate_contract_compatibility
from rsm_schema import schema as rsm_schema

ROOT = Path(__file__).resolve().parent.parent
COPIER_TASKS = ROOT / "_copier_tasks"


def normalize_answer(value: Any) -> Any:
    """Convert nullable prompt defaults to finalization sentinels.

    Parameters
    ----------
    value
        Derived Copier default.

    Returns
    -------
    Any
        Recursively normalized value.
    """
    if value is None:
        return ""
    if isinstance(value, dict):
        return {name: normalize_answer(item) for name, item in value.items()}
    if isinstance(value, list):
        return [normalize_answer(item) for item in value]
    return value


def public_file_models() -> tuple[type[FileTemplateModel], ...]:
    """Discover reusable file models exported by the pinned package.

    Returns
    -------
    tuple[type[rs_files_templates.FileTemplateModel], ...]
        Public concrete models ordered by output path.
    """
    models = {
        member
        for name in rs_files_templates.__all__
        if inspect.isclass(member := getattr(rs_files_templates, name))
        and issubclass(member, FileTemplateModel)
        and member is not FileTemplateModel
    }
    return tuple(sorted(models, key=lambda model: model.output_name))


def validate_generator_dependencies(questions: dict[str, Any]) -> None:
    """Validate the pinned schema and reusable-file integration.

    Parameters
    ----------
    questions
        Derived Copier questions used to construct an empty valid context.

    Raises
    ------
    RuntimeError
        If a public reusable model is not integrated exactly once.
    """
    rsm_schema.validate_schema()
    sys.path.insert(0, str(COPIER_TASKS))
    try:
        from post_generation.repository_files import (
            REPOSITORY_FILE_MODELS,
            model_from_context,
        )
    finally:
        sys.path.remove(str(COPIER_TASKS))

    public_models = public_file_models()
    integrated_models = tuple(REPOSITORY_FILE_MODELS)
    if set(public_models) != set(integrated_models):
        missing = sorted(
            model.__name__ for model in set(public_models) - set(integrated_models)
        )
        stale = sorted(
            model.__name__ for model in set(integrated_models) - set(public_models)
        )
        raise RuntimeError(
            f"rs-files-templates integration drift: missing={missing}, stale={stale}."
        )
    outputs = [model.output_name for model in integrated_models]
    if len(outputs) != len(set(outputs)):
        raise RuntimeError("Reusable file models must have unique output paths.")

    context = {
        name: normalize_answer(deepcopy(question.get("default")))
        for name, question in questions.items()
        if name in rsm_schema.raw["properties"]
    }
    context["project_slug"] = "project"
    for model_type in integrated_models:
        model = model_from_context(model_type, context)
        validate_contract_compatibility(model, schema=rsm_schema.raw)


def derived_artifacts() -> dict[Path, Callable[[], str]]:
    """Return every committed artifact and its deterministic producer.

    Returns
    -------
    dict[pathlib.Path, collections.abc.Callable]
        Output paths mapped to zero-argument content builders.
    """
    questions = build_copier_questions.build_questions()
    validate_generator_dependencies(questions)
    usage = build_field_usage_docs.load_usage(build_field_usage_docs.DEFAULT_USAGE_PATH)
    return {
        build_copier_questions.DEFAULT_OUTPUT_PATH: lambda: (
            build_copier_questions.questions_yaml(questions)
        ),
        build_field_usage_docs.DEFAULT_OUTPUT_PATH: lambda: (
            build_field_usage_docs.build_table(usage)
        ),
        ROOT / "_docs" / "contract" / "rsm-fields.md": lambda: (
            build_rsm_reference.build_reference(rsm_schema.raw)
        ),
    }


def synchronize(*, check: bool) -> list[Path]:
    """Write or verify all derived artifacts.

    Parameters
    ----------
    check
        Report drift without modifying files.

    Returns
    -------
    list[pathlib.Path]
        Paths whose committed contents differed.
    """
    changed = []
    for path, producer in derived_artifacts().items():
        content = producer()
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        changed.append(path)
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    return changed


def main() -> None:
    """Run the command-line interface."""
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="refresh derived files")
    mode.add_argument("--check", action="store_true", help="check derived files")
    args = parser.parse_args()

    changed = synchronize(check=args.check)
    if not changed:
        print("[maintenance] Derived files and generator dependencies are current.")
        return
    for path in changed:
        label = "out-of-sync" if args.check else "updated"
        print(f"[{label}] {path.relative_to(ROOT)}")
    if args.check:
        print("Run `poetry run python _scripts/maintain_repository.py --write`.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
