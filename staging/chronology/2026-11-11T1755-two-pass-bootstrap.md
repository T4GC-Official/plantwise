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
