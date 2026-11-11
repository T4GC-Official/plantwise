# ENMeval-only PlantWise staging handoff

> Implemented 2026-11-11: 268 models served on 127.0.0.1:8175; all 448 species
> accounted for. Current results and operations: [docs/README.md](docs/README.md).
> Initial-state statements below describe the original handoff.

This plan supersedes the three-model site proposal for the current prototype.
The two-pass flow below also supersedes the earlier synthetic-website-first
instructions: train ONE species, verify its complete website, THEN train all.
No training, installation or serving was performed by the preparing agent.
The next agent implements and runs the stages below. Starting prompt:
`AGENT_PROMPT.md`. File provenance: `SOURCE_MAP.md`.

## Scope and initial state

- One model: ENMeval tuning Java Maxent 3.4.4, effort-weighted background,
  BIO1..19 and WG boundary, using the developer's 448-species v1 occurrences.
- The latest supplied `nov_ensembel_plants.R` is biomod2 ensemble code, not
  ENMeval. Preserve it as reference; do not execute or port ensemble machinery
  in this task. Its hardcoded CHELSA/LULC/hornbill setup is not required.
- Adopt useful principles, not all November defaults: validated/deduplicated
  points, explicit seeds/resources, progress, retained evaluation outputs,
  auditable predictor selection and thresholds. Do not introduce elevation,
  VIF pruning, 300 km buffers, LULC masks or new thinning rules silently.
- Bias surface = collector effort used to sample background, not an extra
  BIO predictor or habitat boundary. WG polygon = geographic boundary,
  not a substitute for missing climate data. All required inputs are supplied.
- `Master_Metrics_10_Species.csv` is output, not training data. Its species
  column defines the ten smoke-test targets. Treat historical scores as
  context: unspecified seeds/background/version differences preclude exact
  numerical reproduction as an acceptance condition.
- Preserve the official checkout's original files. Work in its new staging/
  directory and document any root-level integration in a later commit.

## Selected inputs and differences from the originally shared baseline

Use ONLY these declared inputs; do not expand them to make inventories match:

| Input | Selected source and use | Difference from original bprashanth/plantwise baseline |
|---|---|---|
| Occurrences | v1 filtered_species_output.csv: 14,180 rows, 448 species | Original Final_Species.csv has 15,335 rows, 514 species. The additional 66 species are deliberately excluded. For the 448 retained species, every observation row matches numerically, including duplicate multiplicities. |
| Bioclim predictors | 19 wc2.1_30s_bio_{1..19}_fc.tif files in data/attributes | All 19 files are SHA256 byte-identical to the independent original PlantWise/final_attributes copy. Original baseline also has BIO20, deliberately excluded because its provenance is unidentified. |
| WG polygon | v1 wg_boundary shapefile and sidecars in data/boundary | Core .shp/.shx/.dbf/.prj files are byte-identical to original PlantWise/frontend/habitability-tool/src/wg_boundary.*. This directory contains a polygon, not climate layers. |
| Bias/background | September v1-derived biasBg.csv: 10,000 effort-weighted background coordinates; biasMap.tif retained for audit | No generated bias files exist in v1 itself; these are the generated copies preserved in v2. This is an explicit background-policy change, not a replacement environmental predictor. |
| Training | Adapted v1 ENMeval Java-Maxent runner with configurable paths; block CV, FC L/LQ, RM 1/2 initially | Unlike the original direct Java per-species runner, this tunes settings and evaluates spatial partitions. It is not a reproduction of a single legacy random-holdout AUC draw. |
| Smoke reference | Master_Metrics_10_Species.csv | Historical output, NOT occurrence input or an exact-score acceptance target. All ten species exist in v1, original source CSV, baseline AUC report and production TIFF inventory. Only Aglaia_lawii is required for pass 1. |

The v1 occurrence set also exactly matches the production container's 448
per-species CSVs: all 14,180 observation rows, including multiplicities.
Do not confuse this input inventory with output coverage: the original AUC
report has 392 species, of which 340 overlap v1 (108 v1-only, 52 report-only).
The original production TIFF inventory has 368 species, all within v1; 80 v1
species have no original production TIFF. These differences do NOT authorize
adding the missing original-source species or dropping v1-only species.

