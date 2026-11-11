# Processing improvements

The imported scripts coupled data cleaning, tuning, plotting and publication,
used random-ten defaults and swallowed exceptions. The staging runner now
requires one named species and a fresh attempt directory, with terminal status
separate from artifacts. Remaining improvements worth evaluating:

- Materialize a versioned masked predictor stack and validated background once
  per input configuration; avoid repeating extraction/hash work for every job.
- Define ecological minimum-data criteria with domain review; the operational
  gate (>=8 unique cells, >=2 presences per spatial block, finite AICc with
  ncoef < n-1) is an explicit conservative starting policy, not a claim of
  ecological adequacy. Diagnose spatial concentration separately from low n.
- Separate immutable run manifests from execution events, and fit artifacts
  from release packaging. Publish only after full validation and accounting.
- Bias surface was derived using pooled observations. Quantify sensitivity and
  potential leakage before treating block CV as independent validation.
- Replace CRA in a separate reviewed change; do not combine a framework rewrite
  with model validation. Pin builds and inspect dependency security findings.
- Add independent ecological evaluation and data-drift checks before allowing
  automatic retraining/promotion on newly collected data.
