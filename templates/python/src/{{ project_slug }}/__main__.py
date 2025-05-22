"""Executable module for ``python -m {{ project_slug }}``.

Python runs this file when the package is executed as a module. The real entry
logic lives in ``main.py`` so it can also be imported and tested directly.
"""

from {{ project_slug }}.main import main

if __name__ == "__main__":
    main()
