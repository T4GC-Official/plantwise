# Git asset audit, 2026-11-13

Checked current tracked files and all nonignored untracked files, then checked
new Git blobs in origin/main..HEAD. Private runtime evidence is under
runtime/git-audit-20261113/; no private audit inventory is committed.

## Findings

No nonignored untracked files were over1MiB. Private occurrence CSVs, BIO TIFFs,
WG geometry, effort background, trained models, releases, frontend builds,
virtual environments and browser/runtime evidence are ignored. No credentials
were found by high-confidence private-key, GitHub-token, AWS-key or Google
OAuth-secret patterns across tracked and then-nonignored text files. This is a
scoped file/pattern review, not a claim that every possible secret is detectable.

Four pre-existing tracked public assets are over1MiB:

| Path | Bytes |
|---|---:|
| frontend/habitability-tool/src/images/divya_image.jpg | 8,814,274 |
| staging/serving/frontend/src/images/divya_image.jpg | 8,814,274 |
| model/Ecology and Evolution - 2021 - Bharti - Spatial patterns of phylogenetic diversity and endemism in the Western Ghats  India.pdf | 1,356,797 |
| reports/report_manifest.js | 1,164,083 |

These are public photo/paper/report assets already in Git, not private training
data or secrets. Ignore rules do not retroactively untrack existing files.
The pre-existing maxent.jar and historical aggregate AUC tables are also tracked;
they are not private occurrence inputs. No new blob over1MiB or newly named
occurrence/background/GeoTIFF/model/key files appeared in the pending commit
history checked against origin/main. The duplicate photo reuses an existing blob.

## Ignore updates

Ignored the entire local archive/plantwise_v0/ and root SYNC_SHA256SUMS* transfer
manifests, rather than only its legacy TIFF directory. Added local .env/variant,
PEM and key exclusions while keeping .env.example/.env.sample trackable.
The separately tracked staging/archive/legacy runner source remains public;
no local legacy datasets or reports are added. No files were deleted or untracked.

Use git ls-files --others --exclude-standard to inspect remaining candidates,
and git check-ignore -v on any private input before adding files. The detailed
private input/serving inventory is model/data/README.md. Service files contain
no credentials and do not change Cloudflare Access configuration.
