# PlantWise managed service

This directory is the source of truth for plantwise-staging.service. Like
Pyrocene services, the installed user unit is a symlink to the repository file,
not a separate edited copy. The service listens on **0.0.0.0:8175** so the
existing Cloudflare origin at http://localhost:8175 and Tailscale links both work.
No other application or cloudflared unit is managed here.

## Private assets and environment

Follow [the input inventory](../../model/data/README.md) for observations,
bioclim layers, boundary, background and pretrained serving assets. Training
needs BIO1-19; serving an existing release needs its prediction maps instead.
The frontend WG JSONL and optional /diff metadata are listed separately there.
From repository root:

```bash
uv venv staging/.venv
uv pip install --python staging/.venv/bin/python -r staging/serving/environment/requirements.lock.txt
staging/.venv/bin/python staging/serving/scripts/promote.py RELEASE_ID
```

## Build and publish the frontend

Restore staging/serving/frontend/public/wgg.geojsonl.json first. Build in an
isolated ARM64 container using the committed npm lockfile:

```bash
docker run --rm --name plantwise-frontend-build --cpus 2 --memory 4g \
  -v "$PWD/staging/serving/frontend:/work" -w /work \
  mcr.microsoft.com/playwright:v1.61.0-noble bash -c 'npm ci && npm run build'
```

Publish to a fresh immutable directory, never rebuild the directory being served:

```bash
staging/.venv/bin/python - <<'PYCODE'
from datetime import datetime, timezone
from pathlib import Path
import os
import shutil
runtime = Path('staging/runtime')
runtime.mkdir(exist_ok=True)
target = runtime / ('frontend-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
shutil.copytree('staging/serving/frontend/build', target)
next_link = runtime / 'frontend-next'
next_link.symlink_to(target.resolve())
os.replace(next_link, runtime / 'frontend-active')
PYCODE
```

## Install and everyday commands

```bash
python3 staging/serving/services/manage.py install
python3 staging/serving/services/manage.py start
python3 staging/serving/services/manage.py status
python3 staging/serving/services/manage.py logs
python3 staging/serving/services/manage.py restart
python3 staging/serving/services/manage.py stop
python3 staging/serving/services/manage.py disable
```

install creates the unit symlink, reloads systemd and enables startup. start
and restart wait for both the expected model release health and homepage on
127.0.0.1:8175. restart reloads the repository unit first. stop lasts until a
manual start or reboot; disable stops and disables boot startup. Restart on
failure is automatic. Logs go to the user journal.

The unit uses %h/src/github.com/bprashanth/plantwise as its checkout location.
On a different checkout location, adjust this repository unit before installing.
The manager refuses to overwrite an unrelated or copied installed unit. Existing
copies must be inspected and preserved before migrating to the repository link.

Boot without an interactive login requires user lingering. On this host,
loginctl show-user beeps -p Linger reports yes and the unit is enabled. For a
new host, its administrator must enable lingering for the service user if needed.
Do not change lingering or lifecycle for other users/services.

## Cloudflare and verification

Public URL: https://plantwise.idli.cc/ behind the user's Cloudflare Access gate.
The tunnel stays pointed at http://localhost:8175. No tunnel or Access policy
changes are performed by the manager. Unauthenticated access redirects to the
Cloudflare sign-in screen; completing email-code login requires an authorized user.

```bash
curl -fsS http://127.0.0.1:8175/api/health
staging/.venv/bin/python staging/serving/tests/verify_live.py
staging/.venv/bin/python -m pytest staging/serving/tests -q
```

Current full release is full_20261111T1252Z (268 models, 180 exclusions).
To roll back, promote the retained smoke_20261111T1246Z and restart; restore the
full release with the same commands afterward. Frontend rollback independently
points frontend-active at a retained snapshot before restarting. Private release
files and frontend snapshots remain ignored. The previous copied installed unit
is retained under runtime/managed-service-20261113/previous-installed.service.