Byte-identical source rasters do not mean identical final modelling extent:
the ENMeval runner explicitly crops/masks to the WG polygon. Record that mask
along with the changed predictor/background/partition policies in run metadata.
Preserve the production latitude-bound serving safeguard using the selected
original observations, not CV folds. No ensemble, BIO20, extra 66 species,
elevation, CHELSA or LULC is part of this run.

Remote inspected on 2026-11-11: Ubuntu 24.04, ARM64, 20 cores, 121 GiB total
RAM (about 46 GiB available), 208 GB free disk, Docker and Java available,
Rscript absent from PATH. Port 8175 was free at inspection, recheck before
binding. Host shared with other applications, including Pyrocene. No GitHub
SSH authentication was verified; public HTTPS clone works, pushing is not
part of this task. No changes to existing cloudflared or other services.

## Layout and verification

```text
plantwise/                         official repository clone
  staging/
    README.md AGENT_PROMPT.md SOURCE_MAP.md .gitignore
    models/enmeval/                runnable scaffold and bias builder
    models/maxent/maxent.jar
    data/attributes/               19 predictor TIFFs only
    data/occurrences/filtered_species_output.csv
    data/boundary/                 WG shapefile + sidecars
    data/reference/Master_Metrics_10_Species.csv
    data/derived/bias_layer/        biasBg.csv, randomBg.csv, biasMap.tif, metrics
    frontend/                      original React application
    reference/                     production API, v1 sources, November script
    docs/history/                  selected prior findings
    runs/                          NEW unique, resumable run directories
    releases/                      NEW immutable final model map releases
  SYNC_SHA256SUMS                   initial imported-file checksum list
```

Start in the checkout, check `git status`, then:

```bash
cd /home/beeps/src/github.com/bprashanth/plantwise
sha256sum -c SYNC_SHA256SUMS
cd staging
export PLANTWISE_RUNS="$PWD/runs"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export JAVA_TOOL_OPTIONS=-Djava.awt.headless=true
mkdir -p docs runs releases
```

Keep heavy/private data gitignored. Verify with `git check-ignore` and review
`git diff --cached --stat` before each commit. No deletion of any user data or
old result, no rsync --delete. Do not reuse output paths from earlier jobs.

## Required order: two passes

PASS 1: install the isolated environment, harden the runner, train Aglaia_lawii,
and build/verify the complete website using its real GeoTIFF and preview.
Do not begin full training until this one-species site passes the checks below.

PASS 2: train all eligible species from the exact 448-species CSV resumably,
then switch the SAME website to the validated full release. Retain pass 1
outputs for rollback. Fake files and an old v0 TIFF are not prerequisites;
optional synthetic unit tests must never substitute for the real pass 1 gate.

## Stage 1: install an isolated training environment

Preferred: a native ARM64 training container, mounting staging/ with outputs
persisted outside the image; install the following inside that container as
root. Alternative: host R with a dedicated user library, only if authorized
to install host packages. These commands are instructions, not already run.

Ubuntu/Debian system prerequisites (sudo only for an authorized host install):

```bash
sudo apt-get update
sudo apt-get install -y r-base r-base-dev default-jdk build-essential gfortran \
  libgdal-dev gdal-bin libgeos-dev libproj-dev libudunits2-dev \
  libcurl4-openssl-dev libssl-dev libxml2-dev libfontconfig1-dev \
  libfreetype6-dev libpng-dev libjpeg-dev libtiff-dev libharfbuzz-dev \
  libfribidi-dev libglpk-dev cmake pkg-config python3-venv
export JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")"
sudo R CMD javareconf
mkdir -p "$PWD/.Rlib"
export R_LIBS_USER="$PWD/.Rlib"
Rscript -e 'install.packages(c("remotes","rJava","terra","raster","dismo","dplyr"), repos="https://cloud.r-project.org", Ncpus=2)'
Rscript -e 'remotes::install_version("ENMeval", version="2.0.5.2", repos="https://cloud.r-project.org", upgrade="never")'
Rscript -e 'for (p in c("rJava","terra","raster","dismo","dplyr","ENMeval")) {library(p, character.only=TRUE); cat(p, as.character(packageVersion(p)), "\n")}; rJava::.jinit(); print(sessionInfo())'
```

