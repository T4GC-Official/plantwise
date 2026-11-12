# Location comparison at /diff

Open http://100.82.28.38:8175/diff on Tailscale. Simple-language model notes
are at /model. Both are clean routes; original / and /#/tool are unchanged.
Click inside the Western Ghats map or enter full-precision coordinates, then
compare. Both sources are read at cutoff zero; the integer slider changes the
highlighting and recommendation counts without another network request. Use
Only differences, search, or Include unavailable species to inspect the lists.
Details expose exclusion counts, latitude bounds and validation caveats.

## Source contract

GET /api/diff?latitude=12.189703804004086&longitude=75.94048174979808
reads the active staging release and POSTs the identical coordinates with
minProbability=0 to the live species-api-452165326340.asia-south1.run.app
/api/get-results endpoint. Staging uses the existing raster sampler, WG check,
latitude envelopes and finite/NoData validation. No scientific filters changed.
Missing fits are distinguished from below-cutoff scores. Missing live rows get
qualified explanations because the live API exposes no exclusion reason.
Historical latitude/AUC/inventory clues are not asserted as current live causes.

Staging scores retain their raster precision (displayed to two decimals; full
value on hover). Current live scores are whole percentages. Integer cutoffs
preserve the archived API's truncation semantics. Exact coordinates, source
and fetch time are displayed. A failed live request leaves staging usable and
marks live/shared/different counts unavailable, without false staging-only
badges. There is no silent local-TIFF fallback. Responses are not cached.
Two comparisons can run concurrently within the original four-request raster
budget. Live HTTP requests have a 20-second timeout, 5-second connect timeout.

Comparison metadata loads lazily from the active accounting.json, original
448-species occurrence CSV, archived container AUC CSV and source inventory.
These archived metadata files are required for /diff, not the original tool.
Private data and the imported legacy TIFF directory stay outside Git.

## Verified 2026-11-12

At latitude 12.189703804004086, longitude 75.94048174979808, cutoff 50:
staging 23, live 9, shared 5, different 22. At zero: staging 231 and live 264,
265 distinct scored species. Include unavailable species exposes all 448 input
entries (plus any additional live species returned at that location).
The active model release remains full_20261111T1252Z: 268 successful,
180 excluded, no failures. No models were retrained or filters altered.

The newly synced archive/plantwise_v0/tif_data_final contains 395 TIFFs.
Applying the archived container rules at the same point produces 18
recommendations rather than live's 9. This confirms a snapshot/live mismatch,
not its provenance or cause. Therefore the right column uses real-time live
results. The snapshot diagnostic follows archived missing-latitude behavior
and uses only valid 0–1 pixels; it does not change production serving rules.

Validation: 31 pytest cases; final frontend build; real desktop 1440x1100 and
mobile 390x844 browser sessions over the Tailscale IP; actual map clicks;
zero-cutoff counts, shading, search, difference filter, direct /model reload;
simulated live failure; original manual/map/preview/WG browser regression;
actual latitude bounds and NoData API tests. Original homepage screenshots
before/after are pixel-identical at 1440x1687. Screenshots were visually
inspected. Existing AboutPage/ToolPage lint warnings remain; no new lint warning.
The expected outside-WG regression request returns 422. A later browser run
encountered a transient external live timeout during a map click; the source
was explicitly marked unavailable, and the subsequent full run passed. Both
logs are retained. Live API availability is an external dependency.

Private evidence: runtime/diff-page-20261112/ (screenshots, browser-verification,
landing-comparison, snapshot-verification, deployment pointers and logs).

## Reproduce

From repository root:

```bash
staging/.venv/bin/pytest -q staging/tests
staging/.venv/bin/python staging/tests/verify_live.py
PYTHONPATH=staging staging/.venv/bin/python staging/scripts/check_legacy_snapshot.py

docker run --rm --name plantwise-diff-check --network host \
  -e PLANTWISE_DIFF_ORIGIN=http://100.82.28.38:8175 \
  -v "$PWD/staging:/work" -v "$PWD/staging/runtime/browser:/browser" \
  mcr.microsoft.com/playwright:v1.61.0-noble node /work/tests/diff-browser.cjs
```

The browser harness reuses a real response only for its mocked outage test.
Real queries go to /api/diff; the browser itself never requests the external
live API.
The isolated frontend build uses `npm run build` in the same ARM64 container
with staging/frontend mounted at /work. Copy build/ to a new immutable
runtime/frontend-TIMESTAMP directory, atomically update frontend-active and
restart only plantwise-staging.service. Never rebuild the directory being
served. Current frontend: frontend-20261112T131604Z. Previous:
frontend-20261111T154907Z. Deployment pointers are recorded in the private JSON.
Rolling frontend-active back restores the old UI; model rollback is independent
and documented in runbook.md. No cloudflared/other services or Git remotes changed.
