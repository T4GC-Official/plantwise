# --- PART 1: SYSTEM SETUP ---
options(java.parameters = "-Xmx4g")
library(rJava)
.jinit() 
library(terra)
library(dismo)
library(dplyr)
library(ENMeval)

# --- PART 2: THE ENVIRONMENT ---

# 1. Set your main working folder
base_path <- "C:/New folder/sharvani_sdm_working_folder/"
setwd(base_path)

# 2. Point directly to your TIF folder
tif_folder <- "C:/New folder/sharvani_sdm_working_folder/climate/wc2.1_30s/"

# 3. Load all 19 files directly from that folder
tif_list <- list.files(path = tif_folder, pattern = "\\.tif$", full.names = TRUE)
tif_list <- sort(tif_list) # Ensures correct order

if(length(tif_list) == 0) {
  stop("Error: No .tif files found in the folder. Please check the path!")
}

# Load as a SpatRaster (The terra format)
bioclim_raw <- terra::rast(tif_list)

# 4. Load & Align Western Ghats Shapefile
# Use your shapefile to "cookie-cutter" the climate data
wg_shape <- terra::vect("wg_boundary.shp") 
wg_shape <- terra::project(wg_shape, crs(bioclim_raw))

# 5. CROP AND MASK (western ghats boundary selected)
predictors <- terra::crop(bioclim_raw, wg_shape, mask = TRUE)
names(predictors) <- paste0("BIO", 1:19) # Standardize names forever

# Verify the map
plot(predictors[[1]], main="Western Ghats: BIO1")

# --- PART 5: 10 RANDOM SPECIES RUN ---

if(!dir.exists("Batch_Results")) dir.create("Batch_Results")

set.seed(123)
all_sp_names <- unique(occ_final$Species)
random_10 <- sample(all_sp_names, 10)

master_metrics <- list()

for (i in 1:length(random_10)) {
  sp_name <- random_10[i]
  message(paste(">>> Processing Species", i, ":", sp_name))
  
  tryCatch({
    sp_occ <- as.data.frame(occ_final[occ_final$Species == sp_name, c("Longitude", "Latitude")])
    
    # Run ENMeval (Terra compatible)
    eval_results <- ENMevaluate(
      occs = sp_occ, envs = predictors, bg = bias_sites,
      algorithm = 'maxent.jar', partitions = 'block',
      tune.args = list(fc = c("L", "LQ"), rm = 1:2),
      parallel = FALSE
    )
    
    # Selection & Prediction
    res_table <- eval_results@results
    best_idx <- which(res_table$delta.AICc == 0)[1]
    best_model <- eval_results@models[[best_idx]]
    prediction <- terra::predict(predictors, best_model)
    
    # Save Outputs
    file_name <- gsub(" ", "_", sp_name)
    terra::writeRaster(prediction, paste0("Batch_Results/", file_name, "_SDM.tif"), overwrite=TRUE)
    
    png(paste0("Batch_Results/", file_name, "_Plot.png"), width=600, height=800)
    terra::plot(prediction, main=sp_name, col=terrain.colors(100))
    dev.off()
    
    # Collect Metrics
    current_metrics <- res_table[best_idx, ]
    current_metrics$species <- sp_name
    master_metrics[[i]] <- current_metrics
    
    message(paste("Success! Training AUC:", round(as.numeric(current_metrics$auc.train), 3)))
    
  }, error = function(e) {
    message(paste("FAILED:", sp_name, "-", e$message))
  })
}

# SAVE MASTER CSV
final_table <- bind_rows(master_metrics)
write.csv(final_table, "Batch_Results/Master_Metrics_10_Species.csv", row.names = FALSE)
