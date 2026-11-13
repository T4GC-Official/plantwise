# Website and API

backend/app.py serves one immutable model release per process, the React frontend
snapshot, local APIs, /diff and /model. backend/comparison.py reads staging model
artifacts and fetches live scores at zero cutoff. frontend/ contains the original
PlantWise look and the additional comparison pages.

From repository root:

```bash
uv venv staging/.venv
uv pip install --python staging/.venv/bin/python -r staging/serving/environment/requirements.lock.txt
cp staging/serving/environment/plantwise.service ~/.config/systemd/user/plantwise-staging.service
systemctl --user daemon-reload
systemctl --user restart plantwise-staging.service
staging/.venv/bin/python -m pytest staging/serving/tests -q
staging/.venv/bin/python staging/serving/tests/verify_live.py
```

The service cwd is staging/serving, using staging/.venv. Runtime pointers remain
at staging/runtime/active and staging/runtime/frontend-active; model releases
live at staging/model/releases/. Promote with scripts/promote.py and restart
only plantwise-staging.service. No training process is needed for serving.

Build frontend/ in an isolated Node container, copy its build/ into a new
staging/runtime/frontend-TIMESTAMP directory, then atomically replace
frontend-active and restart our service. Never rebuild the served directory.

Browser checks mount staging at /work and runtime/browser at /browser:

```bash
docker run --rm --name plantwise-diff-check --network host \
  -e PLANTWISE_DIFF_ORIGIN=http://100.82.28.38:8175 \
  -e PLANTWISE_DIFF_EVIDENCE=/work/runtime/layout-verification \
  -v "$PWD/staging:/work" -v "$PWD/staging/runtime/browser:/browser" \
  mcr.microsoft.com/playwright:v1.61.0-noble node /work/serving/tests/diff-browser.cjs
```

comparison/ holds optional read-only investigations of archived/live behavior.
The source snapshot at root archive/plantwise_v0 supplies historical metadata
for /diff. It is not a training input and must never be executed as a service.
See [the runbook](../docs/runbook.md) and [comparison operations](../docs/diff-view.md).


/model links each Old/New label to the complete legacy/current runner. The
fixed /source/old/InitialImplementation.py and /source/new/train.R routes serve
text/plain directly from the repository, so reviewers can use them before a
GitHub push. No training data or arbitrary files are exposed by these routes.
