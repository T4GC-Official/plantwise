"""Read-only all-species attribution for a captured live/staging query pair."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import hashlib
import json
import os
import math
import httpx
import pandas as pd
import rasterio
from rasterio.warp import transform
from shapely.geometry import Point, shape
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('PLANTWISE_COMPARISON_DIR',ROOT/'runtime/comparison-20261112-kodagu'))
ARCHIVE=ROOT.parent/'archive/plantwise_v0'
LAT=12.189703804004086; LON=75.94048174979808; THRESHOLD=50

def read(name):return json.loads((OUT/name).read_text())
def keyed(name):return {x['species']:x for x in read(name)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

release=(ROOT/'runtime/active').resolve(strict=True)
catalog=json.loads((release/'catalog.json').read_text())
health=httpx.get('http://127.0.0.1:8175/api/health').json();assert health['release']==catalog['release']
(OUT/'staging-health.json').write_text(json.dumps(health,indent=2))
states={x['species']:x for x in json.loads((release/'accounting.json').read_text())}
occ=pd.read_csv(ROOT/'data/occurrences/filtered_species_output.csv')
inv=pd.read_csv(ARCHIVE/'source_occurrence_inventory.csv').set_index('species')
auc=pd.read_csv(ARCHIVE/'container/auc_and_contributions.csv').set_index('Species')
assert auc.index.is_unique
bounds=occ.groupby('Species').agg(lat_min=('Latitude','min'),lat_max=('Latitude','max'))
features=json.loads((release/'boundary.geojson').read_text())
wg=unary_union([shape(f['geometry']) for f in features['features']]);inside_wg=wg.covers(Point(LON,LAT))
L=keyed('live-threshold-50.json');S=keyed('staging-threshold-50.json');L0=keyed('live-threshold-0.json');S0=keyed('staging-threshold-0.json')
rows=[]
for sp in sorted(set(inv.index)|set(states)|set(L0)|set(S0)):
    state=states.get(sp,{});entry=catalog['species'].get(sp);ib=sp in bounds.index
    lat_min=float(bounds.loc[sp,'lat_min']) if ib else None;lat_max=float(bounds.loc[sp,'lat_max']) if ib else None
    in_lat=lat_min<=LAT<=lat_max if ib else None
    historic_tif=bool(inv.loc[sp,'has_original_production_tif']) if sp in inv.index else None
    historic_auc=sp in auc.index
    score=None;valid=None;cellrow=None;cellcol=None;nodata=None;crs=None
    if entry:
        with rasterio.open(release/entry['raster']) as src:
            x,y=transform('EPSG:4326',src.crs,[LON],[LAT]);cellrow,cellcol=src.index(x[0],y[0]);crs=str(src.crs);nodata=src.nodata
            valid=False
            if 0<=cellrow<src.height and 0<=cellcol<src.width:
                v=src.read(1,window=((cellrow,cellrow+1),(cellcol,cellcol+1)),masked=True)[0,0]
                if not getattr(v,'mask',False):
                    v=float(v)
                    if math.isfinite(v) and 0<=v<=1:score=v;valid=True
    if not ib:stage_reason='outside_selected_448_input'
    elif state.get('status')!='success':stage_reason=state.get('classification',state.get('status','no_terminal_status'))
    elif not inside_wg:stage_reason='outside_wg'
    elif not in_lat:stage_reason='outside_latitude_envelope'
    elif not valid:stage_reason='invalid_or_nodata_pixel'
    elif score*100<THRESHOLD:stage_reason='below_50_percent'
    else:stage_reason='returned'
    expected=stage_reason=='returned';assert expected==(sp in S),sp
    if sp in S:assert abs(S[sp]['probability']/100-score)<1e-8
    if sp in S0:assert entry and in_lat and valid
    live_percent=L0.get(sp,{}).get('probability')
    if sp in L:live_reason='returned'
    elif sp in L0:
        assert live_percent<THRESHOLD
        live_reason='below_50_percent_confirmed_by_live_zero_threshold'
    elif not historic_tif:live_reason='no_historical_production_tif_current_deployment_inventory_unverified'
    elif not historic_auc:live_reason='missing_archived_auc_row_archived_serving_gate'
    elif in_lat is False:live_reason='outside_shared_latitude_envelope_consistent_with_live_zero_threshold'
    else:live_reason='unresolved_current_inventory_or_pixel_or_other_filter'
    row={'species':sp,'in_selected_input':ib,'staging_status':state.get('status','not_in_selected_input'),'staging_classification':state.get('classification'),'raw_occurrences':state.get('occurrence_counts',{}).get('raw'),'usable_cells':state.get('occurrence_counts',{}).get('unique_cell'),'latitude_min':lat_min,'latitude_max':lat_max,'query_within_latitude_bounds':in_lat,'query_inside_wg':inside_wg,'staging_pixel_valid':valid,'staging_pixel_score':score,'staging_percent':score*100 if score is not None else None,'staging_returned_50':sp in S,'staging_returned_0':sp in S0,'staging_reason':stage_reason,'historical_original_tif_present':historic_tif,'archived_auc_row_present':historic_auc,'archived_auc':float(auc.loc[sp,'Test AUC']) if historic_auc else None,'archived_bio20_percent_contribution':float(auc.loc[sp,'wc2.1_30s_bio_20_fc']) if historic_auc else None,'live_reported_integer_percent_at_0':live_percent,'live_reported_percent_at_50':L.get(sp,{}).get('probability'),'live_returned_50':sp in L,'live_returned_0':sp in L0,'live_absence_reason_or_evidence':live_reason,'raster_row':cellrow,'raster_col':cellcol,'raster_crs':crs,'raster_nodata':nodata}
    if entry:
        m=pd.read_csv(ROOT/'runs'/catalog['release']/sp/'metrics.csv').iloc[0]
        row.update(selected_fc=m.fc,selected_rm=float(m.rm),selected_ncoef=int(m.ncoef),block_cv_auc=float(m['auc.val.avg']),n_final=int(m.n_final))
    rows.append(row)
frame=pd.DataFrame(rows);union=frame[frame.species.isin(set(L)|set(S))]
frame.to_csv(OUT/'all-species-diagnostics.csv',index=False);union.to_csv(OUT/'response-union-comparison.csv',index=False)
frame[frame.staging_status=='excluded'].to_csv(OUT/'all-180-exclusions-at-query.csv',index=False)
expected_legacy=set(frame[(frame.historical_original_tif_present==True)&(frame.archived_auc_row_present==True)&(frame.query_within_latitude_bounds==True)].species)
assert expected_legacy==set(L0)
original_context=json.loads((ARCHIVE/'SOURCE_PROVENANCE.json').read_text());integrity={}
for filename,want in original_context['shared_inputs']['selected_bio_tiffs_sha256'].items():
    got=sha(ROOT/'data/attributes'/filename);assert got==want;integrity[filename]=got
for filename,want in original_context['shared_inputs']['wg_shapefile_sha256'].items():
    got=sha(ROOT/'data/boundary'/filename);assert got==want;integrity[filename]=got
for key,path in [('maxent_jar_sha256',ROOT/'models/maxent/maxent.jar'),('selected_occurrence_csv_sha256',ROOT/'data/occurrences/filtered_species_output.csv'),('frontend_geojson_sha256',ROOT/'frontend/public/wgg.geojsonl.json')]:
    got=sha(path);assert got==original_context['shared_inputs'][key];integrity[key]=got
climate={}
for i in range(1,20):
    with rasterio.open(ROOT/f'data/attributes/wc2.1_30s_bio_{i}_fc.tif') as src:
        value=next(src.sample([(LON,LAT)],masked=True))[0];assert not getattr(value,'mask',False) and math.isfinite(float(value));climate[f'BIO{i}']=float(value)
priority=['Drypetes_venusta','Alseodaphne_semecarpifolia','Croton_zeylanicus','Clausena_anisata']
full_files=[f'container/tif_data_final/{sp}.tif' for sp in sorted(set(union[union.staging_status=='success'].species))]
manifest={'priority_original_production_tiffs':[f'container/tif_data_final/{sp}.tif' for sp in priority],'remaining_original_production_tiffs_for_all_24_paired_models':[f for f in full_files if f not in [f'container/tif_data_final/{sp}.tif' for sp in priority]],'optional_excluded_species_original_tiffs':[f'container/tif_data_final/{sp}.tif' for sp in sorted(set(L)-set(catalog['species']))],'additional_provenance_if_available':'Corresponding original production Maxent HTML/lambdas/logs/settings, only if linked to these exact TIFFs; no unrelated March reruns.'}
(OUT/'selective-transfer-manifest.json').write_text(json.dumps(manifest,indent=2))
summary={'captured_at':datetime.now(timezone.utc).isoformat(),'coordinate':{'latitude':LAT,'longitude':LON},'threshold_percent':50,'release':catalog['release'],'release_accounting':health['coverage'],'live_count_50':len(L),'staging_count_50':len(S),'shared':sorted(set(L)&set(S)),'live_only':sorted(set(L)-set(S)),'staging_only':sorted(set(S)-set(L)),'live_count_0':len(L0),'staging_count_0':len(S0),'historical_tif_auc_lat_expected_count':len(expected_legacy),'live_zero_exactly_matches_archived_tif_auc_lat_inventory':expected_legacy==set(L0),'staging_all_448_reasons':dict(Counter(frame[frame.in_selected_input].staging_reason)),'all_268_active_rasters_valid_at_query':bool(frame[frame.staging_status=='success'].staging_pixel_valid.all()),'union_all_inside_latitude_bounds':bool(union.query_within_latitude_bounds.all()),'query_inside_wg':inside_wg,'union_all_have_historical_tif_and_auc':bool(union.historical_original_tif_present.all() and union.archived_auc_row_present.all()),'staging_only_all_present_live_threshold_zero':set(S)-set(L)<=set(L0),'historical_tif_auc_excluded_by_latitude':int(((frame.historical_original_tif_present==True)&(frame.archived_auc_row_present==True)&(frame.query_within_latitude_bounds==False)).sum()),'historical_tif_missing_auc_count':int(((frame.historical_original_tif_present==True)&(frame.archived_auc_row_present==False)).sum()),'live_zero_species_excluded_from_staging':int(((frame.live_returned_0==True)&(frame.staging_status=='excluded')).sum()),'union_bio20_report_nonzero':int((union.archived_bio20_percent_contribution>0).sum()),'staging_50_auc_below_half':int((union[union.staging_returned_50].block_cv_auc<.5).sum()),'source_integrity':integrity,'climate_at_query':climate,'source_hashes':{str(p.relative_to(ROOT.parent)):sha(p) for p in [ARCHIVE/'container/app.py',ARCHIVE/'InitialImplementation.py',ROOT/'backend/app.py',ROOT/'models/enmeval/train.R']}}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k not in ('source_integrity','climate_at_query','source_hashes')},indent=2))
