# Why scores change and observation/cell eligibility

Confirmed the user's recollection: archived runner gate is more than two
observation rows, counted before invoking Maxent. Confirmed current gate is at
least eight distinct usable occurrence cells after filtering, plus four spatial
blocks with at least two validation points each. Multiple records in one cell
count once; exactly eight is sufficient for the count gate, not a guarantee
that all remaining model checks pass.

Added the requested Old/New score explanation to /model and a100 observations
in5 cells example. Published a new immutable frontend, retained rollback and
restarted only our service. Build/browser checks and screenshot inspection
passed on desktop/mobile. No training, models, backend or filter changes.
See docs/diff-view.md and ignored runtime/score-explanation-20261112/.


At20:12, emphasized the observation-row versus unique-cell gate and added it to
the table. Verified raster resolution directly, then added a bracketed cell-size
line (30 arc-seconds square, approximately0.9km on each side in WG). Rebuilt,
published and checked desktop/mobile; screenshot inspected. Evidence in
runtime/cell-size-20261112/. Previous frontend retained.
