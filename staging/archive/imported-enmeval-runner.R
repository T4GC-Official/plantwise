# --- PART 1: SYSTEM SETUP ---
options(java.parameters = "-Xmx4g")

suppressPackageStartupMessages({
  library(rJava)
  library(terra)
  library(dismo)
  library(dplyr)
  library(ENMeval)
})

.jinit()

log_info <- function(...) {
  message(sprintf("[%s] %s", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), paste(..., collapse = "")))
}

maxent_version <- function(jar_path) {
  cmd <- c("-classpath", jar_path, "-verbose", "density.Utils")
  output <- tryCatch(
    system2("javap", args = cmd, stdout = TRUE, stderr = TRUE),
    error = function(e) character(0)
  )
  if (length(output) == 0) return(NA_character_)

  for (i in seq_along(output)) {
    line <- output[[i]]
    if (grepl("putstatic .*Field version:Ljava/lang/String;", line)) {
      prev <- if (i > 1) output[[i - 1]] else ""
      if (grepl("String ", prev, fixed = TRUE)) {
        return(sub("^.*String ", "", prev))
      }
    }
  }

  version_matches <- regmatches(
    output,
    regexec("using Maxent version ([0-9.]+)", output, ignore.case = TRUE)
  )
  for (match in version_matches) {
    if (length(match) > 1) return(match[[2]])
  }

  NA_character_
}

parse_args <- function(args) {
  parsed <- list()
  for (arg in args) {
    if (!startsWith(arg, "--")) next
    kv <- strsplit(sub("^--", "", arg), "=", fixed = TRUE)[[1]]
    key <- kv[1]
    value <- if (length(kv) > 1) paste(kv[-1], collapse = "=") else "TRUE"
    parsed[[key]] <- value
  }
  parsed
}

script_arg <- grep("^--file=", commandArgs(), value = TRUE)
script_dir <- if (length(script_arg) > 0) {
  dirname(normalizePath(sub("^--file=", "", script_arg[1])))
} else {
  normalizePath(getwd())
}
repo_root <- normalizePath(file.path(script_dir, "..", ".."))   # models/enmeval -> repo
runs_root <- Sys.getenv("PLANTWISE_RUNS", file.path(repo_root, "runs"))
args <- parse_args(commandArgs(trailingOnly = TRUE))

species_csv <- normalizePath(
  if (!is.null(args$species_csv)) args$species_csv else file.path(repo_root, "data", "occurrences", "filtered_species_output.csv"),
  mustWork = FALSE
)
tif_folder <- normalizePath(
  if (!is.null(args$tif_folder)) args$tif_folder else file.path(repo_root, "data", "attributes"),
  mustWork = FALSE
)
boundary_shp <- normalizePath(
  if (!is.null(args$boundary_shp)) args$boundary_shp else file.path(repo_root, "data", "boundary", "wg_boundary.shp"),
  mustWork = FALSE
)
output_dir <- normalizePath(
  if (!is.null(args$output_dir)) args$output_dir else file.path(runs_root, "enmeval", "adhoc"),
  mustWork = FALSE
)
maxent_jar <- normalizePath(
  if (!is.null(args$maxent_jar)) args$maxent_jar else file.path(repo_root, "models", "maxent", "maxent.jar"),
  mustWork = FALSE
)
background_n <- as.integer(if (!is.null(args$background_n)) args$background_n else "10000")
species_count <- as.integer(if (!is.null(args$species_count)) args$species_count else "10")
seed <- as.integer(if (!is.null(args$seed)) args$seed else "123")
species_arg <- if (!is.null(args$species)) trimws(unlist(strsplit(args$species, ","))) else character(0)
# Benchmark controls (added 2026-09-09). Defaults reproduce the scaffold's
# behaviour (spatial block CV, fc L/LQ, rm 1/2).
#   --partitions=block|randomkfold|testing   "testing" = one random hold-out of
#                                            --test_frac, i.e. Maxent's randomtestpoints=30
#   --seed also drives the background draw and the hold-out split
partitions_arg <- if (!is.null(args$partitions)) args$partitions else "block"
test_frac <- as.numeric(if (!is.null(args$test_frac)) args$test_frac else "0.3")
kfolds <- as.integer(if (!is.null(args$kfolds)) args$kfolds else "5")
fc_arg <- if (!is.null(args$fc)) trimws(unlist(strsplit(args$fc, ","))) else c("L", "LQ")
rm_arg <- as.numeric(if (!is.null(args$rm)) trimws(unlist(strsplit(args$rm, ","))) else c("1", "2"))
write_maps <- !is.null(args$write_maps) && args$write_maps %in% c("1", "TRUE", "true")
metrics_name <- if (!is.null(args$metrics_name)) args$metrics_name else "Master_Metrics_10_Species.csv"

