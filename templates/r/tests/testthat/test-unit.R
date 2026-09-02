test_that("process_text handles character vectors", {
  expect_identical(process_text(c("a", "B")), c("A", "B"))
  expect_error(process_text(1), "is.character")
})
