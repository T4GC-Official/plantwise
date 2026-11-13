# Starting prompt for the remote agent

Work in `/home/beeps/src/github.com/bprashanth/plantwise`, on branch
`staging/enmeval-nov-2026`. Read `staging/README.md` and
`staging/SOURCE_MAP.md` first. This is a clone of T4GC-Official/plantwise with
an isolated, uncommitted `staging/` import containing the required code and
private local data. Do not replace the existing root src/ implementation.

Build a complete localhost staging version of the original PlantWise site,
using ENMeval-tuned Java Maxent with effort-weighted background ONLY. No
ensemble or three-model switch is required. The November ensemble R script
is reference-only, not the executable model. Keep the original React/Leaflet
look and feel and preserve the production north/south occurrence bound
filter, plus server-side WG membership, input validation and NoData rejection.

Proceed in checkpointed stages:
1. Inspect provenance/checksums and install an isolated native ARM64 R/Java
   environment. Fix the listed runner issues with minimal changes. Record
   actual package versions, jar identity and predictor filename mapping.
2. PASS 1: train Aglaia_lawii with bias background and block CV; save a final
   full-data model, GeoTIFF, preview and metrics. Bring up the original-looking
   frontend + real backend using this one-species release on loopback 8175 if
   free. Verify in browser and API tests: map/manual queries, score/threshold,
   latitude bounds, WG rejection, NoData, preview and no production API calls.
   Base safety behavior on staging/reference/production-api/app.py, not root
   legacy Flask. Save evidence of a working site BEFORE any full training.
   No mandatory synthetic-data or ten-species gate; the ten reference species
   are optional diagnostics. Do not require identical historical AUC scores.
3. PASS 2, only after the one-species site passes: build resumable jobs across
   exactly the 448-species input. Tune/evaluate
   with block CV, then save the chosen model fitted on all valid occurrences
   for serving. Report sparse-data exclusions and all failures honestly; do
   not fill them with old-model maps or silently switch to uniform background.
4. Publish the validated full release in the SAME website/API already tested
   in pass 1, retaining that one-species release for rollback.
   Never require an old baseline AUC row to return a valid new-model species.
5. Serve the built frontend and /api on one endpoint, preferably loopback
   port 8175 if still free. Test map clicks, manual coordinates, species maps,
   latitude bounds, NoData, restart/rollback and no production API requests.
   Leave cloudflared and other existing services unchanged; the user will
   point plantwise.idli.cc to it. Do not claim the domain is live until tested.

No deletion of files or results, no rsync --delete, no production deployments,
no git push, and no private data or outputs in Git. Do not install packages
globally if it would affect other services. Use Docker or a dedicated R user
library. Use modest CPU/RAM concurrency on this shared 20-core ARM64 host.
Commit reviewable code checkpoints locally and write progress, commands,
metrics, paths and recovery instructions into staging/docs/. Read-only
historical inputs must not be overwritten. The user authorizes implementation,
one-species training/serving, subsequent full training, and localhost serving
in this follow-on task. Use ONLY BIO1..19, the supplied WG polygon and bias
background, and the 448-species filtered_species_output.csv. Do not include
BIO20 or the 66 additional species from the original Final_Species.csv.
Read README's documented baseline differences before claiming reproduction.
No need to revisit ensemble design or build a generalized platform.
