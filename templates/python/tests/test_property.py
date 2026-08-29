"""Property-based tests for processing invariants."""

from hypothesis import given, strategies as st

from {{ project_slug }}.services.processing import process_text


@given(st.text())
def test_processing_preserves_input_text(text):
    """Ensure processing never mutates the recorded input text."""
    result = process_text(text)

    assert result.input_text == text


@given(st.text())
def test_processing_output_matches_uppercase(text):
    """Ensure processing output follows Python uppercase behavior."""
    result = process_text(text)

    assert result.output_text == text.upper()
