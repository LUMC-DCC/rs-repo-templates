"""Documentation-builder policy owned by the repository generator."""

DOCUMENTATION_BUILDER_PROFILES = {
    "plain": {"preview": "", "build": "", "output": "docs/"},
    "mkdocs": {
        "preview": "mkdocs serve",
        "build": "mkdocs build --strict",
        "output": "site/",
    },
    "zensical": {
        "preview": "zensical serve",
        "build": "zensical build --strict",
        "output": "site/",
    },
    "sphinx": {
        "preview": "",
        "build": "sphinx-build -W -b html docs/source docs/build/html",
        "output": "docs/build/html/index.html",
    },
    "pkgdown": {
        "preview": "Rscript -e 'pkgdown::build_site(preview = TRUE)'",
        "build": "Rscript -e 'pkgdown::build_site()'",
        "output": "site/",
    },
}


def documentation_builder_profile(name, *, run_prefix="", setup=""):
    """Return setup, preview, build, and output values for one builder."""
    profile = DOCUMENTATION_BUILDER_PROFILES.get(str(name), {})
    preview = str(profile.get("preview", ""))
    build = str(profile.get("build", ""))
    return {
        "setup": setup,
        "preview": f"{run_prefix}{preview}" if preview else "",
        "build": f"{run_prefix}{build}" if build else "",
        "output": str(profile.get("output", "")),
    }
