# Training input inventory

These inputs are private/manual assets, deliberately omitted from Git. A fresh
clone contains this inventory rather than placeholder observations or rasters.
Populate the paths below before training; no automatic downloads are implied.
All paths below are relative to staging/model/data/.

| Path | Required content and purpose |
|---|---|
| occurrences/filtered_species_output.csv | 14,180 rows, 448 species; columns Species,Latitude,Longitude in WGS84 degrees. Original selected observation rows, including multiplicities. |
| attributes/wc2.1_30s_bio_1_fc.tif through wc2.1_30s_bio_19_fc.tif | Exactly BIO1-19 WorldClim predictors, EPSG:4326, aligned30-arc-second cells (roughly0.9km per side in WG). No BIO20. |
| boundary/wg_boundary.shp, .shx, .dbf, .prj | WG polygon with required sidecars; used for training/prediction masking. |
| derived/bias_layer/biasBg.csv | Supplied10,000 effort-weighted background coordinates, Longitude and Latitude columns. Required by the production runner. |
| derived/bias_layer/biasMap.tif, randomBg.csv and metrics | Background-generation audit/reference artifacts; not extra climate predictors. |
| reference/Master_Metrics_10_Species.csv | Historical smoke-target metrics, not observations or training predictors. |

The Java binary is separately required at ../maxent/maxent.jar (Maxent3.4.4,
SHA2564c856e55412f70c5597b03cf9aaaf27e0782e0921f937262273b68bdcb8fee5e).
Selected occurrence CSV SHA256:
4521b609bb04ec781e33455c57b34768c3ca46559ac6fe6e8c465918930cac6c.
Historical source provenance is preserved in
[the source map](../../archive/handoff/SOURCE_MAP.md); its paths describe the
original import, before this layout migration. Full per-run hashes stay in
private config/provenance files. The v0 shared input hashes remain in the
local archive/plantwise_v0/SOURCE_PROVENANCE.json at repository root.

Training validates finite coordinates, WG membership and all19 predictor values,
then keeps one occurrence per climate cell. At least8 distinct usable cells
are required, independent of raw observation count; repeated records do not
increase spatial coverage. The source has514 original species; the additional
66 are outside this448-species training contract.

Do not commit private CSVs, geometry, raster layers, derived background, models,
GeoTIFF predictions or run outputs. The scoped staging/.gitignore covers them.
