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