On a container omit sudo and set the working directory/mount before installing.
Do not modify global R libraries shared with other applications. If compiler,
dependency or version installation fails, diagnose it and record the actual
version change; do not claim the reference environment has been reproduced.

Laptop reference versions (verified, not a full dependency lock): R 4.1.2,
ENMeval 2.0.5.2, rJava 1.0.18, terra 1.9.27, raster 3.6.32, dismo 1.3.16,
dplyr 1.2.1. CRAN currently offers ENMeval 2.0.6; use the reference version
first rather than silently changing the API. Once working, capture sessionInfo
and a dependency lock/snapshot. Never copy x86 R libraries to this ARM64 host.

References: https://cran.r-project.org/package=ENMeval and
https://cran.r-project.org/package=rJava . The API docs/vignette are linked
from the ENMeval package page. Compilation and Java setup are prerequisites,
not something a Python venv or uv can install for R.

For the future API, create an isolated Python venv (uv if available, otherwise
python3 -m venv), install FastAPI, uvicorn, rasterio, pandas and shapely, and
pin the tested versions. Install a current supported Node LTS in the frontend
build environment, use `npm ci`, and retain the lockfile. Serving can use a
lean separate container without the R training packages.

## Stage 2: minimal runner hardening before training

The imported scripts are unmodified references, NOT certified final trainers.
Make small reviewable fixes before declaring a full training run ready:

1. Numeric BIO filename ordering: both ENMeval and bias-builder currently sort
   lexicographically then rename BIO1..19. Fix the mapping consistently;
   record filenames and assigned predictor names. Historical biasBg.csv BIO
   columns are mislabeled; the ENMeval reader takes only its coordinates.
2. Verify the jar ENMeval actually loads, not only the configured file. Check
   dismo/predicts Java lookup for the installed version, compare SHA256 and
   print actual jar path/version. Use an isolated library before copying jars.
3. Confirm ENMeval prediction dispatch/scale on the chosen S4 model. Preserve
   explicit Maxent cloglog output semantics; do not normalize by guessing.
4. Filter supplied background coordinates to cells valid in every predictor
   after WG masking. Record initial/remaining counts; never silently fall back
   to random background. Validate all coordinates and occurrences as well.
5. Log raw, finite, in-boundary, complete-case and unique-cell occurrence counts
   per species. Skip statistically insufficient species with recorded reasons;
   block CV can fail even if raw n > 2. Do not claim all 448 species are usable.
6. Write per-species status and outputs atomically/resumably; distinguish no
   AICc-eligible tuning model, partition failure, zero usable points and model
   failure. The scaffold catches failures and may exit zero with an empty CSV.
7. Ensure a valid finite AICc selection (including ncoef/sample-size limits),
   deterministic ties and reproducibility. Save all tuning rows and selected
   FC/RM, software/input provenance, logs, model object and actual map paths.

Keep the shared bias coordinates fixed for the initial smoke test. If rebuilding
the bias layer, write to a NEW derived directory and record that change. Full
cross-validation of the bias-building process is a later framework question;
the existing all-species effort surface is not an independent external test.

## Stage 3: PASS 1 - train one species and verify its website

Run from staging/. Use a NEW run ID for each attempt, and capture stderr too.
This command is for the imported runner AFTER addressing the above issues:

```bash
RUN_ID="smoke_aglaia_$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$PLANTWISE_RUNS/$RUN_ID"
mkdir -p "$OUT"
set -o pipefail
Rscript "models/enmeval/sdm code for 10 species.R" \
  --species_csv="$PWD/data/occurrences/filtered_species_output.csv" \
  --tif_folder="$PWD/data/attributes" \
  --boundary_shp="$PWD/data/boundary/wg_boundary.shp" \
  --maxent_jar="$PWD/models/maxent/maxent.jar" \
  --bg_csv="$PWD/data/derived/bias_layer/biasBg.csv" \
  --species=Aglaia_lawii --partitions=block --fc=L,LQ --rm=1,2 \
  --seed=123 --write_maps=1 --metrics_name=metrics.csv \
  --output_dir="$OUT" 2>&1 | tee "$OUT/training.log"
```

