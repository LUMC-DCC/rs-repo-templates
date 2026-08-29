# Build and view the documentation

Install the documentation dependencies:

```bash
@@PROJECT_SETUP_DOCS@@
```

Build the HTML documentation:

```bash
@@PROJECT_RUN@@sphinx-build -M html docs/source docs/build
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

The HTML entry point is `docs/build/html/index.html`.
