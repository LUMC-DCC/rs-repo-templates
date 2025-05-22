test_that("processing is idempotent", {
  set.seed(1)
  values <- replicate(25, paste(sample(letters, 12, replace = TRUE), collapse = ""))
  expect_identical(process_text(process_text(values)), process_text(values))
})
