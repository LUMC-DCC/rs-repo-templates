args <- commandArgs(trailingOnly = TRUE)
description <- read.dcf("DESCRIPTION")
version <- unname(description[1, "Version"])

if (!grepl("^[0-9]+(?:\\.[0-9]+){1,3}(?:[-.][0-9A-Za-z]+)*$", version)) {
  stop("DESCRIPTION contains an invalid release version: ", version, call. = FALSE)
}

if (length(args) > 1L) {
  stop("Usage: Rscript tools/check_release.R [tag]", call. = FALSE)
}

if (length(args) == 1L) {
  expected <- paste0("v", version)
  if (!identical(args[[1]], expected)) {
    stop("Release tag ", args[[1]], " does not match ", expected, call. = FALSE)
  }
}

message("Release metadata is consistent for version ", version, ".")
