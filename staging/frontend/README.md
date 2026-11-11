# PlantWise Frontend

This directory contains the Create React App frontend for the baseline `PlantWise_v0` snapshot.

## Install

```bash
npm install
```

The app depends on the tracked `package.json` and `package-lock.json` in this directory. `node_modules/` is intentionally ignored.

## Run

```bash
npm start
```

## Build

```bash
npm run build
```

The generated `build/` directory is ignored. The checked-in `build_history/` directory is only a historical snapshot and is not used as the active build output.

## Data assets

The app expects some static data files in `public/`, including:

- `wgg.geojsonl.json`
- `species_presence.csv`
- image assets under `public/images/`

The image assets are tracked. The data files above are intentionally not tracked in the baseline repository and must be seeded manually before running the full app.
