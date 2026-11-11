# Isolated, one-species, bias-only ENMeval job. Status is the completion marker.
options(java.parameters = '-Xmx4g')
suppressPackageStartupMessages({library(rJava); library(terra); library(dismo); library(predicts); library(ENMeval); library(jsonlite); library(digest)})
a <- list()
for (x in commandArgs(TRUE)) { kv <- strsplit(sub('^--', '', x), '=', fixed=TRUE)[[1]]; a[[kv[1]]] <- paste(kv[-1], collapse='=') }
g <- function(k,d) if(is.null(a[[k]])) d else a[[k]]
root <- normalizePath(g('root','/work'))
out <- g('output_dir', stop('output_dir required'))
# The orchestrator supplies a fresh directory per attempt, never overwriting results.
dir.create(out, recursive=TRUE, showWarnings=FALSE)
atomic_json <- function(x, path) { tmp <- paste0(path,'.tmp'); write_json(x,tmp,auto_unbox=TRUE,pretty=TRUE,na='null'); stopifnot(file.rename(tmp,path)) }
sp <- g('species','Aglaia_lawii')
stopifnot(grepl('^[A-Za-z][A-Za-z0-9_]+$',sp), !file.exists(file.path(out,'status.json')))
status <- list(species=sp,status='running',started=format(Sys.time(),tz='UTC',usetz=TRUE))
atomic_json(status,file.path(out,'status.json'))
t0 <- Sys.time()
exit_code <- 0L
tryCatch({
 seed <- as.integer(g('seed','123')); set.seed(seed)
 terraOptions(memfrac=0.15, progress=0, tempdir=out)
 paths <- list(occ=g('species_csv',file.path(root,'data/occurrences/filtered_species_output.csv')),
  boundary=g('boundary_shp',file.path(root,'data/boundary/wg_boundary.shp')),
  bg=g('bg_csv',file.path(root,'data/derived/bias_layer/biasBg.csv')),
  jar=g('maxent_jar',file.path(root,'models/maxent/maxent.jar')))
 files <- file.path(g('tif_folder',file.path(root,'data/attributes')),sprintf('wc2.1_30s_bio_%d_fc.tif',1:19))
 stopifnot(all(file.exists(c(unlist(paths),files))))
 # ENMeval 2.0.5.2 dispatches through predicts; use its isolated Java library.
 hash <- function(p) digest(file=p,algo='sha256')
 loaded_jar <- file.path(system.file('java',package='predicts'),'maxent.jar')
 if (!file.exists(loaded_jar) || !identical(hash(paths$jar),hash(loaded_jar))) stopifnot(file.copy(paths$jar,loaded_jar,overwrite=TRUE))
 stopifnot(identical(hash(paths$jar),hash(loaded_jar)))
 stopifnot(predicts::MaxEnt(silent=TRUE))
 actual_jar <- rJava::.jcall(rJava::.jcall(rJava::.jcall(rJava::.jnew('density.MaxEnt'),'Ljava/lang/Class;','getClass'),'Ljava/security/ProtectionDomain;','getProtectionDomain'),'Ljava/security/CodeSource;','getCodeSource')
 jar_url <- rJava::.jcall(rJava::.jcall(actual_jar,'Ljava/net/URL;','getLocation'),'S','toString')
 stopifnot(identical(normalizePath(URLdecode(sub('^file:', '', jar_url))),normalizePath(loaded_jar))))
 pred <- rast(files); boundary <- project(vect(paths$boundary),crs(pred)); pred <- crop(pred,boundary,mask=TRUE); names(pred)<-paste0('BIO',1:19); stopifnot(terra::is.lonlat(pred))
 filter_points <- function(df) {
  xy <- data.frame(Longitude=suppressWarnings(as.numeric(df$Longitude)),Latitude=suppressWarnings(as.numeric(df$Latitude)))
  counts <- list(raw=nrow(xy))
  xy <- xy[is.finite(xy$Longitude)&is.finite(xy$Latitude)&abs(xy$Longitude)<=180&abs(xy$Latitude)<=90,,drop=FALSE]; counts$finite<-nrow(xy)
  original_valid <- xy
  if(nrow(xy)) { inside<-!is.na(terra::extract(boundary,terra::vect(xy,geom=c('Longitude','Latitude'),crs='EPSG:4326'))[,2]); xy<-xy[inside,,drop=FALSE] }
  counts$in_boundary<-nrow(xy)
  if(nrow(xy)) xy<-xy[apply(as.matrix(terra::extract(pred,as.matrix(xy))),1,function(v) all(is.finite(v))),,drop=FALSE]
  counts$complete_case<-nrow(xy)
  if(nrow(xy)) xy<-xy[!duplicated(cellFromXY(pred,as.matrix(xy))),,drop=FALSE]
  counts$unique_cell<-nrow(xy)
  list(xy=xy,counts=counts,original_valid=original_valid)
 }
 occ <- read.csv(paths$occ); stopifnot(nrow(occ)==14180,length(unique(occ$Species))==448,sp %in% occ$Species)
 o <- filter_points(occ[occ$Species==sp,]); b <- filter_points(read.csv(paths$bg))
 status$occurrence_counts <- o$counts; status$background_counts <- b$counts
 # Background sampling multiplicities are part of the supplied sampling policy;
 # retain them after coordinate/WG/complete-case validation (ENMeval deduplicates).
 bg_raw <- read.csv(paths$bg)[,c('Longitude','Latitude')]
 bg <- bg_raw[is.finite(bg_raw$Longitude)&is.finite(bg_raw$Latitude),,drop=FALSE]
 bg <- bg[!is.na(terra::extract(boundary,terra::vect(bg,geom=c('Longitude','Latitude'),crs='EPSG:4326'))[,2]),,drop=FALSE]
 bg <- bg[apply(as.matrix(terra::extract(pred,as.matrix(bg))),1,function(v) all(is.finite(v))),,drop=FALSE]
 status$background_counts$retained<-nrow(bg)
 if(nrow(o$xy)<8) { status$status<-'excluded'; status$reason<-'insufficient_unique_cells_for_four_block_cv_minimum_8'; exit_code<-0L } else {
  groups <- tryCatch(ENMeval::get.block(o$xy,bg),error=function(e) stop('partition_failure: ',conditionMessage(e)))
  status$fold_counts <- as.list(table(groups$occs.grp))
  if(length(unique(groups$occs.grp))!=4 || any(table(groups$occs.grp)<2)) stop('partition_failure: require four blocks each with >=2 validation presences')
  result <- ENMeval::ENMevaluate(occs=o$xy,envs=pred,bg=bg,algorithm='maxent.jar',partitions='block',
   tune.args=list(fc=c('L','LQ'),rm=c(1,2)), parallel=FALSE,quiet=FALSE,
   other.settings=list(pred.type='cloglog'))
  tab <- result@results
  write.csv(tab,file.path(out,paste0(sp,'_all_tunes.csv')),row.names=FALSE)
  eligible <- which(is.finite(tab$AICc)&is.finite(tab$auc.val.avg)&is.finite(tab$ncoef)&tab$ncoef < nrow(o$xy)-1)
  if(!length(eligible)) stop('no_AICc_eligible_model: finite AICc, held-out AUC and ncoef < n-1 required')
  best <- eligible[order(tab$AICc[eligible],tab$ncoef[eligible],tab$fc[eligible],tab$rm[eligible])][1]
  model <- result@models[[best]]
  # ENMeval's full models retain all presences; reject partial fit.
  stopifnot(nrow(model@presence)==nrow(o$xy))
  saveRDS(model,file.path(out,paste0(sp,'_model.rds')))
  saveRDS(result,file.path(out,paste0(sp,'_evaluation.rds')))
  # Explicit dismo dispatch for S4 MaxEnt, explicitly request cloglog.
  predict_cloglog <- function(model,data,...) predicts::predict(model,as.data.frame(data),args='outputformat=cloglog')
  map <- terra::predict(pred,model,fun=predict_cloglog,na.rm=TRUE,filename=file.path(out,paste0(sp,'_SDM.tif')),overwrite=FALSE,wopt=list(gdal=c('COMPRESS=DEFLATE'),NAflag=-9999))
  bounds <- global(map,c('min','max'),na.rm=TRUE); stopifnot(all(is.finite(as.matrix(bounds))),bounds$min>=0,bounds$max<=1)
  check <- as.numeric(predicts::predict(model,as.data.frame(terra::extract(pred,as.matrix(o$xy))),args='outputformat=cloglog'))
  sampled <- as.numeric(terra::extract(map,as.matrix(o$xy))[,1]); stopifnot(max(abs(check-sampled))<1e-6)
  png(file.path(out,paste0(sp,'_Plot.png')),width=600,height=800); plot(map,main=paste(sp,'ENMeval Maxent cloglog'),col=hcl.colors(100,'YlGn')); dev.off()
  metrics <- tab[best,,drop=FALSE]; metrics$species<-sp; metrics$n_raw<-o$counts$raw; metrics$n_occ<-nrow(o$xy); metrics$n_final<-nrow(model@presence); metrics$seed<-seed; metrics$partitions<-'block'; metrics$background<-'supplied effort weighted'; metrics$fit_secs<-as.numeric(difftime(Sys.time(),t0,units='secs'))
  write.csv(metrics,file.path(out,'metrics.csv'),row.names=FALSE)
  status$status<-'success'; status$selected<-as.list(metrics[1,]); status$latitude_bounds<-list(min=min(o$original_valid$Latitude),max=max(o$original_valid$Latitude)); status$map_range<-as.list(bounds[1,]); status$prediction_check_max_error<-max(abs(check-sampled))
 }
 provenance <- list(seed=seed,partition='block',output_scale='cloglog',wg_mask=TRUE,jar=list(configured=paths$jar,loaded=loaded_jar,class_source=jar_url,sha256=hash(loaded_jar),version=getOption('predicts_maxent')),inputs=lapply(c(paths,as.list(setNames(files,paste0('BIO',1:19)))),function(p)list(path=p,sha256=hash(p))),packages=as.list(sapply(c('ENMeval','rJava','terra','raster','dismo','dplyr'),function(p)as.character(packageVersion(p)))))
 atomic_json(provenance,file.path(out,'provenance.json'))
 capture.output(sessionInfo(),file=file.path(out,'sessionInfo.txt'))
 write.csv(as.data.frame(installed.packages()[,c('Package','Version')]),file.path(out,'R-packages.csv'),row.names=FALSE)
},error=function(e) { status$status<<-'failed'; status$reason<<-conditionMessage(e); exit_code<<-1L; message(conditionMessage(e)) })
status$elapsed_seconds <- as.numeric(difftime(Sys.time(),t0,units='secs')); status$finished<-format(Sys.time(),tz='UTC',usetz=TRUE)
atomic_json(status,file.path(out,'status.json'))
quit(status=exit_code)
