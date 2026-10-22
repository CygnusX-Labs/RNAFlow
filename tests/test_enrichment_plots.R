#!/usr/bin/env Rscript
# Plot selection and integration tests. KEGG calls are stubbed to avoid network;
# GO core tests use clusterProfiler with an in-memory annotation (no ontologyIndex).
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(tibble)
  library(clusterProfiler)
  library(log4r)
})

load_functions <- function(path) {
  env <- new.env()
  for (expr in parse(path)) {
    if (is.call(expr) && identical(expr[[1]], as.name("<-"))) eval(expr, env)
  }
  env
}
go <- load_functions("src/src/Enrichments/go_enricher.r")
kegg <- load_functions("src/src/Enrichments/kegg_enricher.r")
output <- Sys.getenv("RNAFLOW_PLOT_TEST_DIR", unset = tempfile("rnaflow-enrichment-plots-", tmpdir = "/tmp"))
dir.create(output, recursive = TRUE, showWarnings = FALSE)

check_images <- function(prefix) {
  png <- paste0(prefix, ".png")
  pdf <- paste0(prefix, ".pdf")
  stopifnot(file.info(png)$size > 1000, file.info(pdf)$size > 1000)
  stopifnot(identical(readBin(png, "raw", 8), as.raw(c(137, 80, 78, 71, 13, 10, 26, 10))))
  stopifnot(rawToChar(readBin(pdf, "raw", 4)) == "%PDF")
}

terms <- data.frame(
  ID = sprintf("path%03d", 1:18),
  Description = c(rep("Duplicated description", 2), rep("A long pathway description that should wrap across lines for readable labels", 16)),
  pvalue = seq_len(18) / 10000,
  p.adjust = c(0, seq_len(13) / 1000, 0.1, 0.5, NA, Inf),
  Count = seq_len(18)
)
terms <- terms[rev(seq_len(nrow(terms))), ]
for (kind in c("GO", "KEGG")) {
  env <- if (kind == "GO") go else kegg
  prefix <- file.path(output, paste0(kind, "_top10"))
  plot <- env$plot_enrichment_top_terms(terms, prefix, paste(kind, "enrichment"))
  stopifnot(nrow(plot$data) == 10, identical(plot$data$ID, sprintf("path%03d", 1:10)))
  stopifnot(nrow(ggplot_build(plot)$data[[1]]) == 10)
  check_images(prefix)
  small <- env$plot_enrichment_top_terms(terms[terms$ID %in% sprintf("path%03d", 1:3), ],
                                        file.path(output, paste0(kind, "_small")), kind)
  stopifnot(nrow(small$data) == 3)
  empty <- env$plot_enrichment_top_terms(terms[which(terms$p.adjust >= 0.1), ],
                                        file.path(output, paste0(kind, "_empty")), kind)
  stopifnot(grepl("No significant pathways", ggplot_build(empty)$data[[1]]$label))
  check_images(file.path(output, paste0(kind, "_empty")))
}

# Exercise the actual KEGG table entry point: both directions plot by default.
kegg$enrichKEGG <- function(...) terms
input <- file.path(output, "deg.csv")
write.csv(data.frame(GeneID = 1:20, padj = 0.001, log2FoldChange = rep(c(2, -2), each = 10)),
          input, row.names = FALSE)
kegg$run_kegg_deg_table(input, out_dir = output, name = "fixture_KEGG")
for (direction in c("UP", "DOWN")) {
  prefix <- file.path(output, paste0("fixture_KEGG_", direction, "_enrichments"))
  check_images(prefix)
  full <- read.csv(paste0(prefix, "_full.csv"))
  sig <- read.csv(paste0(prefix, ".csv"))
  stopifnot(nrow(full) == 18, nrow(sig) == 14)
  stopifnot(all(sig$p.adjust < 0.05))
  stopifnot(identical(sig$ID, full$ID[which(full$p.adjust < 0.05)]))
}
map <- data.frame(symbol = "1", ncbi = "1")
kegg$run_kegg_enrichment(character(), map, "no_genes", output)
check_images(file.path(output, "no_genes_enrichments"))
kegg$run_kegg_enrichment("unmapped", map, "no_mapping", output)
check_images(file.path(output, "no_mapping_enrichments"))
kegg$enrichKEGG <- function(...) terms[FALSE, ]
kegg$run_kegg_enrichment("1", map, "no_terms", output)
check_images(file.path(output, "no_terms_enrichments"))

# Real GO enrichment and a normal empty direction must both produce images.
go$logger <- log4r::logger(threshold = "INFO", appenders = log4r::file_appender(file.path(output, "go.log")))
annot <- list(
  term2gene = data.frame(GOID = c(rep("GO:0000001", 50), rep("GO:0000002", 950)), GeneID = paste0("gene", 1:1000)),
  term2name = data.frame(GOID = c("GO:0000001", "GO:0000002"), Term = c("Fixture pathway A", "Fixture pathway B"))
)
go$run_core_enricher(paste0("gene", 1:30), annot, output, "fixture_GO", "UP", 0.05)
go$run_core_enricher(character(), annot, output, "fixture_GO", "DOWN", 0.05)
check_images(file.path(output, "fixture_GO_UP"))
check_images(file.path(output, "fixture_GO_DOWN"))
cat("PASS: GO/KEGG top-10 selection, empty states, default UP/DOWN plots, and KEGG CSV filtering\n")
cat("Artifacts:", output, "\n")
