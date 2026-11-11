# Local operations

All commands start at /home/beeps/src/github.com/bprashanth/plantwise.
This file records reproducible implementation commands; successful runtime
identities and test evidence are added after their gates pass.

## Build isolated environments

```bash
docker build --cpuset-cpus=0-1 -t plantwise-training:20261111 -f staging/environment/Dockerfile.training staging/environment
uv venv staging/.venv
uv pip install --python staging/.venv/bin/python -r staging/environment/requirements.lock.txt
docker run --name plantwise-frontend-rebuild --cpus 2 --memory 4g -v "$PWD/staging/frontend:/app" -w /app node:22-bookworm bash -c 'npm ci && npm run build'
```

The initial imported frontend lockfile required npm install --package-lock-only;
the committed repaired lockfile supports npm ci. No global Node/R install.

## Pass 1

```bash
staging/.venv/bin/python staging/scripts/train_jobs.py smoke_YYYYMMDDTHHMMSSZ --species Aglaia_lawii
staging/.venv/bin/python staging/scripts/release.py staging/runs/smoke_YYYYMMDDTHHMMSSZ smoke_YYYYMMDDTHHMMSSZ --expected 1
staging/.venv/bin/python staging/scripts/promote.py smoke_YYYYMMDDTHHMMSSZ
```

## Website

```bash
mkdir -p ~/.config/systemd/user
cp staging/environment/plantwise.service ~/.config/systemd/user/plantwise-staging.service
systemctl --user daemon-reload
systemctl --user enable --now plantwise-staging.service
curl -fsS http://127.0.0.1:8175/api/health
```

The service is dedicated to this staging project; no existing service changes.
Release promotion updates runtime/active atomically; restart the service to load
it. A running process stays on the same resolved release for all requests.
Rollback uses promote.py with the retained smoke release then a service restart.

## Pass 2 (only after saved real pass-1 evidence)

```bash
staging/.venv/bin/python staging/scripts/train_jobs.py full_YYYYMMDDTHHMMSSZ --gate staging/runtime/pass1-gate.json
staging/.venv/bin/python staging/scripts/release.py staging/runs/full_YYYYMMDDTHHMMSSZ full_YYYYMMDDTHHMMSSZ --expected 448
staging/.venv/bin/python staging/scripts/promote.py full_YYYYMMDDTHHMMSSZ
systemctl --user restart plantwise-staging.service
```

Same run ID skips terminal success/exclusion/failure states. Interrupted attempts
are retained under timestamped names. Failed species are accounted honestly;
fixing code/config requires a new run, never overwriting earlier results.

No deletion commands, global package changes, git push or tunnel changes are
part of operations. Runtime, training data, models, maps and private geometry
are ignored. Cloudflare origin, once tested, is http://127.0.0.1:8175; public
domain setup is the user's responsibility and has not been tested.

## Actual smoke release and browser commands

The active smoke release is `smoke_20261111T1246Z`; code/data runtime artifacts
remain ignored. Training image ID:
`sha256:0db7efd59d9c7a9b312f21366f7b0f1853129560e3c1ec42f796968b4bb252b8`.

```bash
staging/.venv/bin/python staging/tests/verify_live.py
staging/.venv/bin/python -m pytest staging/tests -q
docker run --name plantwise-browser-UNIQUE --network host --cpus 2 --memory 2g -v "$PWD/staging:/work" -v "$PWD/staging/runtime/browser:/browser" -w /work mcr.microsoft.com/playwright:v1.61.0-noble node tests/browser.spec.cjs
```

Install the browser package into ignored runtime/browser using the committed
browser-package.json and browser-package-lock.json (copy as package.json and
package-lock.json then npm ci). Runtime screenshots and detailed network logs
stay out of Git. Browser images and OS packages remain project-isolated.

The frontend is served from runtime/frontend-active, a symlink to an immutable
copy of a successful build (current frontend-20261111T1250Z). After npm build,
copy build/ into a NEW runtime/frontend-<timestamp> directory, update the symlink
atomically and restart only plantwise-staging.service. Do not serve CRA's build/
directly while rebuilding. The API release and frontend snapshot resolve once
at process start. Preview requests carry the result's release identity and get
a clear 409 if a promotion occurred since that prediction.

Actual full run planned: full_20261111T1252Z, --workers 3, max six CPU/24 GiB
container caps; serial warmup and two-job ramp before the three-job ceiling.
Per-job resources.json records sampled Docker CPU/RAM. Total working usage is
expected below caps; monitor the shared host while jobs progress.

Progress without exposing occurrence records:

```bash
staging/.venv/bin/python staging/scripts/progress.py staging/runs/full_20261111T1252Z
tail -n 30 staging/runtime/full-20261111T1252Z.log
systemctl --user status plantwise-staging.service --no-pager
journalctl --user -u plantwise-staging.service -n 30 --no-pager
```

Measured serial/two-job warmup uses ~2.3–2.4 GiB per training container and about
one CPU each, with >40 GiB host memory available. Ceiling3 therefore leaves
substantial room within the shared host; per-container 8GiB/two-CPU limits stay.
