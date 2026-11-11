# Gates for retraining and serving

- [x] Capture ARM64 environment, actual Java jar and dependency snapshot.
- [x] Validate source hashes, numeric BIO mapping, WG mask and background counts.
- [x] Train Aglaia with spatial block CV; finite AICc, held-out AUC, full-data fit.
- [x] Validate real map, score, preview, latitude, WG, NoData and local browser calls.
- [x] Record pass-1 evidence BEFORE starting full training.
- [ ] Account for all 448 species with resumable isolated jobs (full_20261111T1252Z running).
- [ ] Validate full release and atomic promotion; retain smoke rollback.
- [ ] Test restart and rollback on 127.0.0.1:8175.

Future new-data gate: immutable input inventory, coordinate/CRS validation,
background provenance and sensitivity, spatial sampling/partition diagnostics,
minimum-data/AICc eligibility, leakage checks, independent validation where
available, scientific review of score suitability, reproducible environment,
release integrity and API/browser regression evidence before promotion.

## Scientific follow-up before automatic promotion on new data

- [ ] Agree domain-reviewed minimum unique-cell and spatial-fold sample sizes.
- [ ] Decide performance/uncertainty review gates (including low/near-random
  block AUC), sensitivity to effort-background construction and correlated BIOs.
- [ ] Establish independent validation where available; current pooled-effort
  spatial CV does not validate the bias-building process independently.
- [ ] Define data drift and geographic envelope changes needing human review.
- [ ] Version new inputs and package sources; rerun model, map, API, browser,
  restart and rollback gates before changing the active release.
- [ ] Add long-session Leaflet lifecycle/memory testing and migrate obsolete CRA
  separately from model changes.

A finite AICc/AUC and valid GeoTIFF is an operational gate, not an ecological
quality guarantee. The current run reports all eligible fits honestly without
inventing a new retrospective AUC cutoff or silently hiding low-score models.
