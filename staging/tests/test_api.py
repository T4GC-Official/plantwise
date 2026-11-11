"""Regression cases rare in a real single-species raster, including NoData and missing AUC."""
import json
from pathlib import Path
import sys
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from fastapi.testclient import TestClient

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.app import create_app, sample

@pytest.fixture
def site(tmp_path):
    raster=tmp_path/'map.tif'
    values=np.array([[.25,.75],[-9999,1.2]],dtype='float32')
    with rasterio.open(raster,'w',driver='GTiff',height=2,width=2,count=1,dtype='float32',crs='EPSG:4326',transform=from_origin(75,12,1,1),nodata=-9999) as dst:dst.write(values,1)
    (tmp_path/'preview.png').write_bytes(b'preview')
    (tmp_path/'model.rds').write_bytes(b'model')
    boundary={'type':'FeatureCollection','features':[{'type':'Feature','properties':{},'geometry':{'type':'Polygon','coordinates':[[[74,9],[78,9],[78,13],[74,13],[74,9]]]}}]}
    (tmp_path/'boundary.geojson').write_text(json.dumps(boundary))
    catalog={'release':'fixture','evaluation':'block CV','accounting':{'success':1},'species':{'Test_species':{'raster':'map.tif','preview':'preview.png','model':'model.rds','latitude_bounds':{'min':10.5,'max':11.5},'auc':None}}}
    (tmp_path/'catalog.json').write_text(json.dumps(catalog)); (tmp_path/'index.html').write_text('frontend')
    return TestClient(create_app(tmp_path,tmp_path)),raster

def query(c,lat,lon,threshold=0):return c.post('/api/get-results',json={'latitude':lat,'longitude':lon,'minProbability':threshold})

def test_precision_threshold_missing_auc_and_inclusive_latitudes(site):
    c,_=site
    result=query(c,11.5,75.5,25)
    assert result.status_code==200 and result.json()[0]['auc'] is None
    assert result.json()[0]['probability']==25
    assert query(c,11.5,75.5,25.000001).json()==[]
    assert query(c,11.500001,75.5).json()==[]
    assert query(c,10.499999,75.5).json()==[]
    assert query(c,11.5,76.5,74.999999).json()[0]['probability']==75

def test_wg_nodata_raster_extent_and_invalid_scale(site):
    c,raster=site
    assert query(c,0,0).status_code==422
    assert query(c,10.5,75.5).json()==[] # masked NoData
    assert query(c,10.5,76.5).json()==[] # >1 invalid score
    assert query(c,11,77.5).json()==[] # inside WG, outside raster
    assert sample(raster,75.5,10.5) is None
    assert sample(raster,76.5,10.5) is None

@pytest.mark.parametrize('payload',[
    {'latitude':91,'longitude':75,'minProbability':0},
    {'latitude':11,'longitude':181,'minProbability':0},
    {'latitude':11,'longitude':75,'minProbability':-1},
    {'latitude':11,'longitude':75,'minProbability':101},
    {'latitude':'NaN','longitude':75,'minProbability':0},
    {'latitude':'Infinity','longitude':75,'minProbability':0},
    {'latitude':'bad','longitude':75,'minProbability':0},
    {'latitude':True,'longitude':75,'minProbability':0},
    {'latitude':11,'longitude':75,'minProbability':False},
    {'latitude':None,'longitude':75,'minProbability':0},
    {'longitude':75,'minProbability':0},
])
def test_validation(site,payload):assert site[0].post('/api/get-results',json=payload).status_code==422

def test_preview_and_no_api_fallback(site):
    c,_=site
    assert c.get('/api/species/Test_species/map').content==b'preview'
    assert c.get('/api/species/Unknown/map').status_code==404
    assert c.get('/api/species/Test_species/map?release_id=old-release').status_code==409
    assert c.get('/api/unknown').status_code==404
    assert c.get('/api/health').json()['release']=='fixture'

@pytest.mark.parametrize('number',['NaN','Infinity','-Infinity'])
def test_literal_nonfinite_json(site,number):
    response=site[0].post('/api/get-results',content='{"latitude":'+number+',"longitude":75,"minProbability":0}',headers={'Content-Type':'application/json'})
    assert response.status_code==422

@pytest.mark.parametrize('latitude,longitude,threshold',[(11.5,75.5,25),(10.5,75.5,0),(11,77.5,0),(0,0,0)])
def test_get_matches_post(site,latitude,longitude,threshold):
    client,_=site
    params={'latitude':latitude,'longitude':longitude,'minProbability':threshold}
    get=client.get('/api/get-results',params=params)
    post=client.post('/api/get-results',json=params)
    assert get.status_code==post.status_code
    assert get.json()==post.json()

@pytest.mark.parametrize('value',['NaN','Infinity','bad','true','91'])
def test_get_rejects_bad_coordinates(site,value):
    assert site[0].get('/api/get-results',params={'latitude':value,'longitude':75,'minProbability':0}).status_code==422
