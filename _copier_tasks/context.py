"""Load recorded Copier answers for repository finalization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from rsm_schema import RSMMetadata

ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "_config" / "template_policies.json"


def _render_value(value: Any) -> Any:
    """Convert nullable scalar answers to the template's empty sentinel."""
    if value is None:
        return ""
    if isinstance(value, dict):
        return {key: _render_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_render_value(item) for item in value]
    return value


def load_context(project_root: Path, template_type: str) -> dict[str, Any]:
    """Load public RSM answers and language-specific rendering policy.

    Parameters
    ----------
    project_root
        Generated repository root containing ``.copier-answers.yml``.
    template_type
        Expected language scaffold name.

    Returns
    -------
    dict[str, Any]
        Rendering context used by finalization modules.

    Raises
    ------
    ValueError
        If the recorded template type is missing or inconsistent.
    """
    answers_path = project_root / ".copier-answers.yml"
    answers = yaml.safe_load(answers_path.read_text(encoding="utf-8")) or {}
    recorded_type = answers.get("template_type")
    if recorded_type != template_type:
        raise ValueError(
            f"Recorded template type {recorded_type!r} does not match "
            f"task argument {template_type!r}."
        )

    policies = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    policy = policies[template_type]
    context = {
        name: _render_value(answers[name])
        for name in RSMMetadata.model_fields
        if name in answers
    }
    context.update(
        {
            "_template_name": template_type,
            "_template_defaults": policy.get("defaults", {}),
            "_template_schemas": policy.get("field_schemas", {}),
            "_template_supported_choices": policy.get("supported_choices", {}),
        }
    )
    return context
