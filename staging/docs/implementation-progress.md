# Implementation progress

Scope: staging/enmeval-nov-2026, exact supplied 448-species CSV, BIO1–19,
WG polygon, fixed supplied effort-weighted background, ENMeval Java Maxent.
No ensemble, extra species, BIO20, production maps, host package install,
cloudflared changes, deletion or push.

## Environment bring-up

Initial imported checksums all passed. First training image build failed because
Ubuntu 24.04 does not package r-cran-dismo. Removed that apt dependency; CRAN
installation inside the image will supply it. Python Fiona source build lacked
GDAL headers: avoided that unnecessary dependency, using pyshp + pyproj for the
supplied polygon, rasterio wheels for raster IO. Python environment isolated in
staging/.venv; tested versions captured in environment/requirements.lock.txt.

Frontend npm ci detected missing Bootstrap in the imported lockfile. Repair via
npm install --package-lock-only inside Node 22 container, then npm ci. Original
React, Bootstrap, Leaflet appearance retained. Same-origin API enforced.

Inspection of the actual ENMeval 2.0.5.2 source established that maxent.jar
uses predicts::MaxEnt (not dismo). Runner uses predicts' actual Java directory
and explicit predicts dispatch. Its full-data model list is assembled from
mod.full. Assert saved model presence count equals every usable occurrence.

## Current gate

Pass 1 is pending environment installation and real training. Full training must
not begin until real API AND browser evidence is saved. No success claimed yet.

Commands and final operational state will be maintained in runbook.md; event
history in ../chronology/, thematic account in ../narrative/, remaining gates
in ../todos/, processing improvements in ../proposals/.

## Checkpoint validation

`staging/.venv/bin/python -m pytest staging/tests -q`: 12 passed. These fixtures
exercise rare NoData/out-of-raster/latitude boundary cases and absent AUC, and
supplement rather than replace the pending real Aglaia gate. Production frontend
build succeeds. Obsolete Learn React test and commented alternative components
are preserved in archive/, with active methodology updated to this run.

R installation diagnostics: units requires Rcpp >=1.1.0, fs needs libuv headers,
and current dbplyr needs the current dplyr filter_out export. Image repair installs
libuv1-dev, Rcpp and dplyr then retries exact ENMeval 2.0.5.2 with load assertions.

Actual installed environment: R 4.3.3 ARM64, ENMeval 2.0.5.2, predicts 0.2.2,
rJava 1.0.11, terra 1.7.65, raster 3.6.26, dismo 1.3.16, dplyr 1.2.1.
These differ from laptop versions and are recorded explicitly, not described
as exact numerical reproduction. Java Maxent loaded 3.4.4 from the supplied jar.

First model success smoke_20261111T1240Z; release serialization rejected rounded
latitude bounds. Precision fixed and fresh smoke_20261111T1246Z started.

## Completed state

See full-release-report.md for the final results: all 448 species accounted,
268 successful full-data models, 180 exclusions, zero failures. The full release
is active on 127.0.0.1:8175 after API/browser, independent RDS reload, restart,
actual smoke rollback and full re-promotion checks. Input checksums still match.
The detailed earlier entries above are the chronological bootstrap record.
