#!/usr/bin/env python3
"""Validate every successful job and create a fresh immutable normalized release."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

import pandas as pd
from PIL import Image
import rasterio
from rasterio.features import shapes
from rasterio.warp import transform_geom
from shapely.geometry import shape, mapping
import shapefile
from pyproj import CRS, Transformer
from shapely.ops import transform as transform_shape

ROOT = Path(__file__).resolve().parents[1]

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def build(run, release_id, expected):
    target = ROOT / 'releases' / release_id
    if target.exists(): raise ValueError('Release already exists; choose a new identity')
    manifest=Path(run)/'config.json'
    states = ([Path(run)/sp/'status.json' for sp in json.loads(manifest.read_text())['species']] if manifest.exists() else sorted(Path(run).glob('*/status.json')))
    if (Path(run)/'status.json').exists(): states=[Path(run)/'status.json']
    statuses = [json.loads(p.read_text()) for p in states]
    if len(statuses)!=expected or len({s['species'] for s in statuses})!=expected:
        raise ValueError('Every requested species must have exactly one terminal status')
    if any(s['status'] not in ('success','excluded','failed') for s in statuses): raise ValueError('Unfinished jobs')
    if not any(s['status']=='success' for s in statuses): raise ValueError('No successes')
    occ=pd.read_csv(ROOT/'data/occurrences/filtered_species_output.csv')
    if expected==448 and set(occ.Species)!=set(s['species'] for s in statuses): raise ValueError('Species inventory mismatch')
    pending=ROOT/'releases'/('.building-'+release_id)
    pending.mkdir(parents=True)
    destination=target
    target=pending
    catalog={'release':release_id,'evaluation':'four-block spatial CV; ENMeval 2.0.5.2 Java Maxent; effort-weighted background; BIO1–19',
             'species':{},'accounting':{k:sum(s['status']==k for s in statuses) for k in ('success','excluded','failed')}}
    for status, file in zip(statuses,states):
        if status['status']!='success': continue
        sp=status['species']; job=file.parent
        metrics=pd.read_csv(job/'metrics.csv').iloc[0]
        assert math.isfinite(metrics['auc.val.avg']) and math.isfinite(metrics['AICc'])
        assert metrics.n_final==metrics.n_occ
        with Image.open(job/f'{sp}_Plot.png') as preview: preview.verify()
        geo=job/f'{sp}_SDM.tif'
        with rasterio.open(geo) as src:
            assert src.crs and src.nodata is not None
            lo,hi=math.inf,-math.inf
            for _,window in src.block_windows(1):
                arr=src.read(1,window=window,masked=True).compressed()
                if len(arr):
                    assert all(map(math.isfinite, (float(arr.min()),float(arr.max()))))
                    lo=min(lo,float(arr.min()));hi=max(hi,float(arr.max()))
            assert 0<=lo<=hi<=1
        d=target/sp; d.mkdir()
        for name in (f'{sp}_SDM.tif',f'{sp}_Plot.png',f'{sp}_model.rds','metrics.csv','status.json','provenance.json',f'{sp}_all_tunes.csv'):
            shutil.copy2(job/name,d/name)
        original=occ[occ.Species==sp]
        valid=original[original.Latitude.between(-90,90)&original.Longitude.between(-180,180)]
        bounds={'min':float(valid.Latitude.min()),'max':float(valid.Latitude.max())}
        assert bounds==status['latitude_bounds']
        catalog['species'][sp]={'raster':f'{sp}/{sp}_SDM.tif','preview':f'{sp}/{sp}_Plot.png','model':f'{sp}/{sp}_model.rds',
            'latitude_bounds':bounds,'auc':float(metrics['auc.val.avg']),'fc':metrics.fc,'rm':float(metrics.rm),
            'n_raw':int(metrics.n_raw),'n_usable':int(metrics.n_occ),'n_final':int(metrics.n_final)}
    # Exact supplied shapefile polygon for API; frontend asset is not an authority.
    boundary=ROOT/'data/boundary/wg_boundary.shp'
    reader=shapefile.Reader(str(boundary))
    transformer=Transformer.from_crs(CRS.from_wkt(boundary.with_suffix('.prj').read_text()),'EPSG:4326',always_xy=True)
    features=[{'type':'Feature','properties':{},'geometry':mapping(transform_shape(transformer.transform,shape(s.__geo_interface__)))} for s in reader.shapes()]
    (target/'boundary.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features}))
    (target/'accounting.json').write_text(json.dumps(statuses,indent=2))
    (target/'catalog.json').write_text(json.dumps(catalog,indent=2))
    hashes={str(p.relative_to(target)):sha(p) for p in sorted(target.rglob('*')) if p.is_file()}
    (target/'checksums.json').write_text(json.dumps(hashes,indent=2))
    target.rename(destination)
    print(destination)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('release');p.add_argument('--expected',type=int,required=True);a=p.parse_args();build(a.run,a.release,a.expected)
