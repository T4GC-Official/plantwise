# Explicit comparison and UI punctuation

Map selection updates coordinates/marker only; comparison now requires form
submission, including on first load. Added changed-location notice for results
from the prior query. Replaced dot/dash separators with ASCII hyphens, removed
decorative arrows/disclosure marker and renamed disclosure to Why?.

Updated browser checks to verify no requests on initial load or repeated map
selection and full-precision selected coordinates on Compare. Desktop/mobile
checks and visual screenshot inspection passed after publishing a fresh
immutable frontend. Previous frontend retained; only our staging service
restarted. No backend, model or training changes. Evidence and commands are in
docs/diff-view.md and ignored runtime/explicit-compare-20261113/.

Inspected the repository layout to discuss model/serving separation. Root README
still describes baseline code; active training and serving are under staging.
No restructuring, source moves, root README edits or data moves performed.
