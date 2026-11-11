#!/usr/bin/env python3
"""Real release/API evidence; writes a valid query for the browser gate."""
import json
import math
from pathlib import Path
import sys
import httpx
import numpy as np
import rasterio
from shapely.geometry import Point, shape
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
release=(ROOT/'runtime/active').resolve(strict=True)
cat=json.loads((release/'catalog.json').read_text())
boundary=json.loads((release/'boundary.geojson').read_text())
wg=unary_union([shape(f['geometry']) for f in boundary['features']])
c=httpx.Client(base_url='http://127.0.0.1:8175',timeout=30)
health=c.get('/api/health');health.raise_for_status();assert health.json()['release']==cat['release']
assert c.get('/').status_code==200
assert c.get('/wgg.geojsonl.json').status_code==200
sp='Aglaia_lawii';e=cat['species'][sp]
with rasterio.open(release/e['raster']) as src:
    arr=src.read(1,masked=True)
    candidates=np.argwhere(~np.ma.getmaskarray(arr))
    # Find a real pixel center within species latitude bounds, positive score, exact WG.
    for row,col in candidates[::max(1,len(candidates)//10000)]:
        lon,lat=src.xy(int(row),int(col));value=float(arr[row,col])
        if e['latitude_bounds']['min']<lat<e['latitude_bounds']['max'] and .01<value<.99 and wg.covers(Point(lon,lat)):break
    else:raise ValueError('No usable query pixel')

def query(lat,lon,threshold):
    return c.post('/api/get-results',json={'latitude':lat,'longitude':lon,'minProbability':threshold})
r=query(lat,lon,0);r.raise_for_status();by_species={x['species']:x for x in r.json()};assert abs(by_species[sp]['probability']/100-value)<1e-7
below=query(lat,lon,value*100-1e-5);assert sp in {x['species'] for x in below.json()}
above=query(lat,lon,value*100+1e-5);assert sp not in {x['species'] for x in above.json()}
assert query(0,0,0).status_code==422
assert query(91,75,0).status_code==422
assert query(lat,lon,101).status_code==422
assert query(lat,lon,-1).status_code==422
assert c.get(f'/api/species/{sp}/map').headers['content-type']=='image/png'
# Verify exact inclusive endpoint behavior where valid cells exist along bounds.
latitude_checks=[]
for bound in ('min','max'):
    test_lat=e['latitude_bounds'][bound]
    tested=False
    for test_lon in np.linspace(72.9,78.05,3000):
        if not wg.covers(Point(test_lon,test_lat)):continue
        with rasterio.open(release/e['raster']) as src:
            v=next(src.sample([(test_lon,test_lat)],masked=True))[0]
            if np.ma.is_masked(v) or not math.isfinite(float(v)) or not 0<=float(v)<=1:continue
        exact=query(test_lat,float(test_lon),0);exact.raise_for_status();assert sp in {x['species'] for x in exact.json()}
        outside=test_lat+(-1e-7 if bound=='min' else 1e-7)
        excluded=query(outside,float(test_lon),0)
        if excluded.status_code==200:assert sp not in {x['species'] for x in excluded.json()}
        latitude_checks.append({'bound':bound,'inclusive':True,'outside_excluded':True});tested=True;break
    assert tested, f'Could not exercise {bound} latitude endpoint'
# Search actual NoData cell centers inside the exact WG and latitude envelope.
nodata_checked=False
with rasterio.open(release/e['raster']) as src:
    for row,col in np.argwhere(np.ma.getmaskarray(arr))[::max(1,int(np.ma.getmaskarray(arr).sum())//20000)]:
        x,y=src.xy(int(row),int(col))
        if e['latitude_bounds']['min']<=y<=e['latitude_bounds']['max'] and wg.covers(Point(x,y)):
            response=query(y,x,0);response.raise_for_status();assert sp not in {x['species'] for x in response.json()};nodata_checked=True;break
result={'release':cat['release'],'api_passed':True,'real_query':{'latitude':lat,'longitude':lon,'score':value,'species':sp},'latitude_checks':latitude_checks,'real_nodata_exercised':nodata_checked,'fixture_nodata_and_outside_raster':'pytest staging/tests/test_api.py','health':health.json()}
(ROOT/'runtime/live-api-evidence.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
