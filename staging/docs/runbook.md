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
