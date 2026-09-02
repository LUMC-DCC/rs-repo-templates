test_that("the exported package API composes with base R", {
  values <- vapply(c("open", "science"), process_text, character(1))
  expect_identical(unname(values), c("OPEN", "SCIENCE"))
})
