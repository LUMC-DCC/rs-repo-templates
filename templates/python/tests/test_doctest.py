"""Doctest runner for documented Python examples."""

import doctest

from {{ project_slug }}.services import processing


def test_processing_doctests_pass():
    """Ensure documented processing examples stay executable."""
    result = doctest.testmod(processing)

    assert result.failed == 0
