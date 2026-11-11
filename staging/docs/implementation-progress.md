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
