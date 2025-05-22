# Build and view the documentation

Install the documentation dependencies:

```bash
@@DOCS_SETUP@@
```

Build the HTML documentation:

```bash
@@DOCS_BUILD@@
```

On Unix-like systems, `make -C docs html` exposes the same build. On Windows,
use `docs\make.bat html`. The HTML entry point is
`@@DOCS_OUTPUT@@`.
