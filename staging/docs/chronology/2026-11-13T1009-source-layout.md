# Separate model, serving and documentation areas

Grouped training code, helpers, private inputs, runs and releases under model/.
Grouped backend, frontend, serving tests, diagnostics and deployment under
serving/. Moved timeline/narrative/todos/proposals under docs/ and original
handoffs/imported experiments under archive/. Root README now points to the
active staging tree; historical root implementations remain untouched.

Updated model/container roots, serving paths, promotion, dependencies, test
imports and the project's user service. Temporary artifact compatibility links
kept the loaded process usable during migration and were retired into the
ignored archive after restart. Source and input bytes were retained; only code
path references changed. Existing training configs remain immutable; retraining
with the new code/layout needs a new run ID. New unchanged runs remain resumable.

Validation: 31 API tests; live original raster/API checks including real NoData
and latitude bounds; full release checksum validation; real desktop/mobile
comparison browser checks; independent saved smoke model reload in a fresh JVM
with zero prediction error. No retraining or scientific-filter changes. Evidence
is ignored under runtime/layout-verification/. Only our service was restarted.

Committed the layout checkpoint before the requested declaude alias. The next
checkpoint adds source references; no pushes are part of this work.


The first declaude alias completed after the layout commit, inspecting16 local
commits against origin/main; no commit IDs changed. Added a byte-identical
archived runner reference and fixed-file plain-text source routes, then linked
all Old/New labels. The source references work locally before pushing.
Verified32 backend tests, desktop/mobile actual link clicks, raw source content,
original UI regression and screenshots. Published frontend-20261113T044141Z with
rollback retained. A second local checkpoint and final requested declaude run
complete the review preparation; no pushes are performed.
