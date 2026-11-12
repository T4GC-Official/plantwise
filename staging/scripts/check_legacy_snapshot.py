"""Read synced TIFFs using archived container rules; never import the old app.

Outputs private evidence under runtime/. This is a snapshot diagnostic, not a
replacement for the current live service or proof of its training provenance.
"""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import rasterio
from backend.comparison import ComparisonService

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT.parent / 'archive/plantwise_v0'
LAT, LON = 12.189703804004086, 75.94048174979808


def main():
    bounds = {}
    with (ROOT / 'data/occurrences/filtered_species_output.csv').open() as f:
        for row in csv.DictReader(f):
            lat = float(row['Latitude'])
            b = bounds.setdefault(row['Species'], [lat, lat])
            b[0], b[1] = min(b[0], lat), max(b[1], lat)
    with (ARCHIVE / 'container/auc_and_contributions.csv').open() as f:
        auc = {row['Species'] for row in csv.DictReader(f)}
    scores = {}
    files = sorted((ARCHIVE / 'tif_data_final').glob('*.tif'))
    for path in files:
        sp = path.stem
        if sp not in auc or (sp in bounds and not bounds[sp][0] <= LAT <= bounds[sp][1]):
            continue
        with rasterio.open(path) as src:
            # Match the archived container: inverse affine pixel lookup, no CRS
            # transform or added masks. Window reading avoids loading whole maps.
            px, py = ~src.transform * (LON, LAT)
            if 0 <= px < src.width and 0 <= py < src.height:
                value = float(src.read(1, window=((int(py), int(py)+1), (int(px), int(px)+1)))[0, 0])
                if 0 <= value <= 1:
                    scores[sp] = value * 100
    live = ComparisonService.fetch_live(LAT, LON)
    local50 = sorted(sp for sp, score in scores.items() if score >= 50)
    live50 = sorted(sp for sp, row in live.items() if row['score'] >= 50)
    report = {'captured_at': datetime.now(timezone.utc).isoformat(),
              'query': {'latitude': LAT, 'longitude': LON, 'cutoff': 50},
              'files': len(files), 'snapshot_count': len(local50), 'live_count': len(live50),
              'snapshot_recommendations': local50, 'live_recommendations': live50,
              'snapshot_scores': scores, 'live_scores': live,
              'limits': '448 shared species have archived latitude envelopes; absent envelopes bypass filtering as in the container. Snapshot CRS/NoData behavior follows archived code; only valid 0–1 scores retained.'}
    out = ROOT / 'runtime/diff-page-20261112/snapshot-verification.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps({k: report[k] for k in ('files', 'snapshot_count', 'live_count')}))


if __name__ == '__main__':
    main()
