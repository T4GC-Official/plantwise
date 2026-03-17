# PlantWise

`PlantWise` is the baseline code snapshot of the PlantWise India model and web app before improvements from the newer `PlantWise` tree are ported over.

This repository intentionally does not track private or manually seeded datasets. Contributors are expected to populate those files locally before running the web app, training the model, or comparing outputs.

Baseline policy:

- Only code and dependency metadata are part of this baseline.
- The Maxent binary is not tracked in this repository.
- Private/manual datasets are not tracked in this repository.

## What is tracked

- Model source code in the repo root.
- Backend source in `backend/app/`.
- Frontend source in `frontend/habitability-tool/`.
- Dependency manifests such as `requirements.txt` and frontend `package.json` files.

## What is not tracked

- Private or manually seeded datasets.
- Environmental raster layers.
- Trained model outputs.
- Local build outputs and dependency directories.
- Virtual environments and editor noise.

## Python setup

Create a fresh virtual environment and install the minimum tracked Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Frontend setup

The actual React app lives in `frontend/habitability-tool`.

```bash
cd frontend/habitability-tool
npm install
npm start
```

There is also a legacy `frontend/package.json` at the parent level (recorded for baseline accuracy). Treat `frontend/habitability-tool/package.json` as the source of truth for the web app.

## Manual data bootstrap

### 1. To run the end-to-end web app

The backend can serve predictions without the full training inputs, but it does require precomputed model outputs and summary metadata.

Desired local filesystem:

```text
PlantWise_v0/
  backend/
    app/
      data/
        auc_and_contributions.csv
        final_tif_files_withNWG/
          <species>.tif
          ...
  frontend/
    habitability-tool/
      public/
        wgg.geojsonl.json
        species_presence.csv
```

What each file is for:

- `backend/app/data/auc_and_contributions.csv`
  Used by the backend to attach AUC values to API results.
- `backend/app/data/final_tif_files_withNWG/*.tif`
  Used by the backend to look up suitability scores for requested coordinates.
- `frontend/habitability-tool/public/wgg.geojsonl.json`
  Used by the map UI to draw the geography layer.
- `frontend/habitability-tool/public/species_presence.csv`
  Used by the frontend download link on the "Our Model" page.

None of the above are tracked in git in this baseline.

### 2. To train the model

Training requires the source occurrence dataset, the environmental layers, and the Maxent binary. The script trains on the species CSVs found in `sp_data_final/`, which are generated from `Final_Species.csv`, and it reads the weather/environmental layers from `final_attributes/`.

Maxent binary source and version:

- Source location: https://biodiversityinformatics.amnh.org/open_source/maxent/
- Version used in the existing `PlantWise` workspace jar: `3.4.4`
- Expected location in `PlantWise_v0`: `PlantWise_v0/maxent.jar`

How to verify the version from a jar:

```bash
$ jshell --class-path maxent.jar <<'EOF'
> System.out.println(density.Utils.getVersion());
> EOF
|  Welcome to JShell -- Version 17.0.17
|  For an introduction type: /help intro

jshell> 3.4.4
```

In this workspace, running that against `PlantWise/maxent.jar` shows that `density.Utils.version` is initialized to `3.4.4`.

How to sanity-check that the jar is runnable in headless mode:

```bash
java -Djava.awt.headless=true -cp maxent.jar density.MaxEnt visible=false nowarnings
```

That command may still fail later if input layers are missing, but it confirms that Java can load the Maxent main class from the jar.

Desired local filesystem:

```text
PlantWise_v0/
  Final_Species.csv
  maxent.jar
  final_attributes/
    wc2.1_30s_bio_*_fc.asc
    wc2.1_30s_bio_*_fc.prj
    wc2.1_30s_bio_*_fc.tif
    wc2.1_30s_bio_*_fc.asc.aux.xml
    maxent.cache/
      ...
```

Generated at runtime:

```text
PlantWise_v0/
  sp_data_final/
  pr_sp_data_final/
  res/
  tif_data_final/
```

Notes:

- `separateSpecies.py` reads `Final_Species.csv` and creates `sp_data_final/`.
- `InitialImplementation.py` reads species CSVs from `sp_data_final/` and environmental layers from `final_attributes/`.
- `maxent.jar` must exist in the repository root next to `InitialImplementation.py`.
- The source occurrence and raster data are not in git. They must be seeded manually from the restricted dataset location below.
- None of the source data or generated outputs above are tracked in git in this baseline.

Dataset source:

- Data location: https://drive.google.com/drive/folders/1Z0fG6c9xir-KALGFmKkOPUeF1LxHJ-EF?usp=drive_link
- Access: restricted

### 3. To verify regressions

Regression verification should prefer derived, non-sensitive artifacts rather than raw occurrence points or private rasters.

Recommended local and versioned layout:

```text
PlantWise_v0/
  regression_data/
    README.md
    golden/
      auc_and_contributions.csv
      smoke_test_manifest.json
      expected_summary.json
```

Suggested contents:

- `golden/auc_and_contributions.csv`
  A checked-in golden summary of AUC and variable contributions from a known-good run.
- `golden/smoke_test_manifest.json`
  The species subset, run parameters, and input hashes used for regression checks.
- `golden/expected_summary.json`
  Derived counts and tolerances such as number of processed species, missing outputs, and acceptable score drift.

The intention is that regression artifacts are safe to commit because they contain summaries and expectations, not the private raw datasets themselves.

## Current policy

If a contributor clones this repository, they should expect to seed the runtime and training datasets by hand in the paths above before using the app or model training pipeline.
