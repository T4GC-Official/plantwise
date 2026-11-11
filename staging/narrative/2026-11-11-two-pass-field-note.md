# From historical inputs to a staged PlantWise release

The starting point was an official checkout plus an uncommitted staging import.
Its data provenance was explicit, but its executable trainer was a scaffold.
We verified the import before edits and kept historical inputs read-only.

The two-pass structure makes the serving contract part of model validation:
a real Aglaia model must work through the original-looking website before the
448-species inventory can consume training resources. Spatial block metrics
are new evaluation results, not reproductions of historical random holdouts.

Environment work uses an ARM64 container for R/Java, an isolated Python venv,
and a Node container for the frontend. No other service is part of this work.
The runner records cleaning counts, partition sizes, tuning rows, final-data
fit size, explicit cloglog predictions and provenance. Releases carry species
latitude envelopes from original coordinate-valid observations and exact WG
geometry, so the API can enforce both independently of the map UI.

This is a working narrative. Training, browser evidence, full coverage and
publication results will be appended as they are actually established.
