# Experiment Service

`src/` contains a newer experiment/debugging flow layered on top of the `PlantWise_v0` baseline runner.

It provides:

- a small Flask backend in `src/backend/`
- a static frontend in `src/frontend/`
- validation and single-species run execution into isolated run directories

## Config

Config lives at:

```text
src/backend/config/config.json
```

Important keys:

- `run_root`
  Parent directory where experiment runs are stored.
- `seed_data`
  Seed CSV loaded at server startup and treated as the base dataset that uploaded CSV rows are added to.
- `maxent_args`
  Default Maxent args used when the form leaves args empty.
- `maxent_allowed_args`
  Allowed Maxent arg names for validation.

`run_root` is also used when report manifests are rebuilt, so experiment report bundles are discovered from the configured run directory rather than a hardcoded `experiments/` path.

Note on `randomtestpoints`:

- `randomtestpoints=30` means roughly 30% of the presence records are held out as test data, not 30 absolute points.
- If a species has only a small number of records, Maxent applies its own internal rounding when splitting train vs test, so very small species can become unstable or fail if too few training points remain.

By default, `seed_data` points to the repository-root `Final_Species.csv` in `PlantWise_v0/`.

## Install

From `PlantWise_v0/`:

```bash
uv venv .srcvenv
source .srcvenv/bin/activate
uv pip install -r src/requirements.txt
```

## Run

From `PlantWise_v0/`:

```bash
source .srcvenv/bin/activate
python3 ./backend/app.py
```

Then open:

```text
http://127.0.0.1:5050/
```

## Docker 

```
$ cd ../

# Run from the root dir 
$ docker build -t plantwise-v0-regression:0.1 .
$ docker run --rm -p 5050:5050 plantwise-v0-regression:0.1
```

## Notes

- Uploaded CSVs must match the seed schema exactly:
  - `Species,Latitude,Longitude`
- Runs are stored under the configured `run_root`.
- Generated experiment reports are folded into the same regression manifest used by `reports/index.html`.
- `generate_reports.py` is invoked automatically by the backend at the end of a successful experiment run, so you do not need to run it manually for experiments.
