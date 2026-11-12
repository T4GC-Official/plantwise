# Gates for retraining and serving

- [x] Capture ARM64 environment, actual Java jar and dependency snapshot.
- [x] Validate source hashes, numeric BIO mapping, WG mask and background counts.
- [x] Train Aglaia with spatial block CV; finite AICc, held-out AUC, full-data fit.
- [x] Validate real map, score, preview, latitude, WG, NoData and local browser calls.
- [x] Record pass-1 evidence BEFORE starting full training.
- [x] Account for all 448 species: 268 successes, 180 exclusions, zero failures.
- [x] Validate full release and atomic promotion; retain smoke rollback.
- [x] Test restart and rollback on 127.0.0.1:8175.

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
- [ ] Replace this task's fixed CSV SHA/14,180-row/448-species guards with an
  explicitly approved, versioned new-data manifest; preserve strict inventory
  checks so additional species never enter a release accidentally.
- [ ] Define when new observations require rebuilding the collector-effort
  background and how that rebuild is validated independently of model CV.
- [ ] Agree retention policy for immutable runs, failed attempts, images and
  stopped containers; nothing is deleted by the current pipeline.

- [ ] Review the nine released models with block-CV AUC below 0.5; private
  review queue: runs/full_20261111T1252Z/low-auc-review.csv. No ecological quality
  guarantee follows from the completed operational gates.

## External preview follow-up

- [ ] Verify the user's exact external preview URL once provided (screenshot
  truncates its address). Loopback and simulated GET-only forwarding now pass.

## Read-only live comparison follow-up

- [ ] If deeper attribution is needed, obtain exact original production TIFFs
  and matching training provenance from the selective-transfer manifest in
  runtime/comparison-20261112-kodagu/. Do not substitute March reruns.
- [ ] Agree quality handling for zero-coefficient/constant fitted maps and
  weak block-CV performance. Existing release/filters were not changed.
