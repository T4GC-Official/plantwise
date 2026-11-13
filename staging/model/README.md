# Model training

[enmeval/train.R](enmeval/train.R) is the production training entry point.
[scripts/train_jobs.py](scripts/train_jobs.py) launches isolated, resumable
per-species jobs. [environment/Dockerfile.training](environment/Dockerfile.training)
defines the ARM64 training image. Optional bias/block helpers live in enmeval/;
they are not substitutes for the production runner.

Inputs, including private files, are specified in [data/README.md](data/README.md).
Each job writes status, cleaning counts, four-block evaluation, selected model,
GeoTIFF, preview, metrics and provenance under runs/<run>/<species>/.
Validated releases under releases/<release>/ contain serving-ready artifacts,
accounting, the WG boundary, catalogue and checksums. Both directories are ignored.

From repository root (these commands train; use fresh IDs):

```bash
staging/.venv/bin/python staging/model/scripts/train_jobs.py smoke_NEW_ID --species Aglaia_lawii
staging/.venv/bin/python staging/model/scripts/release.py staging/model/runs/smoke_NEW_ID smoke_NEW_ID --expected 1
# Full training only after the real website/API/browser gate passes:
staging/.venv/bin/python staging/model/scripts/train_jobs.py full_NEW_ID --gate staging/runtime/pass1-gate.json
```

Existing run configurations remain immutable and retain historical paths.
This layout/code change changes fingerprints: create a new run ID rather than
trying to resume an old run under different code. Jobs within a new unchanged
run resume normally. No training was performed as part of the layout migration.
For image setup, publication, resource limits and scientific gates see
[the runbook](../docs/runbook.md) and [remaining gates](../docs/todos/).
