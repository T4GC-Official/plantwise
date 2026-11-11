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
