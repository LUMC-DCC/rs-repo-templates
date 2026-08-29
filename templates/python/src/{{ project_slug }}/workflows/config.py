"""Runtime configuration for {{ (project_name or project_slug) }} workflows.

The objects in this module describe settings that may change between workflow
runs, such as labels, profiles, resource limits, or paths supplied by a workflow
engine. Keep project logic in service modules and pass only configuration values
through this layer.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowConfig:
    """Settings used by the workflow runner.

    Parameters
    ----------
    label : str
        Human-readable label shown in logs, reports, or workflow metadata.
    """

    # A visible label is useful even in tiny workflows because it gives logs and
    # reports a stable name before a full workflow engine is configured.
    label: str = "{{ (project_name or project_slug) }} workflow"
