test_that("the package can be loaded in a clean R process", {
  package_path <- find.package("{{ project_slug }}", quiet = TRUE)
  installed_metadata <- file.path(package_path, "Meta", "package.rds")
  is_installed <- nzchar(package_path) && file.exists(installed_metadata)
  skip_if(
    !is_installed,
    "requires an installed package, as provided by R CMD check"
  )
  expression <- "stopifnot({{ project_slug }}::process_text('ok') == 'OK')"
  command <- c("--vanilla", "-e", shQuote(expression))
  expect_equal(system2(file.path(R.home("bin"), "Rscript"), command), 0L)
})
