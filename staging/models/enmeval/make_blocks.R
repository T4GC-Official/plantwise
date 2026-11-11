# make_blocks.R -- one spatial-block assignment per species, shared by every
# model so "block CV" means the same exam everywhere.
#
# Uses ENMeval::get.block (the same function biomod2's CV.strategy="block" and
# ENMeval's partitions="block" call), on the cell-deduped, no-NA occurrence set
# that the v1 script models. Writes:
#   <out>/<Species>.csv                     Species,Latitude,Longitude,block
#   <out>/maxent/<Species>_train_k.csv      Maxent samples file (blocks != k)
#   <out>/maxent/<Species>_test_k.csv       Maxent testsamplesfile (block == k)
suppressPackageStartupMessages({ library(terra); library(ENMeval) })
parse_args <- function(args) { p <- list(); for (a in args) { if (!startsWith(a, "--")) next
  kv <- strsplit(sub("^--", "", a), "=", fixed = TRUE)[[1]]; p[[kv[1]]] <- if (length(kv) > 1) kv[2] else "TRUE" }; p }
a <- parse_args(commandArgs(trailingOnly = TRUE))
script_arg <- grep("^--file=", commandArgs(), value = TRUE)
script_dir <- if (length(script_arg)) dirname(normalizePath(sub("^--file=", "", script_arg[1]))) else getwd()
repo_root  <- normalizePath(file.path(script_dir, "..", ".."))   # models/enmeval -> repo
g <- function(k, d) if (!is.null(a[[k]])) a[[k]] else d
species_csv <- g("species_csv", file.path(repo_root, "data", "occurrences", "filtered_species_output.csv"))
tif_folder  <- g("tif_folder", file.path(repo_root, "data", "attributes"))
bg_csv      <- g("bg_csv", file.path(repo_root, "data", "derived", "bias_layer", "randomBg.csv"))
list_file   <- g("species_list", file.path(repo_root, "data", "SPECIES.md"))
out         <- g("out", file.path(repo_root, "data", "derived", "blocks"))
dir.create(file.path(out, "maxent"), recursive = TRUE, showWarnings = FALSE)

tifs <- sort(list.files(tif_folder, "^wc2\\.1_30s_bio_([1-9]|1[0-9])_fc\\.tif$", full.names = TRUE))
pred <- terra::rast(tifs)
occ_all <- read.csv(species_csv)
bg <- read.csv(bg_csv)[, c("Longitude", "Latitude")]
species <- gsub(" ", "_", trimws(readLines(list_file))); species <- species[nzchar(species)]

summary <- list()
for (sp in species) {
  o <- unique(occ_all[occ_all$Species == sp, c("Longitude", "Latitude")])
  if (!nrow(o)) { message("skip ", sp, " (no data)"); next }
  o <- o[!duplicated(terra::cellFromXY(pred[[1]], as.matrix(o))), ]
  o <- o[stats::complete.cases(terra::extract(pred, as.matrix(o))), ]
  blk <- ENMeval::get.block(o, bg)
  o$block <- blk$occs.grp
  # Background block membership for each background set, so Maxent folds can
  # be scored within-block exactly as ENMeval/biomod2 do (they evaluate the
  # held-out block's presences only against that block's background).
  dir.create(file.path(out, "bg"), showWarnings = FALSE)
  for (tag in c("random", "bias")) {
    b <- read.csv(file.path(dirname(bg_csv), paste0(tag, "Bg.csv")))[, c("Longitude", "Latitude")]
    b$block <- ENMeval::get.block(o, b)$bg.grp
    write.csv(b, file.path(out, "bg", paste0(sp, "_", tag, ".csv")), row.names = FALSE)
  }
  d <- data.frame(Species = sp, Latitude = o$Latitude, Longitude = o$Longitude, block = o$block)
  write.csv(d, file.path(out, paste0(sp, ".csv")), row.names = FALSE)
  for (k in 1:4) {
    write.csv(d[d$block != k, 1:3], file.path(out, "maxent", paste0(sp, "_train_", k, ".csv")), row.names = FALSE)
    write.csv(d[d$block == k, 1:3], file.path(out, "maxent", paste0(sp, "_test_", k, ".csv")), row.names = FALSE)
  }
  summary[[sp]] <- data.frame(Species = sp, n = nrow(d), t(as.vector(table(factor(d$block, levels = 1:4)))))
}
s <- do.call(rbind, summary); names(s)[3:6] <- paste0("block", 1:4)
write.csv(s, file.path(out, "block_sizes.csv"), row.names = FALSE)
print(s, row.names = FALSE)
