# Aglaia pass-1 report

Run: `smoke_20261111T1246Z`. Release: `staging/releases/smoke_20261111T1246Z`.
The earlier run and failed package directory are retained for audit.

- 48 raw finite observations; 46 inside the exact supplied WG polygon and with
  all 19 predictor values; 39 unique cells used for both CV and final fit.
- All 10,000 supplied effort-weighted background coordinates retained.
- Four spatial blocks, seed 123, FC L/LQ × RM 1/2. Selected LQ, RM 1 by AICc.
- Mean held-out AUC 0.706056385431573 (SD 0.259138576499423); training AUC
  0.749241025641026. AICc 899.346323768715, nine nonzero coefficients.
- All 39 usable cells retained in saved final model. No holdout-only fit served.
- GeoTIFF cloglog range 0.031396958976984–0.990916967391968; direct Java/map
  presence-cell agreement error zero. Model RDS, evaluation RDS, all tunes,
  metrics, preview, status, input hashes and full package/session snapshot saved.
- Original observation latitude envelope: 8.60533–19.38864, inclusive.
- Actual Java class source is predicts/java/maxent.jar; SHA256
  4c856e55412f70c5597b03cf9aaaf27e0782e0921f937262273b68bdcb8fee5e;
  reported version 3.4.4. BIO filenames are assigned numerically, BIO1 through19.

Runtime environment differs from the laptop: R 4.3.3, ENMeval 2.0.5.2,
predicts 0.2.2, rJava 1.0.11, terra 1.7.65, raster 3.6.26, dismo 1.3.16,
dplyr 1.2.1; native ARM64 Ubuntu 24.04. CBI unavailable without ecospat.
No identical historical AUC or independent ecological validation is claimed.

API real-data checks passed, including raster/API agreement, just-below/above
thresholds, both inclusive latitude endpoints and just-outside exclusion,
outside-WG rejection, an actual NoData cell and invalid inputs. Restart loaded
the same release without training. Evidence: ignored runtime/live-api-evidence.json
and runtime/live-api-restart-evidence.json. Rare out-of-raster and missing-AUC
cases use deterministic fixtures; 15 API regression cases pass.

Browser gate: first Playwright run exercised real manual query, map click and
preview but rejected missing Leaflet marker images. Marker assets now bundled;
final browser run and pass-1 gate identity are recorded below once established.

## Final website acceptance

PASS at 2026-11-11 ~18:20 Asia/Kolkata, before any full-inventory training.
Playwright exercised manual and map queries, preview, outside-WG error, About,
Model, homepage and mobile tool. 46 network requests, zero production API calls,
zero local missing assets, zero JS exceptions. The one 422/console resource error
is the deliberately rejected outside-WG query. Leaflet icons are bundled.
Seventeen API regressions pass, including booleans and literal NaN/Infinity.
Frontend serves an immutable runtime snapshot so rebuilds do not disrupt it.

Acceptance marker: ignored runtime/pass1-gate.json. Detailed evidence/screenshots
copied to runtime/pass1-evidence/ before full training. These contain real queries
and stay out of Git. Full training is now authorized by the completed gate.
