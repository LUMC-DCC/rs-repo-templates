# Build and view the documentation

Install the documentation dependencies:

```bash
@@PROJECT_SETUP_DOCS@@
```

Preview the documentation locally:

```bash
@@PROJECT_RUN@@zensical serve
```

Build the static site and treat warnings as errors:

```bash
@@PROJECT_RUN@@zensical build --strict
```

The local preview is available at <http://127.0.0.1:8000/> by default. The
static site is written to the `site/` directory.
