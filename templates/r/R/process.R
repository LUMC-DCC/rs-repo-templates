#' Process text
#'
#' A small starter function that demonstrates the package boundary. Replace it
#' with project-specific implementation while keeping user interfaces thin.
#'
#' @param value A character vector to process.
#'
#' @return The input converted to upper case.
#' @export
#'
#' @examples
#' process_text("research software")
process_text <- function(value) {
  stopifnot(is.character(value))
  toupper(value)
}
