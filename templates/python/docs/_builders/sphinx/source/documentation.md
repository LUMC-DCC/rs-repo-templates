# Build and view the documentation

Install the documentation dependencies:

```bash
@@DOCS_SETUP@@
```

Build the HTML documentation:

```bash
@@DOCS_BUILD@@
```

The generated `docs/Makefile` and `docs/make.bat` expose the same Sphinx targets
for environments where `make` or a Windows command prompt is preferred.

On Unix-like systems:

```bash
make -C docs html
```

On Windows:

```bat
docs\make.bat html
```

The HTML entry point is `@@DOCS_OUTPUT@@`.
