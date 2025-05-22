test_that("the package exposes its starter function", {
  expect_true(is.function(process_text))
  expect_identical(process_text("research"), "RESEARCH")
})
