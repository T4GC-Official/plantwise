# PlantWise

The active ENMeval model and website are in [staging/](staging/README.md).

| Area | Location |
|---|---|
| Model training and releases | [staging/model/](staging/model/README.md) |
| Required private training inputs | [staging/model/data/](staging/model/data/README.md) |
| Website and API | [staging/serving/](staging/serving/README.md) |
| Operations and project history | [staging/docs/](staging/docs/README.md) |
| Superseded staging code and original handoff | [staging/archive/](staging/archive/README.md) |

The other root-level Python scripts, model/, backend/, frontend/, container/
and src/ belong to the earlier implementation. They are retained for reference;
they are not the active training or serving entry points. The previous root
README is preserved in [the handoff archive](staging/archive/handoff/BASELINE_README.md).
Private observations, rasters, trained artifacts and runtime state are not tracked
in Git. To replicate training, bring the selected observations and bioclim inputs
and place them at these paths (from the repository root):

```text
staging/model/
  data/occurrences/filtered_species_output.csv
  data/attributes/wc2.1_30s_bio_1_fc.tif ... wc2.1_30s_bio_19_fc.tif
  data/boundary/wg_boundary.shp + .shx + .dbf + .prj
  data/derived/bias_layer/biasBg.csv
  maxent/maxent.jar
```

The data contract is 448 species / 14,180 observation rows, aligned WorldClim
BIO1-19 rasters at 30-arc-second resolution, the WG polygon and supplied effort
background. Do not add BIO20 or the 66 extra original species. See the
[input inventory](staging/model/data/README.md) for formats, hashes and sources,
and [model setup](staging/model/README.md) for training/release commands.

To serve an existing trained model, restore its entire private release directory
to `staging/model/releases/<release>/`, select it with `promote.py`, and build and
publish the frontend. Serving predictions uses the release GeoTIFFs; it does not
need the original bioclim stack. The frontend map also needs the supplied
`staging/serving/frontend/public/wgg.geojsonl.json`. The optional live comparison
needs the original occurrence CSV and the two archived metadata CSVs listed in
[the inventory](staging/model/data/README.md#serving-assets).

The persistent service is managed from
[staging/serving/services/](staging/serving/services/README.md), following the
Pyrocene repository-unit pattern. It keeps port **8175** for the existing
Cloudflare origin `http://localhost:8175`. After the private assets, Python
environment and frontend snapshot are ready:

```bash
python3 staging/serving/services/manage.py install
python3 staging/serving/services/manage.py start
python3 staging/serving/services/manage.py status
```

Public site: https://plantwise.idli.cc/ (Cloudflare Access login required).
Direct local checks: http://127.0.0.1:8175/api/health and
http://100.82.28.38:8175/ on Tailscale. Cloudflare configuration is managed
separately; these commands manage only PlantWise.
