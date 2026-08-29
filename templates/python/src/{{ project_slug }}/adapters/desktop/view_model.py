"""View-model helpers for the desktop adapter.

View models prepare display-ready data for GUI widgets. Keeping this layer
separate makes desktop behavior testable without opening windows.
"""

from dataclasses import dataclass

from {{ project_slug }}.services.processing import process_text


@dataclass(frozen=True)
class DesktopViewModel:
    """Data displayed by the desktop adapter.

    Parameters
    ----------
    title : str
        Window title.
    message : str
        Message displayed in the UI.
    """

    title: str
    message: str


def build_view_model(text: str = "{{ (project_name or project_slug) }}") -> DesktopViewModel:
    """Build display-ready data for the desktop UI.

    Parameters
    ----------
    text : str, default="{{ (project_name or project_slug) }}"
        Text to process.

    Returns
    -------
    DesktopViewModel
        Display-ready view model.
    """
    # Delegate processing to the shared service layer, then shape the result for
    # the GUI.
    result = process_text(text)
    return DesktopViewModel(
        title="{{ (project_name or project_slug) }}",
        message=result.output_text,
    )
