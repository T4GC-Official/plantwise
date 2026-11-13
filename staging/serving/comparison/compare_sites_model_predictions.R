# Read-only inference on saved staging models. No fitting or service changes.
options(java.parameters='-Xmx1g')
suppressPackageStartupMessages({library(rJava);library(terra);library(predicts);library(jsonlite);library(digest)})
root <- '/work/model'; out <- '/evidence'; lat<-12.189703804004086;lon<-75.94048174979808
release<-read_json(file.path(out,'summary.json'))$release
catalog<-read_json(file.path(root,'releases',release,'catalog.json'),simplifyVector=FALSE)
jar<-file.path(system.file('java',package='predicts'),'maxent.jar');sourcejar<-file.path(root,'maxent/maxent.jar')
if(digest(file=jar,algo='sha256')!=digest(file=sourcejar,algo='sha256')) stopifnot(file.copy(sourcejar,jar,overwrite=TRUE))
stopifnot(predicts::MaxEnt(silent=TRUE),getOption('predicts_maxent')=='3.4.4')
pred<-rast(file.path(root,'data/attributes',sprintf('wc2.1_30s_bio_%d_fc.tif',1:19)));names(pred)<-paste0('BIO',1:19)
requested<-read.csv(file.path(out,'response-union-comparison.csv'))$species
checks<-list()
for(sp in requested){
 if(is.null(catalog$species[[sp]])) next
 entry<-catalog$species[[sp]];model<-readRDS(file.path(root,'releases',release,entry$model));map<-rast(file.path(root,'releases',release,entry$raster))
 cell<-cellFromXY(map,matrix(c(lon,lat),nrow=1));center<-xyFromCell(map,cell);env<-as.data.frame(terra::extract(pred,center));pixel<-as.numeric(terra::extract(map,cell)[1,1])
 cloglog<-as.numeric(predicts::predict(model,env,args='outputformat=cloglog'));logistic<-as.numeric(predicts::predict(model,env,args='outputformat=logistic'))
 stopifnot(abs(cloglog-pixel)<1e-6,nrow(model@presence)==entry$n_final)
 item<-list(model_class=class(model)[1],n_final=nrow(model@presence),pixel_center=as.list(center[1,]),raster_cloglog=pixel,reloaded_model_cloglog=cloglog,reloaded_model_logistic_same_fit=logistic,absolute_error=abs(cloglog-pixel))
 if(sp=='Chrysophyllum_flexuosum') item$whole_map_range<-as.list(terra::global(map,c('min','max'),na.rm=TRUE)[1,])
 checks[[sp]]<-item
}
write_json(list(passed=TRUE,algorithm='inference_only_no_retraining',jar_sha256=digest(file=jar,algo='sha256'),jar_version=getOption('predicts_maxent'),model_checks=checks),file.path(out,'model-inference-verification.json'),auto_unbox=TRUE,pretty=TRUE,digits=NA)
cat('Verified',length(checks),'saved models at exact query-cell centers; no fitting performed\n')
