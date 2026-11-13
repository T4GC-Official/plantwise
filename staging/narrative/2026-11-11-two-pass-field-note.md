# From historical inputs to a working PlantWise release

The starting point was an official checkout plus an uncommitted staging import.
The selected inputs were explicit: 448 species and 14,180 observations, nineteen
WorldClim BIO rasters, the supplied WG polygon and fixed effort-weighted
background. We verified the imported checksums before changing executable code,
kept original inputs read-only and left the official root implementation intact.

The trainer was a scaffold rather than a release pipeline. Lexicographic raster
ordering could label BIO10 as BIO2. It did not persist the selected model,
validate every background cell, require finite eligible AICc or reliably signal
failure. The replacement remains small and task-specific: one species per job,
explicit source identity, staged cleaning counts, four spatial blocks, the
original L/LQ × RM1/2 grid, deterministic selection and an atomic terminal status.
Every final model must contain all usable occurrence cells. Original observations,
not folds or deduplicated records, provide the serving latitude envelope.

Environment work stayed isolated. An ARM64 Ubuntu container supplies R/Java,
a Python venv supplies the API and geospatial IO, and Node 22 builds the original
React frontend. Current CRAN dependencies exposed old Ubuntu Rcpp/dplyr and
missing libuv headers. Package installation also returned success while ENMeval
was absent, so actual package-load assertions became mandatory. Source inspection
showed that this ENMeval version uses predicts, not dismo, to load Java Maxent.
We verify the loaded Java class location, supplied jar checksum and version.
The actual environment differs from the laptop and is documented honestly.

The two-pass structure made the website part of model acceptance. Aglaia's 48
raw observations became 39 usable cells. LQ/RM1 won eligible AICc selection;
mean held-out block AUC was about 0.706. The selected RDS, GeoTIFF, preview and
metrics were produced together. Packaging then caught JSON rounding of latitude
bounds; full-precision serialization and a fresh run resolved it. The first
browser run found missing Leaflet marker images; explicit bundled assets fixed
them. The original map, Bootstrap layout, branding and navigation remained.

The API enforces exact WG membership and inclusive species latitude bounds,
then reads a single raster window, rejecting NoData and invalid scores. It
keeps score precision and includes valid species even when AUC metadata is
missing. Requests stay on the same origin. Preview requests identify their
release so a promotion cannot silently pair old results with a new map. The
frontend is served from an immutable build snapshot, avoiding CRA's transient
missing assets during rebuilds. A dedicated loopback user service reloads these
snapshots without R or training.

Real API and Playwright evidence passed before the full inventory started.
The batch began serially, ramped to two jobs and then capped at three, recording
resource samples. Every species finished with a terminal status: 268 successes,
174 exclusions with fewer than eight usable cells, six zero-usable-point
exclusions and no failures. No old maps, extra species or uniform-background
fallback filled the gaps. All original data checksums still match.

Independent RDS verification exposed a subtle measurement issue: original
coordinates exactly on grid edges can select different cells after tiny floating
point changes to the crop/write transform. Comparing identical GeoTIFF pixel
centers resolved that ambiguity; all 268 reloaded models match with error zero.
The failed verification log is retained, and a canonical grid/cell-ID policy is
proposed for future processing. No model or raster was changed to satisfy it.

The final full release passed real API checks, seventeen regression cases and
Playwright manual/map/preview/navigation/mobile checks. It has no production API
calls or missing local assets. Restart passed, an actual rollback loaded the
retained one-species release, and re-promotion restored all 268 models without
training. The full release is left running on 127.0.0.1:8175. Existing services
and cloudflared were untouched; public domain configuration remains with the user.

These are completed operational gates, not an ecological quality guarantee.
Nine fitted models have held-out block AUC below 0.5 and are explicitly flagged.
Domain-reviewed sample/performance criteria, effort-background sensitivity,
independent validation and new-data drift gates remain in todos/. Processing
improvements, including a stricter source package lock and canonical raster
grid, are in proposals/. Superseded scaffold code is preserved in archive/.

The user's subsequent mobile screenshot exposed a gap in the first acceptance:
we had preserved the overall design but added release/protocol paragraphs and
an AUC column. Comparing rendered screenshots with the deployed original made
the resulting mobile displacement clear. Those additions are now removed;
metadata belongs in the API/docs, while the tool keeps the original layout.
A screenshot inspection and matching control bounds now complement functional
checks. The desktop controls and footer match production pixel-for-pixel.

The reported JSON exception is reproduced when a preview forwarder rejects POST
with an empty response. Read-only GET recommendations preserve the same backend
safeguards and work under that constraint; POST remains available. The client
also handles empty responses and distinguishes failed requests from empty
recommendations. The exact screenshot coordinates return20 results in both
viewport tests. The external URL itself remains unverified until the truncated
address is supplied in full; neither the domain nor tunnel was changed.

A subsequent read-only comparison with the live site separated coverage from
scores at the user's exact point. Both frontends at50 returned9 and23 species,
with five shared. Three live recommendations were excluded from the new model
inventory, one fell below the new cutoff, and eighteen crossed above it. Live's
threshold0 response exposed the latter scores, so missing metadata or maps could
be ruled out for those differences. Both serving implementations include the
latitude envelope. The current live zero-threshold set exactly matches the
archived TIFF/AUC/latitude candidate set, although that is not proof of an
identical current deployment or historical model-training provenance.

Saved-model inference matches the new rasters. One selected model is constant,
and several returned models have weak block-CV scores, reinforcing why a larger
recommendation list is not a quality verdict. Full evidence and a selective
original-map transfer list remain private; the investigation did not change
services, models or filters. See docs/live-staging-comparison-2026-11-12.md.


The next serving change made the investigation accessible through /diff. One
map click now requests the same point from the active staging rasters and the
real live API, retaining scores at zero so a cutoff no longer hides the reason
for a list difference. Exclusions have explicit cell counts, unavailable pixels
remain distinct from zero, and uncertain live omissions are labelled as such.
A separate /model page explains training/background/coverage differences without
claiming the archived trainer proves historical map provenance. The newly synced
395-map snapshot returns18 rather than9 at the verification point, reinforcing
why live scores are fetched directly. Responsive browser checks and screenshot
inspection passed; original landing pixels and tool behavior were preserved.
See docs/diff-view.md for source contracts, evidence and operations.


For expert review, simplified the model comparison copy and moved all row
explanations into the existing dropdown, leaving three aligned result columns.
Both validation AUCs are visible there; excluded fits explicitly lack a staging
AUC. Clarified distinct occurrence cells and missing BIO values, and retained
operational provenance in repository docs while shortening the product pages.
Updated desktop/mobile checks and visually reviewed screenshots before closing
this revision. The model inventory, scores and filters remain unchanged.


The model notes now explain score changes through Old/New background sampling,
model settings and observation handling. Verified that the archived eligibility
gate counted more than two rows, while staging requires at least eight distinct
complete climate cells for four-block evaluation. Added a concrete example to
separate occurrence counts from cell counts. Published and visually checked the
updated explanation on desktop/mobile without changing any training behavior.

The eligibility distinction is now explicit in both explanatory text and the
comparison table, with verified30-arc-second cell dimensions and approximate
0.9km ground dimensions alongside it.


Refined /diff so selecting a point is independent from executing a comparison.
Users can explore the map before submitting; previous results are explicitly
labelled when the draft location changes. Simplified labels and punctuation,
and verified both layouts and actual request behavior through Playwright.
Reviewed the source layout for a discussion of clearer model/serving boundaries,
without moving directories or changing root documentation yet.
