# ENMeval Java Maxent

[train.R](train.R) is the current single-species production runner. It reads
model/data, filters/deduplicates observations, enforces the8-cell/four-block
gate, tunes FC L/LQ and RM1/2, selects by eligible AICc, and writes the selected
full-data model plus explicit cloglog predictions and metrics.

The orchestrator mounts staging/model at /work and invokes enmeval/train.R.
Use [../README.md](../README.md) for commands and [../data/README.md](../data/README.md)
for required inputs. build_bias_layer.R and make_blocks.R are optional helper
scripts with model-relative defaults. Their seeds/settings are not silently
substituted for the supplied background used in published releases.
The earlier ten-species experimental runner is preserved in staging/archive/.
