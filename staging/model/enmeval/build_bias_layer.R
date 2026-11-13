# build_bias_layer.R -- runnable port of ../../docs/refs/bias_layer_r_code.R (delivered
# 2026-09-09) onto the PlantWise benchmark inputs.
#
# What it does (unchanged from the delivered script): pool ALL species'
# occurrences as presences, draw 10,000 random background points, fit Maxent to
# model *collector effort*, predict it over the study area (biasMap), then draw
# 10,000 background points with probability proportional to biasMap (biasBg).
# biasBg is the `bias_sites` input the v1 ENMeval script was always meant to get.
#
# What differs, and why:
#   - predictors: the 19 WG-clipped bioclim layers in PlantWise_v0/final_attributes
#     (no elevation, WG extent) so the bias model sees exactly what every
#     benchmark run sees. --tif_folder / --elevation override.
#   - occurrences: filtered_species_output.csv (Species,Latitude,Longitude)
#     instead of the Excel sheet; no Genus column needed.
#   - rgdal (readOGR) dropped -- archived from CRAN; the layers are already
#     masked to the WG so no boundary clip is needed.
#   - seeds exposed as --seed_bg / --seed_bias (defaults 454 / 30985 as delivered).
suppressPackageStartupMessages({
  library(rJava); library(raster); library(dismo); library(dplyr)
})
options(java.parameters = "-Xmx4g")

parse_args <- function(args) {
  parsed <- list()
  for (arg in args) {
    if (!startsWith(arg, "--")) next
    kv <- strsplit(sub("^--", "", arg), "=", fixed = TRUE)[[1]]
    parsed[[kv[1]]] <- if (length(kv) > 1) paste(kv[-1], collapse = "=") else "TRUE"
  }
  parsed
}
log_info <- function(...) message(sprintf("[%s] %s", format(Sys.time(), "%H:%M:%S"), paste0(...)))

script_arg <- grep("^--file=", commandArgs(), value = TRUE)
script_dir <- if (length(script_arg)) dirname(normalizePath(sub("^--file=", "", script_arg[1]))) else getwd()
repo_root  <- normalizePath(file.path(script_dir, ".."))   # enmeval -> model
a <- parse_args(commandArgs(trailingOnly = TRUE))
g <- function(k, d) if (!is.null(a[[k]])) a[[k]] else d

species_csv <- g("species_csv", file.path(repo_root, "data", "occurrences", "filtered_species_output.csv"))
tif_folder  <- g("tif_folder",  file.path(repo_root, "data", "attributes"))
elev_path   <- g("elevation",   "")
maxent_jar  <- g("maxent_jar",  file.path(repo_root, "maxent", "maxent.jar"))
out_dir     <- g("out",         file.path(repo_root, "data", "derived", "bias_layer"))
n_bg        <- as.integer(g("n_bg", "10000"))
min_occ     <- as.integer(g("min_occ", "4"))
seed_bg     <- as.integer(g("seed_bg", "454"))
seed_bias   <- as.integer(g("seed_bias", "30985"))
exclude     <- if (!is.null(a$exclude_species)) trimws(unlist(strsplit(a$exclude_species, ","))) else character(0)
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

# dismo needs maxent.jar in its java dir (same convention as the v1 script)
dismo_jar <- file.path(system.file("java", package = "dismo"), "maxent.jar")
if (!file.exists(dismo_jar)) stopifnot(file.copy(maxent_jar, dismo_jar))

# ---- predictors ---------------------------------------------------------------
tifs <- list.files(tif_folder, "^wc2\\.1_30s_bio_([1-9]|1[0-9])_fc\\.tif$", full.names = TRUE)
tifs <- tifs[order(as.integer(sub(".*bio_([0-9]+)_fc.*", "\\1", basename(tifs))))]
stopifnot(length(tifs) == 19)
pred <- raster::stack(tifs)
names(pred) <- paste0("BIO", 1:19)
if (nzchar(elev_path)) {
  elev <- raster::crop(raster::raster(elev_path), pred)
  elev <- raster::resample(elev, pred[[1]], method = "bilinear")
  names(elev) <- "elevation"
  pred <- raster::stack(pred, raster::mask(elev, pred[[1]]))
}
log_info("Predictors: ", nlayers(pred), " layers, ", ncell(pred), " cells, extent ",
         paste(round(as.vector(extent(pred)), 3), collapse = " "))

