test_that("case conversion remains stable for empty input", {
  expect_identical(process_text(character()), character())
})