Aglaia_lawii has 48 raw points. The ten reference targets and raw point counts:

| Species | Raw observations |
|---|---:|
| Goniothalamus_wightii | 10 |
| Aglaia_lawii | 48 |
| Hopea_glabra | 11 |
| Poeciloneuron_indicum | 56 |
| Diospyros_ridleyi | 7 |
| Pajanelia_longifolia | 9 |
| Litsea_stocksii | 39 |
| Mallotus_resinosus | 74 |
| Xanthophyllum_arnottianum | 62 |
| Ficus_beddomei | 16 |

OPTIONAL diagnostics after the one-species website is verified: to run the
ten reference targets, replace --species with exactly this comma-separated
list, not a random --species_count=10 selection. This is not a mandatory gate:

```text
Goniothalamus_wightii,Aglaia_lawii,Hopea_glabra,Poeciloneuron_indicum,Diospyros_ridleyi,Pajanelia_longifolia,Litsea_stocksii,Mallotus_resinosus,Xanthophyllum_arnottianum,Ficus_beddomei
```

Validate actual successful status per species, nonempty all-tunes/metrics,
finite held-out auc.val.avg (not auc.train), selected model settings, the
`<Species>_SDM.tif`/`<Species>_Plot.png` pair, CRS, coverage, NoData and 0..1
cloglog value ranges. Inspect raster samples at known presences and outside
the WG. Account for every requested species, even if a sparse one is skipped.
Save machine-readable timings and a human-readable smoke report in docs/.

Before full training, verify that the selected full-data model includes all
usable Aglaia_lawii records (not just a holdout subset), and implement Stage
5's frontend/API against its one-species release. On loopback port 8175 if
free, require:

- Original-looking frontend loads its WG asset and queries the local backend
  by both map click and manual coordinate entry; never production fallback.
- Known valid pixel-center scores agree between direct raster sampling and
  API results. Query thresholds just below/above a known score to verify
  filtering. Find a valid in-envelope/WG pixel rather than assuming any
  previously suggested example coordinate will return this species.
- Matching species preview opens; show actual ENMeval evaluation protocol,
  not a made-up AUC or an old baseline value.
- Inclusive latitude-bound filtering, outside-WG, NoData and outside-raster
  behavior are tested. Malformed/nonfinite coordinates and bad thresholds
  yield clear errors. Test missing AUC metadata separately without hiding
  otherwise valid predictions. Small deterministic unit fixtures are fine
  if a rare edge case cannot be exercised by this one real raster.
- Browser console/network inspection shows no missing app assets or calls
  to the production API. OSM basemap calls are separate and expected.
- Restart reloads this release without training. Save API/browser evidence
  and generation/start commands in docs/. If no browser automation is
  available, arrange manual verification before claiming the gate passed.

Only after this gate succeeds may pass 2 begin. Keep the one-species site
available while full training runs separately.

## Stage 4: full training and release

- PASS 2 begins only after the pass 1 website has passed its acceptance gate.
- Explicitly enumerate all unique species from the provided occurrence CSV;
  do not rely on the scaffold's default random ten. Use one-species jobs with
  an immutable run config, logs and status; start with concurrency 1, measure
  RAM, and increase cautiously. Set BLAS/OpenMP to one thread per job.
- Keep block partitions and fc {L,LQ} x rm {1,2} initially. Do not expand the
  modelling grid while debugging infrastructure. Save CV metrics separately
  from final models. Do not directly compare these AUCs with random-background
  or random-holdout legacy AUCs as if they were the same exam.
- Verify the installed ENMeval's selected model uses all valid occurrences
  for its full-data fit under block CV. Save that full-data object, or refit
  explicitly with the selected FC/RM if needed. Do not serve a 70% holdout fit
  merely because a test score exists. Assert n_final against all usable data.
- Publish a normalized release with one canonical species ID per TIFF,
  model-specific previews, selected settings, evaluation protocol and scores,
  raw/usable occurrence counts, source checksums and latitude bounds. Resolve
  filename suffixes/hyphens via explicit mapping, not lossy ad hoc rewriting.
