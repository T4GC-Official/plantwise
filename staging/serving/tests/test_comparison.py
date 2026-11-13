import json
from pathlib import Path
import sys
import httpx
import pytest
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.comparison import ComparisonService
from test_api import site


def metadata(self):
    states = {'Test_species': {'status': 'success', 'occurrence_counts': {'unique_cell': 12}, 'selected': {'ncoef': 2}},
              'Sparse_species': {'status': 'excluded', 'occurrence_counts': {'unique_cell': 5}},
              'Zero_species': {'status': 'excluded', 'occurrence_counts': {'unique_cell': 0}}}
    bounds = {s: {'min': 10.5, 'max': 11.5} for s in states}
    return states, bounds, {'Test_species': .8, 'Sparse_species': .6}, {s: True for s in states}


def test_diff_live_and_staging_keep_zero_cutoff_and_exclusions(site, monkeypatch):
    monkeypatch.setattr(ComparisonService, 'metadata', metadata)
    monkeypatch.setattr(ComparisonService, 'fetch_live', staticmethod(lambda lat, lon: {'Test_species': {'score': 54, 'auc': .8}, 'Sparse_species': {'score': 74, 'auc': .6}, 'Zero_species': {'score': 0, 'auc': None}}))
    client, _ = site
    response = client.get('/api/diff', params={'latitude': 11.5, 'longitude': 75.5})
    assert response.status_code == 200
    data = response.json(); rows = {r['species']: r for r in data['rows']}
    assert data['live']['status'] == 'available'
    assert rows['Test_species']['staging']['score'] == 25  # retained even below50
    assert rows['Test_species']['live']['score'] == 54
    assert rows['Sparse_species']['staging']['status'] == 'excluded'
    assert '5 usable' in rows['Sparse_species']['staging']['reason']
    assert rows['Zero_species']['live']['score'] == 0  # zero is a score, not missing
    assert rows['Zero_species']['staging']['score'] is None
    assert 'no-store' in response.headers['cache-control']


def test_diff_live_failure_is_not_empty_recommendations(site, monkeypatch):
    monkeypatch.setattr(ComparisonService, 'metadata', metadata)
    def fail(*args): raise httpx.ConnectError('unreachable')
    monkeypatch.setattr(ComparisonService, 'fetch_live', staticmethod(fail))
    response = site[0].get('/api/diff', params={'latitude': 11.5, 'longitude': 75.5})
    data = response.json()
    assert response.status_code == 200 and data['live']['status'] == 'unavailable'
    assert all(r['live']['status'] == 'source_unavailable' for r in data['rows'])
    assert next(r for r in data['rows'] if r['species'] == 'Test_species')['staging']['score'] == 25


def test_diff_reuses_latitude_nodata_and_wg_safeguards(site, monkeypatch):
    monkeypatch.setattr(ComparisonService, 'metadata', metadata)
    monkeypatch.setattr(ComparisonService, 'fetch_live', staticmethod(lambda *args: {}))
    client, _ = site
    for latitude, longitude, expected in [(11.6, 75.5, 'outside_latitude'), (10.5, 75.5, 'nodata')]:
        data = client.get('/api/diff', params={'latitude': latitude, 'longitude': longitude}).json()
        row = next(r for r in data['rows'] if r['species'] == 'Test_species')
        assert row['staging']['status'] == expected
    assert client.get('/api/diff?latitude=0&longitude=0').status_code == 422
    assert client.get('/api/diff?latitude=NaN&longitude=75').status_code == 422


def test_diff_missing_live_explanation_is_qualified(site, monkeypatch):
    monkeypatch.setattr(ComparisonService, 'metadata', metadata)
    monkeypatch.setattr(ComparisonService, 'fetch_live', staticmethod(lambda *args: {}))
    data = site[0].get('/api/diff?latitude=11.5&longitude=75.5').json()
    row = next(r for r in data['rows'] if r['species'] == 'Test_species')
    assert row['live']['status'] == 'not_returned'
    assert row['live']['reason_confidence'] == 'unknown'
    assert row['live']['score'] is None


def test_clean_routes_do_not_replace_original_home(site):
    client, _ = site
    assert client.get('/').text == 'frontend'
    assert client.get('/diff').text == 'frontend'
    assert client.get('/model').text == 'frontend'
    assert client.get('/api/not-an-endpoint').status_code == 404
