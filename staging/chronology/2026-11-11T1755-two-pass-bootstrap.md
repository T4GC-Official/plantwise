# Two-pass bootstrap (Asia/Kolkata)

Read AGENT_PROMPT, README and SOURCE_MAP; confirmed branch staging/enmeval-nov-2026.
Initial imported-file SHA256 verification passed in full. No tracked root files changed.
Port 8175 free. Host aarch64; Docker available; Rscript absent. Chose dedicated
Ubuntu 24.04 ARM64 container, two build CPUs, single-thread numerical libraries.

The scaffold sorts BIO files lexicographically, does not persist models, has an
unfiltered background, unchecked AICc selection and success exit on failures.
These are implementation work before the Aglaia gate. No full training started.

Documentation follows ../io: timestamped chronology, dated thematic narrative,
operational docs, remaining todos and proposals. Raw evidence remains ignored.

## Dependency diagnostics and first code checkpoint

Local commit e50872f contains scaffold hardening, release backend, original UI
and operational notes. Initial 12 API regression cases pass; frontend production
build passes (existing CRA/lint warnings retained for separate cleanup).

ENMeval 2.0.5.2 actually uses predicts::MaxEnt; source inspection corrected jar
installation and S4 prediction dispatch. Current predicts ships a jar, so verify
and replace it with the supplied jar inside the isolated image before loading.

R package installation returned zero despite unavailable ENMeval. Added explicit
load assertions. Diagnosed current units requiring Rcpp >=1.1.0, dbplyr needing
dplyr filter_out export, and fs needing libuv headers. Upgrading these only
inside the container; ENMeval remains pinned. No scientific-policy fallback.

No connected browser was available (browser discovery returned empty); user
explicitly authorized Playwright. Dedicated ARM64 headless Chromium container
prepared. Real browser/API pass remains pending Aglaia training.

## First Aglaia model and packaging precision gate

Run smoke_20261111T1240Z trained successfully in about 33 seconds: 48 raw,
46 in-WG/complete cases, 39 unique cells; 10,000/10,000 background retained.
Selected LQ/RM1, held-out AUC ~0.706, AICc ~899.35, nine coefficients, final n=39.
Map values checked against direct Java cloglog predictions. CBI unavailable
because ecospat is not installed; not fabricated or used for selection.

Release packaging rejected exact latitude-bound equality because jsonlite's
default serialization rounded coordinates. Fixed digits=NA and started fresh
smoke_20261111T1246Z. Failed package directory and first run retained. Stopped
our own new service pending valid publication; no pre-existing service changed.
Release builder now stages into a .building directory and renames only after
validation/checksums complete. Found four input IDs with legitimate hyphens or
subspecies periods; preserve them exactly instead of lossy canonicalization.

## Pass-1 website accepted

smoke_20261111T1246Z published on loopback8175. Real API/raster checks pass,
including exact inclusive latitude endpoints, actual NoData and threshold
precision. Restart reloaded the same release without training. First browser
run caught missing Leaflet marker assets; bundled imports fixed them. Final
Playwright run passes manual/map queries, preview, navigation and mobile view,
with no missing local assets, JS exceptions or production API requests.
Seventeen API fixtures pass. Runtime pass1-gate.json and pass1-evidence snapshot
saved before starting the full inventory. Smoke remains served during full work.

## Full inventory started after acceptance

Run full_20261111T1252Z started at 12:49:33 UTC with immutable config and exact
448-name inventory. Serial warmup, two-job ramp, ceiling3. Early training jobs
use ~2.3–2.4 GiB each, ~one CPU each; >40 GiB host memory available. Sparse
species receive explicit exclusions; all terminal states are resumable. The
one-species release remains active on the website throughout training.
