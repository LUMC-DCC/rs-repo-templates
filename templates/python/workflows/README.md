# Workflows

This directory contains workflow material for {{ (project_name or project_slug) }}.

## Current workflow

The current Python workflow accepts text input, processes it through the
project service layer, and returns a structured result.

```python
from {{ project_slug }}.workflows.pipeline import run_workflow

result = run_workflow("example input")
print(result.output_text)
```

## Contents

| Path | Contents |
| ---- | -------- |
| `definitions/` | Engine-specific workflow definitions for this project. |
| `examples/example_input.txt` | Minimal example input for smoke tests and demonstrations. |
| `src/{{ project_slug }}/workflows/` | Importable Python workflow code. |