- Latitude envelopes come from the original validated occurrence dataset,
  not CV folds or thinned training subsets. Invalid or missing bounds require
  an explicit unavailable status, never a silent bypass.
- Report every excluded/failed species and why. Do not force fits on tiny
  samples or substitute original maps. Make the release resumable and keep
  all earlier outputs; changing config creates a new run.

## Stage 5: the original-looking site

Implement the API/frontend below during pass 1 with Aglaia_lawii's trained
release, before Stage 4 full training. After pass 2, switch the same website
to the full release, rerun tests and expose its actual release identity.
Never mix predictions from different releases or rebuild a second website.

Use supplied frontend/ and a NEW staging backend; reference the archived
production FastAPI code, not the root Flask code lacking latitude bounds.

Minimum API:
- POST /api/get-results accepts latitude, longitude and minProbability.
- GET /api/species/{species}/map returns the matching new-model preview.
- GET /api/health reports active release and coverage without private paths.

Recommendation behavior:
1. Validate finite coordinates/threshold; enforce WG on the backend even for
   manually entered coordinates. Frontend boundary must load before clicks.
2. Apply inclusive min/max species latitude bounds before recommending.
3. Query the right raster CRS with a single pixel/window, reject masked,
   NoData/nonfinite/out-of-range cells. Never read all rasters into each
   per-request process. Cache bounds/catalog and cap request concurrency.
4. Keep existing slider initially; describe scores as suitability, not actual
   planting success probability. Keep the score's floating precision for
   thresholding and sorting; round only for display.
5. Include a species even if its historical baseline Test AUC row is absent.
   Show its own block-CV evaluation or unavailable metadata with clear labels.
6. Provide only this release's maps. No old baseline PNGs under new-model names.

Set the frontend to same-origin /api calls explicitly: its API URL currently
falls back to the production Cloud Run service. Also handle CRA homepage/base
path settings, SPA history fallback, loading failures and stale requests.
Use `npm ci` then a production build, not a public npm development server.

Serve static frontend and API behind one loopback endpoint, proposed
127.0.0.1:8175. Backend can be behind a reverse proxy or serve built static
assets itself, without exposing data directories. Check the port is free.
Restart must reload the published release without retraining. Persist data
outside images; use a service/Compose config with restart behavior and logs.

Example endpoint test once serving is implemented:

```bash
curl -fsS http://127.0.0.1:8175/api/health
curl -fsS http://127.0.0.1:8175/api/get-results \
  -H 'Content-Type: application/json' \
  -d '{"latitude":10.46675,"longitude":76.8295,"minProbability":50}'
```

An empty result for one query is not itself a failure. Also check boundary,
NoData, input-error and per-species latitude regression cases. The old
Prismatomeris_tetrandra example lat 12.704167/lon 75.704167 lies beyond its
observed max latitude 10.455; if that species has a trained map, it must not be
suggested there even if its raw new-model pixel is high. Do not assume it will
train successfully from sparse observations.

The user will configure plantwise.idli.cc in Cloudflare. Leave existing
tunnels alone and provide the exact loopback origin when ready. On this same
host cloudflared can use http://127.0.0.1:8175; if cloudflared is containerized
elsewhere, loopback routing differs and must be coordinated rather than
binding publicly without approval. Temporary laptop access:

```bash
ssh -N -L 8175:127.0.0.1:8175 beeps@100.82.28.38
```

## Completion checklist

- One-species training AND complete website tests passed BEFORE full training.
- Environment and jar versions captured, predictor mapping correct.
- One-species and explicit ten-species smoke reports retained.
- Full run has success/skip/failure accounting for all 448 species.
- Selected full-data models and matching TIFFs/previews published.
- Original visual identity retained, no ensemble switch or production calls.
- WG, species latitude envelope and raster validity enforced server-side.
- Rebuild/restart preserves results and does not require retraining.
- Localhost endpoint works after restart; Cloudflare origin documented.
- Code commits contain no private CSVs, model outputs, secrets or bulk rasters.
