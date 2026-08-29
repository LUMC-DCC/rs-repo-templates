"""Workflow step definitions for {{ (project_name or project_slug) }}.

Each function in this module should represent one meaningful workflow step.
Steps receive typed inputs and return typed outputs, which makes them easier to
test, document, and connect to workflow engines such as CWL or Snakemake later.
"""

from dataclasses import dataclass, field

from {{ project_slug }}.workflows.config import WorkflowConfig
from {{ project_slug }}.services.processing import (
    ProcessingResult,
    process_text,
)


@dataclass(frozen=True)
class WorkflowInput:
    """Input payload passed to the first workflow step.

    Parameters
    ----------
    text : str
        Text value to process.
    config : WorkflowConfig
        Runtime settings for this workflow run.
    """

    text: str
    # Use a factory so every input payload receives its own config object.
    config: WorkflowConfig = field(default_factory=WorkflowConfig)


@dataclass(frozen=True)
class WorkflowResult:
    """Output payload returned by the workflow.

    Parameters
    ----------
    input_text : str
        Original text received by the workflow.
    output_text : str
        Processed text produced by the workflow.
    """

    input_text: str
    output_text: str


def process_step(payload: WorkflowInput) -> ProcessingResult:
    """Run the text-processing step.

    Parameters
    ----------
    payload : WorkflowInput
        Typed input payload for this step.

    Returns
    -------
    ProcessingResult
        Result returned by the shared processing service.
    """
    # The workflow delegates domain logic to the service layer. This keeps the
    # step focused on workflow data flow rather than processing details.
    return process_text(payload.text)
