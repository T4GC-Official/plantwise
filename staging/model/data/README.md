# Training input inventory

These inputs are private/manual assets, deliberately omitted from Git. A fresh
clone contains this inventory rather than placeholder observations or rasters.
Populate the paths below before training; no automatic downloads are implied.
All paths below are relative to staging/model/data/.

| Path | Required content and purpose |
|---|---|
| occurrences/filtered_species_output.csv | 14,180 rows, 448 species; columns Species,Latitude,Longitude in WGS84 degrees. Original selected observation rows, including multiplicities. |
| attributes/wc2.1_30s_bio_1_fc.tif through wc2.1_30s_bio_19_fc.tif | Exactly BIO1-19 WorldClim predictors, EPSG:4326, aligned 30-arc-second cells (roughly 0.9 km per side in WG). No BIO20. |
| boundary/wg_boundary.shp, .shx, .dbf, .prj | WG polygon with required sidecars; used for training/prediction masking. |
| derived/bias_layer/biasBg.csv | Supplied 10,000 effort-weighted background coordinates, Longitude and Latitude columns. Required by the production runner. |
| derived/bias_layer/biasMap.tif, randomBg.csv and metrics | Background-generation audit/reference artifacts; not extra climate predictors. |
| reference/Master_Metrics_10_Species.csv | Historical smoke-target metrics, not observations or training predictors. |

The Java binary is separately required at ../maxent/maxent.jar (Maxent 3.4.4,
SHA256 4c856e55412f70c5597b03cf9aaaf27e0782e0921f937262273b68bdcb8fee5e).
Selected occurrence CSV SHA256:
4521b609bb04ec781e33455c57b34768c3ca46559ac6fe6e8c465918930cac6c.
Historical source provenance is preserved in
[the source map](../../archive/handoff/SOURCE_MAP.md); its paths describe the
original import, before this layout migration. Full per-run hashes stay in
private config/provenance files. The v0 shared input hashes remain in the
local archive/plantwise_v0/SOURCE_PROVENANCE.json at repository root.

Training validates finite coordinates, WG membership and all 19 predictor values,
then keeps one occurrence per climate cell. At least 8 distinct usable cells
are required, independent of raw observation count; repeated records do not
increase spatial coverage. The source has 514 original species; the additional
66 are outside this 448-species training contract.

Do not commit private CSVs, geometry, raster layers, derived background, models,
GeoTIFF predictions or run outputs. The scoped staging/.gitignore covers them.


## Serving assets

Serving a pre-trained model does not require the original BIO1-19 layers or a
running R/Java process. Restore the **complete** private release under
staging/model/releases/<release>/, preserving relative filenames and checksums:
catalog.json, accounting.json, boundary.geojson, checksums.json and each
species' model, prediction GeoTIFF and preview. Promote the release using
staging/serving/scripts/promote.py, then restart the managed service.

The frontend map requires the supplied private
staging/serving/frontend/public/wgg.geojsonl.json (WG features, one JSON feature
per line). Restore it before building the frontend. It is separate from the
training shapefile; a .shp cannot be substituted for this browser asset.

For /diff, also restore these local comparison inputs:

- staging/model/data/occurrences/filtered_species_output.csv
- archive/plantwise_v0/container/auc_and_contributions.csv
- archive/plantwise_v0/source_occurrence_inventory.csv

The archive CSVs are historical serving AUC metadata and species/map inventory,
not additional training observations or the legacy TIFF set. They are manually
provided in the private transfer bundle; the entire local archive is ignored.
Without them the original release API still serves, but /diff returns a clear
comparison-metadata error. Legacy TIFFs are not required: live scores are fetched
from the PlantWise India API. Current/archived runner sources for /model are
tracked and require no private source-file transfer.

See [serving services](../../serving/services/README.md) for frontend publication,
startup and readiness checks, and [the runbook](../../docs/runbook.md) for the
full train, validate, publish and rollback flow.
