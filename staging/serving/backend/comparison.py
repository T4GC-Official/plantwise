"""Read-only comparison of the active release and observed live API scores."""
import csv
import math
from datetime import datetime, timezone
from pathlib import Path
from threading import BoundedSemaphore

import httpx
from fastapi import HTTPException
from shapely.geometry import Point

LIVE_ENDPOINT = 'https://species-api-452165326340.asia-south1.run.app/api/get-results'


class ComparisonService:
    def __init__(self, root, release, catalog, wg, sampler, live_fetch=None):
        self.root, self.release, self.catalog = Path(root), Path(release), catalog
        self.wg, self.sampler = wg, sampler
        self.live_fetch = live_fetch
        self.capacity = BoundedSemaphore(2)
        self._metadata = None

    def metadata(self):
        if self._metadata is not None:
            return self._metadata
        import json
        states = {s['species']: s for s in json.loads((self.release / 'accounting.json').read_text())}
        bounds = {}
        with (self.root / 'model/data/occurrences/filtered_species_output.csv').open() as f:
            for r in csv.DictReader(f):
                lat, lon = float(r['Latitude']), float(r['Longitude'])
                if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
                    continue
                b = bounds.setdefault(r['Species'], {'min': lat, 'max': lat})
                b['min'], b['max'] = min(b['min'], lat), max(b['max'], lat)
        archive = self.root.parent / 'archive/plantwise_v0'
        with (archive / 'container/auc_and_contributions.csv').open() as f:
            auc = {r['Species']: float(r['Test AUC']) for r in csv.DictReader(f)}
        with (archive / 'source_occurrence_inventory.csv').open() as f:
            inventory = {r['species']: r['has_original_production_tif'] == '1' for r in csv.DictReader(f)}
        self._metadata = states, bounds, auc, inventory
        return self._metadata

    @staticmethod
    def fetch_live(latitude, longitude):
        # Fetch all zero-cutoff scores once. Integer cutoffs can then be adjusted
        # in the browser without requerying or changing either serving policy.
        with httpx.Client(timeout=httpx.Timeout(20, connect=5)) as client:
            r = client.post(LIVE_ENDPOINT, json={'latitude': latitude, 'longitude': longitude, 'minProbability': 0})
            r.raise_for_status()
            data = r.json()
        if not isinstance(data, list):
            raise ValueError('Unexpected live response')
        result = {}
        for r in data:
            sp, score = r['species'], r['probability']
            if not isinstance(sp, str) or isinstance(score, bool) or not isinstance(score, (float, int)) or not math.isfinite(score) or not 0 <= score <= 100:
                raise ValueError('Invalid live score')
            if sp in result:
                raise ValueError('Duplicate live species')
            result[sp] = {'score': score, 'auc': r.get('auc')}
        return result

    def compare(self, latitude, longitude):
        if not self.wg.covers(Point(longitude, latitude)):
            raise HTTPException(422, 'Choose a location inside the Western Ghats boundary.')
        if not self.capacity.acquire(blocking=False):
            raise HTTPException(503, 'A comparison is already running. Please try again shortly.')
        try:
            try:
                states, bounds, auc, inventory = self.metadata()
            except (OSError, ValueError, KeyError):
                raise HTTPException(503, 'Comparison metadata is unavailable. The original tool is still available.')
            live_error = None
            try:
                live = (self.live_fetch or self.fetch_live)(latitude, longitude)
            except (httpx.HTTPError, ValueError, KeyError, TypeError):
                live = {}
                live_error = 'PlantWise India did not return a valid response. Retry to compare both models.'
            fetched_at = datetime.now(timezone.utc).isoformat()
            rows = []
            entries = self.catalog['species']
            for sp in sorted(set(states) | set(live)):
                state = states.get(sp, {})
                entry = entries.get(sp)
                b = bounds.get(sp)
                inside_lat = b is not None and b['min'] <= latitude <= b['max']
                score = None
                if sp not in bounds:
                    status, reason = 'not_in_dataset', 'This species is not in the 448-species staging input.'
                elif state.get('status') != 'success' or entry is None:
                    n = state.get('occurrence_counts', {}).get('unique_cell')
                    status = 'excluded' if state.get('status') == 'excluded' else 'unavailable'
                    reason = (f'No staging model: {n} usable climate cells; this run required at least 8.'
                              if status == 'excluded' and n is not None else 'No successful model in the active staging release.')
                elif not inside_lat:
                    status, reason = 'outside_latitude', 'Outside this species’ observed latitude range in staging.'
                else:
                    value = self.sampler(self.release / entry['raster'], longitude, latitude)
                    if value is None:
                        status, reason = 'nodata', 'The staging map has no valid climate prediction at this location.'
                    else:
                        status, reason, score = 'scored', '', value * 100
                stage = {'status': status, 'score': score, 'reason': reason,
                         'usable_cells': state.get('occurrence_counts', {}).get('unique_cell'),
                         'latitude_bounds': b, 'auc': entry.get('auc') if entry else None,
                         'constant_model': state.get('selected', {}).get('ncoef') == 0}
                if live_error:
                    old = {'status': 'source_unavailable', 'score': None, 'reason': live_error, 'reason_confidence': 'unavailable'}
                elif sp in live:
                    old = {'status': 'scored', 'score': live[sp]['score'], 'auc': live[sp].get('auc'), 'reason': '', 'reason_confidence': 'observed'}
                else:
                    if b is not None and not inside_lat:
                        detail = 'The archived live-serving latitude range excludes this point.'
                    elif sp not in auc:
                        detail = 'The archived live metadata has no AUC entry for this species.'
                    elif inventory.get(sp) is False:
                        detail = 'The species is absent from the historical production map inventory.'
                    else:
                        detail = 'Its current raster coverage, NoData or deployment rules are not exposed by the live API.'
                    old = {'status': 'not_returned', 'score': None,
                           'reason': f'No score returned by live at a zero cutoff. {detail}',
                           'reason_confidence': 'possible' if b is not None and not inside_lat or sp not in auc or inventory.get(sp) is False else 'unknown'}
                rows.append({'species': sp, 'staging': stage, 'live': old})
            return {'query': {'latitude': latitude, 'longitude': longitude}, 'fetched_at': fetched_at,
                    'staging': {'release': self.catalog['release'], 'coverage': self.catalog['accounting']},
                    'live': {'status': 'unavailable' if live_error else 'available', 'error': live_error,
                             'source': 'plantwise-india.org live API', 'score_precision': 'whole_percent' if all(v['score'] == int(v['score']) for v in live.values()) else 'decimal_percent'},
                    'rows': rows}
        finally:
            self.capacity.release()