if (!file.exists(species_csv)) stop("Species CSV not found: ", species_csv)
if (!dir.exists(tif_folder)) stop("TIF folder not found: ", tif_folder)
if (!file.exists(boundary_shp)) stop("Boundary shapefile not found: ", boundary_shp)
if (!file.exists(maxent_jar)) stop("maxent.jar not found: ", maxent_jar)

log_info("Script directory: ", script_dir)
log_info("Repository root: ", repo_root)
log_info("Species CSV: ", species_csv)
log_info("TIF folder: ", tif_folder)
log_info("Boundary shapefile: ", boundary_shp)
log_info("Output directory: ", output_dir)
log_info("maxent.jar: ", maxent_jar)
jar_version <- maxent_version(maxent_jar)
if (is.na(jar_version)) {
  log_info("Maxent version: unavailable (could not inspect jar with javap)")
} else {
  log_info("Maxent version: ", jar_version)
}

# Ensure dismo can locate maxent.jar.
dismo_java_dir <- system.file("java", package = "dismo")
if (nchar(dismo_java_dir) == 0) {
  stop("Could not locate the dismo package java directory.")
}
dismo_jar <- file.path(dismo_java_dir, "maxent.jar")
if (!file.exists(dismo_jar)) {
  copied <- file.copy(maxent_jar, dismo_jar, overwrite = TRUE)
  if (!copied) {
    stop("Failed to copy maxent.jar into dismo java directory: ", dismo_java_dir)
  }
  log_info("Copied maxent.jar into dismo java directory: ", dismo_jar)
}

# --- PART 2: INPUT DATA ---
occ_final <- read.csv(species_csv)
required_cols <- c("Species", "Latitude", "Longitude")
missing_cols <- setdiff(required_cols, names(occ_final))
if (length(missing_cols) > 0) {
  stop("Species CSV is missing required columns: ", paste(missing_cols, collapse = ", "))
}

bio_tif_pattern <- "^wc2\\.1_30s_bio_([1-9]|1[0-9])_fc\\.tif$"
tif_list <- sort(list.files(path = tif_folder, pattern = bio_tif_pattern, full.names = TRUE))
if (length(tif_list) != 19) {
  stop(
    "Expected exactly 19 BIO tif files in ", tif_folder,
    " but found ", length(tif_list), "."
  )
}

log_info("Loaded occurrence rows: ", nrow(occ_final), " across ", length(unique(occ_final$Species)), " species")
log_info("Using ", length(tif_list), " environmental layers")

# --- PART 3: ENVIRONMENT SETUP ---
bioclim_raw <- terra::rast(tif_list)
wg_shape <- terra::vect(boundary_shp)
wg_shape <- terra::project(wg_shape, crs(bioclim_raw))
predictors <- terra::crop(bioclim_raw, wg_shape, mask = TRUE)
names(predictors) <- paste0("BIO", 1:19)

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

if (!is.null(args$bg_csv)) {
  # Effort-weighted background from build_bias_layer.R (the developer's
  # bias layer). This is the `bias_sites` the original script expected.
  bias_sites <- read.csv(args$bg_csv)[, c("Longitude", "Latitude")]
  log_info("Loaded ", nrow(bias_sites), " background points from ", args$bg_csv)
} else {
  # Random background points from the masked study area (seeded). Scaffold
  # behaviour, kept as the no-bias control.
  set.seed(seed)
  bg_points <- terra::spatSample(
    predictors[[1]],
    size = background_n,
    method = "random",
    na.rm = TRUE,
    as.points = TRUE,
    values = FALSE
  )
  bias_sites <- as.data.frame(terra::crds(bg_points))
  names(bias_sites) <- c("Longitude", "Latitude")
  log_info("Generated ", nrow(bias_sites), " random background points from the masked predictor extent")
}

# --- PART 4: SELECT SPECIES TO RUN ---
all_sp_names <- sort(unique(occ_final$Species))
if (length(species_arg) > 0) {
  missing_species <- setdiff(species_arg, all_sp_names)
  if (length(missing_species) > 0) {
    stop("Requested species not found in dataset: ", paste(missing_species, collapse = ", "))
  }
  selected_species <- species_arg
} else {
  set.seed(seed)
  selected_species <- sample(all_sp_names, min(species_count, length(all_sp_names)))
}

log_info("Selected ", length(selected_species), " species: ", paste(selected_species, collapse = ", "))

# --- PART 5: RUN SCAFFOLD ---
master_metrics <- list()

