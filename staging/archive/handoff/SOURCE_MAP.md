# Sources and transfer contract (2026-11-11)

All source paths below are relative to the laptop workspace
`/home/desinotorious/src/github.com/bprashanth/plantwise`.
Remote checkout: `/home/beeps/src/github.com/bprashanth/plantwise`.
The imported tree is under `staging/` to avoid changing official repo paths.

| Remote staging path | Laptop source | Purpose |
|---|---|---|
| models/enmeval/ | PlantWise_v2/models/enmeval/ | v1 ENMeval/bias code with consolidated default paths |
| models/maxent/maxent.jar | PlantWise_v1/model/maxent.jar | Java model binary, inspect version at bootstrap |
| data/occurrences/filtered_species_output.csv | PlantWise_v1/model/filtered_species_output.csv | 14,180 observations, 448 species |
| data/reference/Master_Metrics_10_Species.csv | PlantWise_v1/model/Master_Metrics_10_Species.csv | Ten explicit smoke species and historical metric reference |
| data/boundary/ | PlantWise_v1/model/wg boundary file/ | WG shapefile and sidecars, not climate predictors |
| data/attributes/ | PlantWise_v2/data/attributes/wc2.1_30s_bio_{1..19}_fc.tif | 19 WG-clipped WorldClim BIO rasters |
| data/derived/bias_layer/ | PlantWise_v2/data/derived/bias_layer/{biasMap.tif,biasBg.csv,randomBg.csv,biasModel.csv} | Previously generated effort surface/background and audit metrics |
| frontend/ | PlantWise_v2/src/frontend/ | Original PlantWise React UI with local API environment setting |
| frontend/public/wgg.geojsonl.json | PlantWise_v0/frontend/habitability-tool/public/wgg.geojsonl.json | Required existing frontend WG boundary asset |
| reference/production-api/ | PlantWise_v2/archive/container-2026-07/ small serving files | Production latitude-filter semantics; not a trainer |
| reference/v1/ | PlantWise_v1/model/{sdm code for 10 species.R,build_bias_layer.R} | Unmodified v1-era reference code |
| reference/nov_ensembel_plants.R | nov_ensembel_plants.R | Latest supplied November ensemble, reference only |
| docs/history/ | Selected PlantWise_v2/docs/chronology and ENMeval reference notes | Prior findings and known limitations |

The v1 occurrence CSV SHA256 is
`4521b609bb04ec781e33455c57b34768c3ca46559ac6fe6e8c465918930cac6c`.
It is byte-identical to the v2 occurrence copy. Core WG shapefile components
(.shp/.shx/.dbf/.prj) are also byte-identical between v1 and v2.

No generated bias layer was found under v1. The supplied generated files are
the September outputs of the v1-derived bias builder, retained in v2.
The current ENMeval runner only consumes Longitude/Latitude from biasBg.csv,
so mislabeled historical BIO columns in that file are not predictor inputs.
Keep the coordinates fixed for the first smoke test; document/rebuild the
bias model separately if changing the background policy or raster mask.

The v2 runnable ENMeval code differs from v1 mainly in default paths; it does
not change ENMeval into biomod2. Do not copy the old v1 relative defaults back
over it. The WG polygon, bias raster, and bioclim predictors have distinct
roles and cannot substitute for one another.

## Verified differences from the originally shared bprashanth baseline

- Compared against the independent PlantWise checkout, whose origin is
  git@github.com:bprashanth/plantwise.git, not only against v0's symlinks:
  all 19 selected BIO TIFFs are byte-identical. Original also contains BIO20;
  it is NOT transferred or selected for training.
- v1 .shp/.shx/.dbf/.prj match the original frontend's WG shapefile byte-for-byte.
  ENMeval explicitly uses that polygon to mask its predictors, which is a
  modelling-footprint policy to record in addition to TIFF identity.
- v1 input has 448 species/14,180 rows; original Final_Species.csv has 514
  species/15,335 rows. Every v1 row matches original rows for retained species
  numerically with duplicate multiplicities preserved. The extra 66 species
  are intentionally excluded; do NOT sync/use Final_Species.csv as a fallback.
- Production container occurrences match all v1 species and rows exactly.
  Baseline AUC report covers 392 species: 340 shared, 108 v1-only, 52 report-only.
  Production map inventory covers 368 species, all within v1. Do not confuse
  report/map coverage with the training input or silently filter to AUC rows.
- All ten historical smoke targets overlap v1 occurrences, original source,
  baseline AUC and production maps. Only Aglaia_lawii is required for pass 1;
  then verify its real website before proceeding to full training.
- ENMeval tuning/spatial CV and effort-weighted background differ from the
  original direct-Java workflow. The bias input is not a climate layer.

Not transferred: original production prediction TIFFs, July ensemble runs,
BIO20, global climate rasters, elevation, LULC, virtual environments, R
workspaces, node_modules, credentials, or other repos' .git directories.
No original-vs-new map selector is needed in this simplified scope.

`SYNC_SHA256SUMS` at remote checkout root records every imported regular file,
with paths relative to the checkout. It is an initial snapshot: edits by the
next agent will intentionally change those checksums. The clone's existing
tracked files are outside this checksum list and must remain intact.
