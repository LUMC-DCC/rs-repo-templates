"""Apply Python package runtime metadata to generated infrastructure."""

from utils.python_runtime import container_python_version

CONTAINER_PATHS = (
    "Dockerfile",
    "Containerfile",
    "Apptainer.def",
)
PYTHON_VERSION_TOKEN = "@@PYTHON_CONTAINER_VERSION@@"


def configure_python_runtime(ctx, cwd):
    """Validate Python metadata and synchronize selected container recipes.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    cwd : pathlib.Path
        Generated project root.
    """
    if str(ctx.get("_template_name", "")).strip().lower() != "python":
        return

    version = container_python_version(cwd)
    for relative_path in CONTAINER_PATHS:
        path = cwd / relative_path
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        path.write_text(
            content.replace(PYTHON_VERSION_TOKEN, version),
            encoding="utf-8",
        )
