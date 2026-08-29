# Build and view the documentation

Install the documentation dependencies:

```bash
@@PROJECT_SETUP_DOCS@@
```

Preview the documentation locally:

```bash
@@PROJECT_RUN@@mkdocs serve
```

Build the static site:

```bash
@@PROJECT_RUN@@mkdocs build
```

The local preview is available at <http://127.0.0.1:8000/> by default. The
static site is written to the `site/` directory.
