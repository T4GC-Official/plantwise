# Expert review copy and comparison table

Applied the user's specific copy edits to /model and /diff. Replaced vague
inventory wording with original514 versus staging448 source species coverage.
Defined usable cells, missing BIO layers, the minimum-eight gate and query-time
latitude/NoData behavior. Removed the requested explanatory/caution sections.

Removed the difference column; preserved Why / details and show staging block-CV
AUC next to live-reported AUC there. Excluded models explicitly have unavailable
staging AUC. Changed the diff title to the map instruction.

Built a new immutable frontend, switched frontend-active and restarted only
plantwise-staging.service. Browser checks passed on desktop/mobile over the
Tailscale address; visually inspected screenshots. Retained previous frontend
and evidence. No backend, models, training, filters, cloudflared or other service
changes. Operational details are in docs/diff-view.md.
