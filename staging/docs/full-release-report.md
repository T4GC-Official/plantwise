# Full release: 2026-11-11

Active release: **full_20261111T1252Z**, served at **http://127.0.0.1:8175**.
The user can configure plantwise.idli.cc against this loopback origin. No tunnel
or public domain configuration was changed or claimed live.

## Inventory and processing

Exactly 448 input species / 14,180 observations; source checksum unchanged.
All species have one terminal job status:

| Outcome | Species |
|---|---:|
| Successful full-data models | 268 |
| Excluded: 1–7 usable unique cells | 174 |
| Excluded: zero usable cells | 6 |
| Failures | 0 |
| Total | 448 |

All observations were finite and geographically valid. WG membership retained
13,790 rows; complete BIO1–19 values retained 13,789; per-species cell deduplication
retained 9,595 cells across all species. The 268 fitted models use 9,007 cells;
all saved models assert n_final = n_usable. Excluded species are unavailable;
no original maps or extra species fill gaps. Supplied effort-weighted background
retained all 10,000 coordinates. No BIO20, extra 66 species or ensemble was used.

Full training ran after the saved real pass-1 website gate (12:49:33 UTC).
First full-job status started 12:49:37 UTC; final job finished 13:54:18 UTC.
Serial/two-job warmup preceded the ceiling of three jobs. Successful jobs took
~32 seconds; sampled containers used ~2–2.4 GiB each, with ample host headroom.
Runs, outputs, data, release geometry, logs and screenshots remain out of Git.

## Model evaluation and limitations

ENMeval 2.0.5.2 / Java Maxent 3.4.4, four spatial blocks, FC L/LQ × RM 1/2,
seed 123, supplied effort-weighted background, WG masking and BIO1–19.
Finite AICc, finite held-out AUC and ncoef < n-1 determine eligible settings;
deterministic ties use AICc, coefficient count, FC and RM. Minimum eight unique
cells and two validation presences per block is an operational starting gate.
Actual environment versions and jar identity are in training-environment.md.

| Selected settings | Species |
|---|---:|
| L / RM1 | 57 |
| L / RM2 | 67 |
| LQ / RM1 | 77 |
| LQ / RM2 | 67 |

Mean held-out block AUC: 0.7492; median 0.7589; interquartile range
0.6797–0.8330; range 0.3094–0.9927. **Nine models have block AUC below 0.5** and
are flagged in the private run's low-auc-review.csv. These scores remain available in API/report metadata;
no retrospective quality cutoff was silently introduced. Scientific review,
background sensitivity and independent validation remain future model gates.
CBI is unavailable because ecospat is not installed. No exact reproduction of
historical AUC or ecological certification is claimed. Scores are cloglog
suitability, not planting-success probabilities.

## Release validation

- Every success has metrics, all tuning rows, selected model RDS, evaluation RDS,
  GeoTIFF, decoded PNG preview, provenance, package/session snapshot and logs.
- Normalized release validates finite raster range 0–1, CRS, NoData, original
  coordinate-valid latitude envelopes, all requested statuses and SHA256 hashes.
- All 268 RDS models independently reloaded in a fresh, network-isolated JVM;
  direct cloglog predictions match their GeoTIFF pixel centers with max error 0.
- A first validator used original coordinates at grid edges. Tiny raw/cropped
  x-resolution differences selected adjacent pixels there. Pixel-center sampling
  fixes the comparison; trained models and maps were not changed. Details and
  future canonical-grid proposal are recorded in chronology/ and proposals/.
- Aglaia's full-run TIFF is byte-identical to the retained smoke TIFF.
- Full-release real API tests pass for score agreement, thresholds, inclusive
  latitude endpoints, WG filtering, real NoData, preview and invalid inputs.
- Seventeen API regression fixtures pass, including missing AUC, out-of-raster,
  nonfinite numbers, booleans, and release-specific preview rejection.
- Playwright passes home, manual query, actual Leaflet map click, matching preview,
  outside-WG error, About/Model routes and mobile view. Zero production API calls,
  missing local assets or JS exceptions. One expected 422 is the deliberate WG
  rejection; OSM basemap requests are expected.
- Full restart passed. Actual rollback to smoke (one species) passed API tests,
  then re-promotion to full (268 species) passed again without training. A stale
  smoke-release preview request is rejected with 409 under the full release.

## Paths and service

- Run: staging/model/runs/full_20261111T1252Z/
- Release: staging/model/releases/full_20261111T1252Z/
- Rollback: staging/model/releases/smoke_20261111T1246Z/
- Active model link: staging/runtime/active
- Frontend snapshot: staging/runtime/frontend-20261111T1250Z/
- Service: systemctl --user status plantwise-staging.service
- Final API evidence: staging/runtime/final-full-api.json
- Full browser/model evidence: staging/runtime/full-evidence/
- Full accounting/metrics: run/accounting.json, final-audit.json,
  all-success-metrics.csv, low-auc-review.csv

The enabled user service has restart behavior and user lingering was already
enabled. It loads immutable frontend/model snapshots at startup and never trains.
Detailed restart, rollback, rebuild and verification commands are in runbook.md.

## Subsequent frontend correction

See visual-parity-and-preview.md: extra diagnostic UI and the AUC column were
removed to match the original website. The frontend uses validated GET queries
for read-only preview compatibility, retaining POST. Twenty-six API cases and
desktop/mobile visual/interaction checks now pass. Model artifacts are unchanged.
