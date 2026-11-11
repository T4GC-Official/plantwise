# Training environment and modelling contract

Native ARM64 Ubuntu 24.04 image plantwise-training:20261111; verified image ID
sha256:0db7efd59d9c7a9b312f21366f7b0f1853129560e3c1ec42f796968b4bb252b8.
R 4.3.3, ENMeval 2.0.5.2, predicts 0.2.2, rJava 1.0.11, terra 1.7.65,
raster 3.6.26, dismo 1.3.16, dplyr 1.2.1. See successful job sessionInfo.txt,
R-packages.csv and provenance.json for the complete tested snapshot. Container
Java version is captured in runtime/training-environment.txt.

The ENMeval version is pinned; older laptop R/terra/rJava versions were not
silently asserted. Current CRAN dependency changes required Rcpp/dplyr updates
and libuv headers. The Dockerfile retains the initial dependency-attempt layer,
then repairs it and asserts real package loads. This preserves the locally
cached installation history; simplifying the build to a fully archived package
source lock is an improvement recorded in proposals/.

Input CSV SHA256 is checked at startup against the supplied immutable hash.
Files are constructed numerically for BIO1–19 and recorded with assigned names
and SHA256. Exact WG polygon masks the stack. Coordinates must be finite,
geographically valid, inside WG and complete in every predictor. Occurrence
cells deduplicate before splitting; counts retain every stage. Fixed supplied
bias-background coordinates are validated against all layers; no uniform
fallback. Historical bias CSV environmental columns are never used.

Operational minimum: eight unique cells and all four block validation groups
with at least two presences each. Sparse data exclusions and partition/model
failures are explicit. This gate does not imply ecological adequacy. All four
FC/RM tuning rows are retained; selection requires finite held-out AUC and
AICc and ncoef < n-1; ties use AICc, ncoef, FC, RM order. The selected ENMeval
full-data model must have n_final equal to n_usable. CBI is unavailable because
ecospat is absent; reported evaluation is held-out block AUC with full supplied
background. It is not an independent external test of the pooled bias surface.

Maxent jar is copied into each disposable container's isolated predicts Java
library before JVM class loading. Configured hash, actual Java class origin,
loaded jar hash and version must agree. Supplied version is 3.4.4, SHA256
4c856e55412f70c5597b03cf9aaaf27e0782e0921f937262273b68bdcb8fee5e.
Explicit predicts::predict S4 dispatch requests outputformat=cloglog; final map
values are compared at every usable occurrence with direct Java predictions.
No extra predictors, species, thinning, ensemble or old-model fills are used.
