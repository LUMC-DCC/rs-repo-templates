# Generate a reproducible Nix environment when rix is the selected manager.
if (!requireNamespace("rix", quietly = TRUE)) {
  install.packages("rix", repos = "https://cloud.r-project.org")
}

rix::rix(
  r_ver = "@@R_CONTAINER_VERSION@@",
  r_pkgs = c(
{% set rix_packages = [] %}{% if test_types.entries %}{% set _ = rix_packages.append("testthat") %}{% endif %}{% if quality_tools.formatter == "styler" %}{% set _ = rix_packages.append("styler") %}{% endif %}{% if quality_tools.linter == "lintr" %}{% set _ = rix_packages.append("lintr") %}{% endif %}{% if documentation_types.entries and documentation_builder == "pkgdown" %}{% set _ = rix_packages.append("pkgdown") %}{% endif %}{% for package in rix_packages %}    "{{ package }}"{{ "," if not loop.last else "" }}
{% endfor %}  ),
  ide = "none",
  project_path = ".",
  overwrite = TRUE
)
