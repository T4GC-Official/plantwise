# Processing improvements

The imported scripts coupled data cleaning, tuning, plotting and publication,
used random-ten defaults and swallowed exceptions. The staging runner now
requires one named species and a fresh attempt directory, with terminal status
separate from artifacts. Remaining improvements worth evaluating:

- Materialize a versioned masked predictor stack and validated background once
  per input configuration; avoid repeating extraction/hash work for every job.
- Define ecological minimum-data criteria with domain review; the operational
  gate (>=8 unique cells, >=2 presences per spatial block, finite AICc with
  ncoef < n-1) is an explicit conservative starting policy, not a claim of
  ecological adequacy. Diagnose spatial concentration separately from low n.
- Separate immutable run manifests from execution events, and fit artifacts
  from release packaging. Publish only after full validation and accounting.
- Bias surface was derived using pooled observations. Quantify sensitivity and
  potential leakage before treating block CV as independent validation.
- Replace CRA in a separate reviewed change; do not combine a framework rewrite
  with model validation. Pin builds and inspect dependency security findings.
- Add independent ecological evaluation and data-drift checks before allowing
  automatic retraining/promotion on newly collected data.

Environment build: capture package tarballs or an archived CRAN repository for
all packages in R-packages.csv and simplify the currently cached two-attempt
installation Dockerfile. Final image is verified and pinned locally by content
ID, but a future CRAN/apt rebuild is not bit-reproducible without source snapshots.

Serving build: always snapshot finished frontend output before switching its
runtime symlink. CRA regenerates build/ in place, so serving that directory
causes transient missing assets during rebuilds; the implemented snapshot fixes
this operational issue while keeping an eventual framework migration separate.

Frontend lifecycle follow-up: remove remaining commented blocks in a separate
cleanup and release Leaflet maps on component unmount, including aborting an
in-flight boundary fetch. Current functional navigation/browser gate passes,
but repeated long-session route changes deserve a memory/lifecycle regression.

Raster grid policy: terra's crop/write path changed the x pixel spacing by
~1.5e-17 degrees. Original observations exactly on cell edges can select adjacent
cells between raw and cropped grids. Independent validation now compares exact
output pixel centers, which all 268 models pass. For future processing, persist
one canonical grid/transform/cell-ID mapping and explicitly define tie behavior
for edge coordinates, so masking, deduplication and verification all share it.

Visual/entrypoint acceptance: compare settled screenshots against the original
at desktop and phone sizes, including a scrolled results view. Keep operator
metadata out of the product layout. Test the actual user-facing forwarding URL,
not only loopback, and include empty/non-JSON gateway responses. The GET endpoint
is suitable for read-only recommendations; transport parity tests must retain
all spatial and numeric validation.

Model acceptance follow-up from the read-only live comparison: inspect
AICc-selected zero-coefficient/constant full-data models explicitly. A constant
cloglog map can exceed the default50 threshold while having poor held-out
performance. Define/report this quality gate with domain review before any
future filter or retraining-policy change; the comparison changed neither.
Record original-map provenance (scale, background, features, fitted sample set,
software and geometry) alongside TIFFs so old/new score differences can be
attributed rather than guessed from a later edited trainer.
