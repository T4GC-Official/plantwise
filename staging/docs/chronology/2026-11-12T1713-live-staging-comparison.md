# Read-only live/staging recommendation comparison

Read the supplied archived notes/prompt and the extracted deployed container
code. Confirmed active staging full_20261111T1252Z with268 successes,180
exclusions, zero failures. Did not execute archived training/cleanup scripts.

Captured real browser requests at full-precision user coordinates and slider50:
live9 /staging23. Direct numeric POSTs reproduce both. Exact-ID overlap is five,
with four live-only and eighteen staging-only. An initial conversational tally
was miscounted and corrected against set operations before reporting results.

Diagnostic threshold0 queries: live264 /staging231. All eighteen staging-only
species appear live below50. Three live-only species lack staging fits due to
five/seven/six usable cells; a fourth has a valid staging score below50. Every
union species is within the same original-observation latitude envelope and
has archived TIFF/AUC coverage. WG membership and valid predictor/map pixels
pass. Source differences in metadata gates or the66 extra source species do
not explain this union's list discrepancy.

Live264 IDs exactly match historical TIFF+AUC+latitude eligibility. The
container's north/south filter and staging's equivalent check are both present;
the older Flask implementation is not the correct comparator. Live metadata
matches the archived AUC rows, but current live source/model provenance is not
assumed cryptographically identical to the snapshot.

Verified shared input hashes and archive checksum manifest. Reloaded24 saved
staging models for inference only in a separate network-isolated container,
with staging mounted read-only; explicit cloglog samples match their maps.
Found one zero-coefficient constant map and five low-block-AUC recommendations
in the23; recorded as quality limitations without changing filtering.

Recorded the supplied jar's CLoglog default and variable-importance meaning of
jackknife; avoided assuming a Logistic legacy scale or LOOCV. Patched local
trainer settings are not proof of every original deployed map. Requested exact
selective production TIFFs/provenance through a manifest for deeper attribution.

Private raw responses, full CSVs, report and screenshots remain under ignored
runtime/comparison-20261112-kodagu/. Reproducible analysis scripts and a concise
operational summary are recorded in the repository. Active service PID/start,
release, filters and all scientific artifacts remain unchanged. No retraining,
deletions, cloudflared changes, deployments or push.
