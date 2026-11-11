# models/enmeval — ENMeval-tuned Maxent + bias layer (v1)

The developer's "sdm code for 10 species.R" (original: `docs/refs/enmeval-developer-README.md`),
made runnable: CLI flags, species loop, one point per grid cell before the
split, and the `bias_sites` input it was missing. Same `maxent.jar` as
production; fits fc {L, LQ} × rm {1, 2} per species and keeps the AICc-best.

```bash
Rscript models/enmeval/build_bias_layer.R    # -> data/derived/bias_layer (effort map, biasBg.csv, randomBg.csv), 36 s
Rscript models/enmeval/make_blocks.R         # -> data/derived/blocks (4 spatial folds per species, shared by all models)
Rscript "models/enmeval/sdm code for 10 species.R" --species=Hopea_ponga --seed=1 \
   --partitions=testing --bg_csv=data/derived/bias_layer/biasBg.csv --output_dir=runs/enmeval/adhoc
```

Flags: `--partitions=block|randomkfold|testing`, `--test_frac`, `--fc=L,LQ,H`,
`--rm=1,2,3`, `--bg_csv`, `--seed`, `--write_maps=1`, `--metrics_name`.
Defaults resolve to `data/`. The bias layer is a *background policy*: it is
where the 10,000 "not-here" points are drawn from, never a predictor.
