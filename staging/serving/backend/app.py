"""One immutable release per process; same-origin frontend and bounded raster reads."""
import json
import math
import os
from pathlib import Path
from threading import BoundedSemaphore

import rasterio
from rasterio.warp import transform
from fastapi import FastAPI, HTTPException, Query as QueryParam
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from shapely.geometry import Point, shape
from shapely.ops import unary_union
from .comparison import ComparisonService

ROOT = Path(__file__).resolve().parents[2]


class Query(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra='forbid')
    latitude: float = Field(strict=True, ge=-90, le=90)
    longitude: float = Field(strict=True, ge=-180, le=180)
    minProbability: float = Field(strict=True, ge=0, le=100)


def sample(path, longitude, latitude):
    with rasterio.open(path) as src:
        x, y = transform('EPSG:4326', src.crs, [longitude], [latitude])
        row, col = src.index(x[0], y[0])
        if not (0 <= row < src.height and 0 <= col < src.width):
            return None
        value = src.read(1, window=((row, row + 1), (col, col + 1)), masked=True)[0, 0]
        if getattr(value, 'mask', False):
            return None
        value = float(value)
        return value if math.isfinite(value) and 0 <= value <= 1 else None


def create_app(release_path=None, static_path=None):
    release = Path(release_path or os.environ.get('PLANTWISE_RELEASE', ROOT / 'runtime/active')).resolve(strict=True)
    catalog = json.loads((release / 'catalog.json').read_text())
    entries = catalog['species']
    features = json.loads((release / 'boundary.geojson').read_text())
    wg = unary_union([shape(f['geometry']) for f in features['features']])
    for species, entry in entries.items():
        if not entry.get('latitude_bounds') or not all(math.isfinite(v) for v in entry['latitude_bounds'].values()):
            raise ValueError(f'Unavailable latitude bounds: {species}')
        if entry['latitude_bounds']['min'] > entry['latitude_bounds']['max']:
            raise ValueError(f'Invalid latitude bounds: {species}')
        for key in ('raster', 'preview', 'model'):
            p = (release / entry[key]).resolve(strict=True)
            if not p.is_relative_to(release):
                raise ValueError('Release paths must stay within the release')
    app = FastAPI(title='PlantWise ENMeval')
    capacity = BoundedSemaphore(4)
    comparison = ComparisonService(ROOT, release, catalog, wg, sample)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, exc):
        # Do not echo NaN/Infinity input into a JSONResponse (invalid JSON).
        return JSONResponse(status_code=422, content={'detail': [
            {'loc': e['loc'], 'msg': e['msg'], 'type': e['type']} for e in exc.errors()
        ]})

    @app.get('/api/health')
    def health():
        return {'status': 'ok', 'release': catalog['release'], 'species_count': len(entries),
                'coverage': catalog['accounting'], 'evaluation': catalog['evaluation'], 'score': 'cloglog suitability'}

    def recommend(query: Query):
        if not wg.covers(Point(query.longitude, query.latitude)):
            raise HTTPException(422, 'Coordinates are outside the Western Ghats boundary')
        if not capacity.acquire(blocking=False):
            raise HTTPException(503, 'Service busy; retry shortly')
        try:
            result = []
            for species, entry in entries.items():
                bounds = entry['latitude_bounds']
                if not bounds['min'] <= query.latitude <= bounds['max']:
                    continue
                value = sample(release / entry['raster'], query.longitude, query.latitude)
                if value is not None and value >= query.minProbability / 100:
                    result.append({'species': species, 'probability': value * 100,
                                   'auc': entry.get('auc'), 'evaluation': catalog['evaluation'],
                                   'release': catalog['release']})
            return sorted(result, key=lambda x: (-x['probability'], x['species']))
        finally:
            capacity.release()

    @app.post('/api/get-results')
    def results(query: Query):
        return recommend(query)

    @app.get('/api/get-results')
    def get_results(
        latitude: float = QueryParam(..., ge=-90, le=90, allow_inf_nan=False),
        longitude: float = QueryParam(..., ge=-180, le=180, allow_inf_nan=False),
        minProbability: float = QueryParam(..., ge=0, le=100, allow_inf_nan=False),
    ):
        # Read-only queries also work through preview forwarders that accept GET.
        values = Query(latitude=latitude, longitude=longitude, minProbability=minProbability)
        return JSONResponse(recommend(values), headers={'Cache-Control': 'no-store'})

    @app.get('/api/species/{species}/map')
    def preview(species: str, release_id: str | None = None):
        if release_id is not None and release_id != catalog['release']:
            raise HTTPException(409, 'Release changed; refresh the page before opening this map')
        if species not in entries:
            raise HTTPException(404, 'Species is unavailable in this release')
        return FileResponse(release / entries[species]['preview'], media_type='image/png')

    @app.get('/api/diff')
    def diff_results(
        latitude: float = QueryParam(..., ge=-90, le=90, allow_inf_nan=False),
        longitude: float = QueryParam(..., ge=-180, le=180, allow_inf_nan=False),
    ):
        if not capacity.acquire(blocking=False):
            raise HTTPException(503, 'Service busy; retry shortly')
        try:
            return JSONResponse(comparison.compare(latitude, longitude), headers={'Cache-Control': 'no-store'})
        finally:
            capacity.release()

    @app.get('/source/old/InitialImplementation.py', include_in_schema=False)
    def old_model_source():
        return FileResponse(ROOT / 'archive/legacy/InitialImplementation.py', media_type='text/plain',
                            headers={'X-Content-Type-Options': 'nosniff', 'Cache-Control': 'no-cache'})

    @app.get('/source/new/train.R', include_in_schema=False)
    def new_model_source():
        return FileResponse(ROOT / 'model/enmeval/train.R', media_type='text/plain',
                            headers={'X-Content-Type-Options': 'nosniff', 'Cache-Control': 'no-cache'})

    @app.get('/api/{path:path}')
    def api_missing(path: str):
        raise HTTPException(404, 'API endpoint not found')

    static = Path(static_path or os.environ.get('PLANTWISE_STATIC', ROOT / 'runtime/frontend-active')).resolve(strict=True)
    @app.get('/diff', include_in_schema=False)
    @app.get('/diff/', include_in_schema=False)
    @app.get('/model', include_in_schema=False)
    @app.get('/model/', include_in_schema=False)
    def comparison_page():
        return FileResponse(static / 'index.html', headers={'Cache-Control': 'no-cache'})

    app.mount('/', StaticFiles(directory=static, html=True), name='frontend')
    return app
