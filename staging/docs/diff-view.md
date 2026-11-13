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
served. Current frontend: frontend-20261113T042955Z. Previous frontend-20261112T144233Z is retained. Previous: frontend-20261112T144117Z;
frontend-20261112T141223Z; frontend-20261112T131604Z and original frontend-20261111T154907Z is also retained. Deployment pointers are recorded in the private JSON.
Rolling frontend-active back restores the old UI; model rollback is independent
and documented in runbook.md. No cloudflared/other services or Git remotes changed.


## Expert review copy revision (2026-11-12)

Simplified /model to the summary, training comparison and a short definition
of usable cells/missing scores. Replaced vague map inventory language with
original source coverage (514 species, including 66 omitted from staging).
Removed the requested provenance/scale cautions, precision commentary, live
missing-score, model-quality and synced-TIFF sections from the product page.
Earlier investigation evidence/provenance remains in operational docs.

/diff now uses the requested map instruction as its title and has three result
columns. Per-species explanations remain in Why / details. That dropdown shows
both staging block-CV AUC and live-reported AUC, without the comparability
sentence. Species without a fitted staging model explicitly show AUC unavailable.
A usable cell is a distinct occurrence cell inside WG with valid values in all
19 layers; missing any layer removes that occurrence from training. Query-time
latitude limits and NoData are separate reasons for a missing score.

Final frontend build passed with only existing AboutPage/ToolPage warnings.
Desktop/mobile Playwright checks over Tailscale passed, including three-column
layout, revised titles, exclusion details, Clausena staging AUC0.624 alongside
live AUC, real map queries, cutoff behavior, /model reload and simulated live
outage. Visually inspected desktop/mobile screenshots. Evidence and deployment
pointers: runtime/diff-copy-edit-20261112/. Preserve earlier diff-page evidence.
To write a fresh browser evidence directory, set PLANTWISE_DIFF_EVIDENCE to an
absolute container path under /work/runtime when running the harness.


## Score explanation revision (2026-11-12)

/model includes Why the scores change, with Old/New background sampling,
model settings and training-data handling. Eligibility was checked directly:
archived InitialImplementation.py check_presence_points uses Presence_Count>2;
separateSpecies.py counts rows (group.shape[0]). New train.R filters coordinates,
WG membership and all19 finite predictor values, deduplicates cellFromXY, and
excludes nrow<8. Four spatial blocks must each have at least two validation
presences. Thus eight is inclusive, and a hundred records in five cells still
fail the count gate. This wrapper comparison does not imply Maxent internally
retained every old input row.

Copied the final build to frontend-20261112T144117Z; previous frontend retained.
Only our service restarted; no backend, filters, model or training changes.
Build succeeded with existing AboutPage/ToolPage warnings. Playwright over the
Tailscale address verified all three Old/New pairs, exact count explanations,
direct route reload and no horizontal overflow at1440 and390 pixel widths.
Desktop/mobile section screenshots were visually inspected. Private evidence:
runtime/score-explanation-20261112/ (verify.cjs, JSON, screenshots, deployment).


Cell-size clarification: verified source BIO1 GeoTIFF EPSG:4326 resolution is
1/120 degree in each direction (30 arc-seconds). /model explicitly contrasts
>2 observation rows against >=8 distinct usable cells, repeats the rule in the
comparison table, and adds “1 cell = 30″ × 30″, approximately0.9 km ×0.9 km in
the Western Ghats.” Ground dimensions are approximate and vary with latitude.
New immutable frontend frontend-20261112T144233Z; rollback retained. Desktop/mobile
browser checks and mobile screenshot inspection passed; evidence under
runtime/cell-size-20261112/. No model, data or filter changes.


## Explicit comparison interaction (2026-11-13)

Map clicks now only select the marker and populate coordinates. No comparison
runs on page load or map selection; submit Compare both models to query. A
changed-location notice separates draft coordinates from displayed results.
Cutoff changes continue to reuse the fetched scores. Renamed the disclosure to
Why?, removed decorative arrows including the native disclosure marker, and
changed text separators to ASCII hyphens. Original home/tool routes unchanged.

Built and published immutable frontend-20261113T042955Z, retaining rollback.
Only our service restarted. Desktop/mobile Playwright verification over
Tailscale passed: zero requests on load, multiple map clicks make no API calls,
Compare sends the exact selected coordinates, the pending notice clears, score
counts/cutoffs/AUC details/model routing/live outage handling still work. Visually
inspected screenshots. Build has only existing AboutPage/ToolPage warnings.
Private evidence: runtime/explicit-compare-20261113/. Updated harness is under
tests/diff-browser.cjs. No training, scientific filters or backend changes.

Source restructuring is discussion only: no source/data directories moved and
no root README changes made in this revision.