for (i in seq_along(selected_species)) {
  sp_name <- selected_species[[i]]
  sp_occ <- as.data.frame(occ_final[occ_final$Species == sp_name, c("Longitude", "Latitude")])
  # One record per grid cell BEFORE any split, so the held-out set never shares
  # a cell with training data. This is what Maxent's removeduplicates does in
  # v0 and what ENMeval would do after the split otherwise.
  n_raw <- nrow(sp_occ)
  sp_occ <- sp_occ[!duplicated(terra::cellFromXY(predictors[[1]], as.matrix(sp_occ))), ]
  # Drop records on masked / no-data cells (Maxent drops these too); ENMeval
  # refuses NA predictor values in a hold-out set.
  occ_vals <- terra::extract(predictors, as.matrix(sp_occ))
  sp_occ <- sp_occ[stats::complete.cases(occ_vals), ]
  log_info(">>> [", i, "/", length(selected_species), "] Processing ", sp_name, " with ", nrow(sp_occ), " presence points (", n_raw, " raw)")

  tryCatch({
    set.seed(seed)
    occs_test <- NULL
    part_settings <- NULL
    sp_train <- sp_occ
    if (partitions_arg == "testing") {
      n_test <- max(1L, as.integer(round(nrow(sp_occ) * test_frac)))
      test_idx <- sample(seq_len(nrow(sp_occ)), n_test)
      occs_test <- sp_occ[test_idx, ]
      sp_train <- sp_occ[-test_idx, ]
    } else if (partitions_arg == "randomkfold") {
      part_settings <- list(kfolds = kfolds)
    }
    log_info("Partition=", partitions_arg, " train=", nrow(sp_train),
             " test=", if (is.null(occs_test)) "cv" else nrow(occs_test),
             " seed=", seed, " fc=", paste(fc_arg, collapse = "/"),
             " rm=", paste(rm_arg, collapse = "/"))
    t0 <- Sys.time()
    eval_results <- ENMevaluate(
      occs = sp_train,
      envs = predictors,
      bg = bias_sites,
      algorithm = "maxent.jar",
      partitions = partitions_arg,
      partition.settings = part_settings,
      occs.testing = occs_test,
      tune.args = list(fc = fc_arg, rm = rm_arg),
      parallel = FALSE,
      quiet = TRUE
    )
    fit_secs <- as.numeric(difftime(Sys.time(), t0, units = "secs"))

    res_table <- eval_results@results
    # partitions="testing" reports a single hold-out score as auc.val / or.10p;
    # the CV modes report *.avg / *.sd. Normalise so downstream code sees both.
    for (m in c("auc.val", "auc.diff", "cbi.val", "or.mtp", "or.10p")) {
      if (m %in% names(res_table) && !(paste0(m, ".avg") %in% names(res_table))) {
        res_table[[paste0(m, ".avg")]] <- res_table[[m]]
        res_table[[paste0(m, ".sd")]] <- NA_real_
      }
    }
    best_idx <- which(res_table$delta.AICc == 0)[1]
    best_model <- eval_results@models[[best_idx]]
    prediction <- terra::predict(predictors, best_model)

    file_name <- gsub(" ", "_", sp_name)
    tif_path <- file.path(output_dir, paste0(file_name, "_SDM.tif"))
    png_path <- file.path(output_dir, paste0(file_name, "_Plot.png"))

    if (write_maps) {
      terra::writeRaster(prediction, tif_path, overwrite = TRUE)
      png(png_path, width = 600, height = 800)
      terra::plot(prediction, main = sp_name, col = terrain.colors(100))
      dev.off()
    }

    all_tunes <- res_table
    all_tunes$species <- sp_name
    all_tunes$seed <- seed
    all_tunes$partitions <- partitions_arg
    write.csv(all_tunes, file.path(output_dir, paste0(file_name, "_all_tunes.csv")), row.names = FALSE)

    current_metrics <- res_table[best_idx, ]
    current_metrics$species <- sp_name
    current_metrics$seed <- seed
    current_metrics$partitions <- partitions_arg
    current_metrics$background <- if (is.null(args$bg_csv)) "random" else basename(args$bg_csv)
    current_metrics$n_raw <- n_raw
    current_metrics$n_occ <- nrow(sp_occ)
    current_metrics$n_train <- nrow(sp_train)
    current_metrics$n_test <- if (is.null(occs_test)) NA_integer_ else nrow(occs_test)
    current_metrics$fit_secs <- round(fit_secs, 1)
    master_metrics[[length(master_metrics) + 1]] <- current_metrics

    log_info(
      "SUCCESS ", sp_name,
      " | train AUC=", round(as.numeric(current_metrics$auc.train), 3),
      " | val AUC=", round(as.numeric(current_metrics$auc.val.avg), 3),
      " | secs=", round(fit_secs),
      " | best tune=", current_metrics$tune.args,
      " | tif=", tif_path
    )
  }, error = function(e) {
    log_info("FAILED ", sp_name, " - ", e$message)
  })
}

final_table <- bind_rows(master_metrics)
metrics_path <- file.path(output_dir, metrics_name)
write.csv(final_table, metrics_path, row.names = FALSE)
log_info("Wrote metrics CSV: ", metrics_path, " (", nrow(final_table), " successful species)")
