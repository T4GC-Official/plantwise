# Reload saved models in a fresh JVM; prove no ephemeral Maxent path is required.
suppressPackageStartupMessages({library(rJava);library(terra);library(predicts);library(jsonlite);library(digest)})
args <- commandArgs(TRUE); release <- normalizePath(args[1]); root <- '/work'
jar <- file.path(system.file('java',package='predicts'),'maxent.jar'); supplied<-file.path(root,'models/maxent/maxent.jar')
stopifnot(file.copy(supplied,jar,overwrite=TRUE)); stopifnot(predicts::MaxEnt(silent=TRUE))
catalog<-read_json(file.path(release,'catalog.json'),simplifyVector=FALSE)
pred<-rast(file.path(root,'data/attributes',sprintf('wc2.1_30s_bio_%d_fc.tif',1:19)));names(pred)<-paste0('BIO',1:19)
occ<-read.csv(file.path(root,'data/occurrences/filtered_species_output.csv'))
checks<-list()
for(sp in names(catalog$species)) {
 entry<-catalog$species[[sp]]; model<-readRDS(file.path(release,entry$model))
 stopifnot(nrow(model@presence)==entry$n_final)
 xy<-as.matrix(occ[occ$Species==sp,c('Longitude','Latitude')]); values<-as.data.frame(terra::extract(pred,xy)); map<-rast(file.path(release,entry$raster)); scores<-terra::extract(map,xy)[,1]
 keep<-which(complete.cases(values)&is.finite(scores));stopifnot(length(keep)>0)
 direct<-as.numeric(predicts::predict(model,values[keep,,drop=FALSE],args='outputformat=cloglog'))
 error<-max(abs(direct-scores[keep]));stopifnot(is.finite(error),error<1e-6)
 checks[[sp]]<-list(n_final=nrow(model@presence),checked=length(keep),max_error=error)
}
write_json(list(release=catalog$release,passed=TRUE,models=checks),args[2],auto_unbox=TRUE,pretty=TRUE,digits=NA)
cat('Fresh-JVM model reload passed:',length(checks),'models\n')