# ---- occurrences: all species, one point per cell per species -----------------
occ <- read.csv(species_csv)
stopifnot(all(c("Species", "Latitude", "Longitude") %in% names(occ)))
occ <- unique(occ)
if (length(exclude)) occ <- occ[!(occ$Species %in% exclude), ]
occ$cell <- raster::cellFromXY(pred[[1]], occ[, c("Longitude", "Latitude")])
occ <- occ[!is.na(occ$cell), ]
occ <- occ %>% distinct(Species, cell, .keep_all = TRUE)          # = elimCellDups per species
keep <- occ %>% count(Species) %>% filter(n >= min_occ) %>% pull(Species)
occ <- occ %>% filter(Species %in% keep)
log_info("Occurrences after per-species cell dedup and >=", min_occ, " filter: ",
         nrow(occ), " points, ", length(keep), " species")

bias.ext <- as.data.frame(raster::extract(pred, occ[, c("Longitude", "Latitude")]))
bias.ext <- cbind(occ[, c("Longitude", "Latitude")], bias.ext)
bias.ext <- bias.ext[complete.cases(bias.ext), ]

# ---- random background ---------------------------------------------------------
set.seed(seed_bg)
randomSites <- as.data.frame(dismo::randomPoints(pred[[1]], n_bg + 1000))
colnames(randomSites) <- c("Longitude", "Latitude")
randomBg <- cbind(randomSites, as.data.frame(raster::extract(pred, randomSites)))
randomBg <- randomBg[complete.cases(randomBg), ][seq_len(min(n_bg, sum(complete.cases(randomBg)))), ]
write.csv(randomBg, file.path(out_dir, "randomBg.csv"), row.names = FALSE)

# ---- collector-effort Maxent ---------------------------------------------------
trainData <- rbind(bias.ext, randomBg)
presentBg <- c(rep(1, nrow(bias.ext)), rep(0, nrow(randomBg)))
write.csv(cbind(trainData, presentBg), file.path(out_dir, "biasIn.csv"), row.names = FALSE)
log_info("Fitting bias Maxent: ", nrow(bias.ext), " presences vs ", nrow(randomBg), " background")
t0 <- Sys.time()
biasModel <- dismo::maxent(x = trainData[, -(1:2)], p = presentBg,
                           args = c("writebackgroundpredictions=true", "randomtestpoints=20"),
                           path = file.path(out_dir, "maxent_temp"))
log_info("Bias model fitted in ", round(as.numeric(difftime(Sys.time(), t0, units = "secs"))), " s; ",
         "test AUC ", round(biasModel@results["Test.AUC", 1], 3))
write.csv(biasModel@results, file.path(out_dir, "biasModel.csv"))
save(biasModel, file = file.path(out_dir, "biasModel.RData"))

biasMap <- dismo::predict(biasModel, pred)
raster::writeRaster(biasMap, file.path(out_dir, "biasMap.tif"), format = "GTiff", overwrite = TRUE)
log_info("biasMap written; value range ", paste(round(range(values(biasMap), na.rm = TRUE), 3), collapse = "-"))

# ---- effort-weighted background --------------------------------------------------
set.seed(seed_bias)
biasSites <- dismo::randomPoints(biasMap, n_bg, prob = TRUE)
biasBg <- cbind(as.data.frame(biasSites), as.data.frame(raster::extract(pred, biasSites)))
colnames(biasBg)[1:2] <- c("Longitude", "Latitude")
biasBg <- biasBg[complete.cases(biasBg), ]
write.csv(biasBg, file.path(out_dir, "biasBg.csv"), row.names = FALSE)
log_info("biasBg.csv: ", nrow(biasBg), " effort-weighted background points -> ", out_dir)
