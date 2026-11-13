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
Private observations, rasters, trained artifacts and runtime state are not tracked in git. 
To replicate this setup, you will have to bring your own data and Bioclim layers. 

