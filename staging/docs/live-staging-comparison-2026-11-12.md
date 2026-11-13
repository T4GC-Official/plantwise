# Live/staging investigation — 2026-11-12

Read-only comparison at latitude12.189703804004086, longitude75.94048174979808,
threshold50. Actual browser network requests and direct numeric POSTs agree:
**live9, staging23, five shared, four live-only, eighteen staging-only**.
Current staging release remains full_20261111T1252Z:268 success /180 exclusions.

Three live-only species have no staging model because of data eligibility;
one has a valid staging prediction below50. All eighteen staging-only species
are returned by live at diagnostic threshold0, with reported scores below50.
Thus their absence is not missing live coverage/metadata/NoData. All27 union
species are selected inputs, have historical TIFF/AUC coverage, and pass their
shared latitude envelopes. The query is inside WG and all19 climate values are
valid; all268 active staging rasters have valid cells here.

The extracted deployed container is the correct historical serving reference,
rather than the older Flask backend. It includes the north/south latitude gate,
and current staging includes it too. Neither has a per-species longitude
envelope. Live's264 threshold0 IDs exactly match the historical TIFF+AUC+latitude
candidate set, strong consistency evidence rather than proof of a deployed
source hash. Latitude filtering does not explain this query's9-versus23 list.

Twenty-four saved staging models in the response union were independently
reloaded for inference only and matched GeoTIFF pixels exactly. Training
provenance, including background, feature/regularization selection, BIO20,
preprocessing, prediction scale and full-data fit, is compared in the private
report. Actual original TIFF training provenance is not inferred from the
patched local runner. The supplied jar defaults to CLoglog, so an assumed
old-Logistic/new-Cloglog explanation is not established.

The detailed report also flags a constant, zero-coefficient staging model and
low block-AUC recommendations; more returned species does not prove quality.
No filter, score, model, service, archive or training data was changed.

Private evidence, per-species scores/bounds and screenshots remain Git-ignored:

- ../runtime/comparison-20261112-kodagu/findings.md — full explanation/table
- response-union-comparison.csv — all27 union species and serving gates
- all-species-diagnostics.csv — source inventory including448 selected species
- all-180-exclusions-at-query.csv — exclusions, including absent-on-both cases
- *-browser-http.json / *-browser-response-body.json — actual UI API calls
- *-threshold-{0,50}-http.json / *-threshold-{0,50}.json — raw direct requests
- *-results-desktop.png — inspected rendered lists
- model-inference-verification.json — saved-model/raster agreement
- selective-transfer-manifest.json — exact original TIFF paths for follow-up

For exact original pixel/geometry checks, the manifest prioritizes four
production TIFFs, then lists the remaining20 paired models and three optional
maps for excluded species. Matching production-generated HTML/lambdas/logs are
needed for training provenance; unrelated March reruns are not substitutes.
Shared BIO1–19, observations, WG and jar do not need duplicate transfers.

## Reproduce in a fresh evidence directory

Run from the repository root. These commands query sites/read models only.
Choose a new container name on each invocation; no old artifacts are deleted.

```bash
PLANTWISE_COMPARISON_DIR="$PWD/staging/runtime/comparison-$(date -u +%Y%m%dT%H%M%SZ)"
export PLANTWISE_COMPARISON_DIR
mkdir -p "$PLANTWISE_COMPARISON_DIR"
docker run --name plantwise-query-comparison-UNIQUE --network host --cpus 2 --memory 2g -e PLANTWISE_COMPARISON_DIR=/evidence -v "$PWD/staging:/work:ro" -v "$PLANTWISE_COMPARISON_DIR:/evidence" -v "$PWD/staging/runtime/browser:/browser:ro" -w /work mcr.microsoft.com/playwright:v1.61.0-noble node scripts/compare_sites_browser.cjs
staging/.venv/bin/python staging/serving/comparison/compare_sites_capture.py
staging/.venv/bin/python staging/serving/comparison/compare_sites_analyze.py
docker run --name plantwise-inference-comparison-UNIQUE --network none --cpus 2 --memory 4g -v "$PWD/staging:/work:ro" -v "$PLANTWISE_COMPARISON_DIR:/evidence" -w /work plantwise-training:20261111 Rscript scripts/compare_sites_model_predictions.R
staging/.venv/bin/python staging/serving/comparison/compare_sites_report.py
```

Results reflect the capture time; a future live deployment may differ. The
archived code remains untouched. All substantive per-species interpretation is
in findings.md, with established causes separated from plausible contributors
and unresolved original-map provenance.
