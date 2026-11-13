# Active PlantWise model and website

This is the current implementation. Training and serving have separate source
trees. Historical code and handoff instructions are under archive/.

```text
staging/
  README.md
  model/
    README.md
    enmeval/          train.R, bias/background and block helpers
    maxent/           private maxent.jar
    scripts/          resumable jobs, accounting, release validation
    environment/     isolated ARM64 training Dockerfile
    data/             private training inputs and derived background
    runs/             private immutable run configurations and job outputs
    releases/         private validated model releases
  serving/
    README.md
    backend/          FastAPI API, raster sampling, live comparison
    frontend/         React/Leaflet website
    scripts/          release promotion
    comparison/       read-only legacy/live diagnostics
    tests/            API, real-release and browser checks
    environment/      Python/browser dependencies
    services/         repository-owned systemd unit and lifecycle manager
  docs/               operations, chronology, narrative, todos, proposals
  archive/            superseded code, source handoff, imported references
  runtime/            private active pointers, frontend snapshots, evidence
  .venv/              private isolated Python environment
```

## Model and inputs

The runner is [model/enmeval/train.R](model/enmeval/train.R), launched by
[model/scripts/train_jobs.py](model/scripts/train_jobs.py). It uses ENMeval
Java Maxent, effort-weighted background, BIO1-19 and the WG polygon. Eligible
species need at least eight distinct usable occurrence cells, with at least
two validation presences in each of four geographic blocks. No ensemble,
BIO20 or additional 66 original-source species are used.

See [the data inventory](model/data/README.md) for exact required files, formats,
provenance and private-file policy; files remain documented even when absent
from a fresh clone. [Model operations](model/README.md) cover training and output.

## Serving

Public URL: https://plantwise.idli.cc/ behind Cloudflare Access. The persistent
[service manager](serving/services/README.md) keeps the origin on port 8175 and
starts at boot. Training and serving asset placement is documented in
[model/data/README.md](model/data/README.md), including frontend map/comparison assets.

The active site is http://100.82.28.38:8175/ on Tailscale (bound to 0.0.0.0:8175).
/diff compares the active model release against the live PlantWise India API;
/model explains training differences. Map selection does not submit a query.
The original appearance remains available at / and /#/tool.

[Serving instructions](serving/README.md) and [runbook](docs/runbook.md) explain
setup, release selection and rollback. Current model release:
full_20261111T1252Z, 268 successful models, 180 exclusions, zero failures.
The one-species smoke_20261111T1246Z release remains available for rollback.

## Verify from the repository root

```bash
staging/.venv/bin/python -m pytest staging/serving/tests -q
staging/.venv/bin/python staging/serving/tests/verify_live.py
staging/.venv/bin/python staging/model/scripts/train_jobs.py --help
```

## Layout migration

The former staging/models, scripts, data, runs and releases were grouped under
model/; backend, frontend, tests and serving dependencies moved under serving/.
The model runner now mounts staging/model at /work in its training container.
The backend resolves staging/runtime independently of its source directory.
Model files, release checksums and input bytes were not changed.

Historical run configs/provenance keep their original paths and fingerprints.
They are evidence, not editable configuration: use a new run ID for training
with this reorganized code. New runs remain resumable under an unchanged
fingerprint. Archived docs/timeline entries may show pre-migration paths; the
current README and runbook define current commands. Do not execute archived
training or cleanup scripts. Temporary compatibility links used during migration
are retained only under archive/layout-compat, not as active source paths.

Project history: [chronology](docs/chronology/), [narrative](docs/narrative/),
[remaining work](docs/todos/) and [proposals](docs/proposals/).
