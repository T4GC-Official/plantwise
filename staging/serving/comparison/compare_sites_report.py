"""Render the evidence-backed comparison report outside Git."""
import json
import os
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get('PLANTWISE_COMPARISON_DIR',ROOT/'runtime/comparison-20261112-kodagu'))
s=json.loads((OUT/'summary.json').read_text());rows=pd.read_csv(OUT/'response-union-comparison.csv').set_index('species')
live=json.loads((OUT/'live-threshold-50.json').read_text());stage=json.loads((OUT/'staging-threshold-50.json').read_text())
checks=json.loads((OUT/'model-inference-verification.json').read_text())
lines=['# Live/staging comparison at the requested point','',
'## Reproduced requests','',
f"Latitude **{s['coordinate']['latitude']}**, longitude **{s['coordinate']['longitude']}**, threshold **50%**. Captured {s['captured_at']}.",
'Both browsers used the original default slider setting of 50, the full input strings, and no preview/debug query mode. Live sent a JSON POST with coordinate strings; staging sent GET query parameters. Direct numeric JSON POSTs to both endpoints reproduced their browser responses exactly. Request/response bodies, headers and screenshots are retained in this directory.',
'',
'| Setting | Live | Staging |','|---|---|---|',
'| Frontend | https://plantwise-india.org/#/tool | http://100.82.28.38:8175/#/tool |',
'| Actual API | https://species-api-452165326340.asia-south1.run.app/api/get-results | http://100.82.28.38:8175/api/get-results |',
f"| Threshold50 count | {s['live_count_50']} | {s['staging_count_50']} |",
f"| Diagnostic threshold0 count | {s['live_count_0']} | {s['staging_count_0']} |",
f"| Active release | Not exposed by the live API | {s['release']} |",'',
f"Exact-ID overlap: **{len(s['shared'])} shared**, **{len(s['live_only'])} live-only**, **{len(s['staging_only'])} staging-only**, union27. Shared IDs: {', '.join(s['shared'])}. No inferred taxonomic aliases were used. Glochidion_ellipticum and Glochidion_heyneanum are different IDs, not an alias.",
'',
'## Species-by-species outcome','',
'Every row below belongs to the selected448 input, has a historical production TIFF and archived AUC row, and is within its original-observation latitude envelope at this point. The point is inside WG. Every available staging raster has a valid cell here. Full bounds, input counts, raster indices, metadata presence and per-side status are in response-union-comparison.csv. Live percentages below are the **reported integers from threshold0**, not invented unrounded pixel scores. A staging score below50 is shown even when its species is not returned at50.','',
'| Species | Live reported % | Staging actual % | Explanation at threshold50 |',
'|---|---:|---:|---|']
order=[x['species'] for x in live]+[x['species'] for x in stage if x['species'] not in {a['species'] for a in live}]
for sp in order:
 r=rows.loc[sp]
 if r.staging_status=='excluded':score=f"excluded ({int(r.usable_cells)} cells)";reason='Live-only: no staging model; fewer than8 usable cells'
 else:
  score=f'{r.staging_percent:.4f}'
  reason=('Both returned; fitted scores/rank differ' if r.live_returned_50 and r.staging_returned_50 else
          'Live-only: staging score below50' if r.live_returned_50 else
          'Staging-only: live score below50, confirmed by threshold0')
 lines.append(f'| {sp} | {int(r.live_reported_integer_percent_at_0)} | {score} | {reason} |')
lines+=['',
'**The count identity is 9 live − 3 staging exclusions − 1 downward threshold crossing + 18 upward threshold crossings = 23 staging.** Three live-only exclusions are Ficus_talbotii (five raw/usable cells), Symplocos_cochinchinensis (six raw/usable cells), and Glochidion_heyneanum (nine raw records, seven inside WG/complete cells). The latter loses two rows at the training WG-membership stage; old TIFF training sample counts remain unknown. Clausena_anisata is successfully fitted and valid but scores44.2094%, versus54 reported by live. None of these four is absent because of its serving latitude envelope.',
'',
'## Coverage and serving gates','',
'Current staging health and accounting remain268 success /180 excluded /0 failed. This is not448 served models. All original selected observation rows, BIO1–19 files, WG core files, frontend WG asset and jar match the supplied archive provenance hashes. SOURCE_SHA256SUMS also verifies the archived source snapshot.',
'',
'| Staging disposition of all448 species at this query | Count |','|---|---:|',
'| Excluded for1–7 usable cells; no fitted map |174|',
'| Excluded for zero usable cells; no fitted map |6|',
'| Fitted, but outside original-observation latitude envelope |37|',
'| Fitted, inside envelope, valid cell, below50 |208|',
'| Returned |23|','',
'All268 active staging rasters have finite valid0–1 cells at the query. The37 latitude-rejected species also happen to have scores below50 here; latitude remains a real independent gate, not a bypass. Threshold0 returns231 =268−37. All180 exclusions are listed in all-180-exclusions-at-query.csv, including species returned by neither site at50.',
'',
'Examples absent from both lists at50: Cinnamomum_sulphuratum has six usable cells and live reports46 at threshold0; Mitrephora_grandiflora has seven cells and live reports42. Their staging absence is **no model**, not a low staging probability. Thirty-four species in the live threshold0 list are excluded from the staging release.',
'',
'### Latitude/longitude: the deployed container is the right reference','',
'The provided container/app.py applies inclusive per-species minimum/maximum **latitude** checks. Current staging/backend/app.py does too, using the same selected original observations. Neither code has a per-species longitude envelope; longitude participates in raster sampling/bounds, and staging additionally enforces the exact WG polygon server-side. The older archived Flask backend lacks this north/south gate and is not the production reference.',
'',
'The historical production inventory has368 TIFFs,340 with an AUC row. Applying latitude envelopes to those340 predicts264 IDs at this point; the current live threshold0 response matches that exact set. All nine live AUC values also match the archived container metadata. The live OpenAPI route/schema shape agrees with the archived FastAPI app. This is strong consistency evidence, not a deployed-source hash or proof that every implementation detail is unchanged. All27 union species pass latitude bounds, so a missing staging latitude filter does **not** explain the9-versus23 discrepancy.',
'',
'### WG, NoData, metadata, rounding and thresholds','',
'- Query membership is confirmed inside the supplied WG polygon. All19 climate values are valid. No staging cell in the27-species union is NoData; the three excluded species have no staging raster to sample. All18 staging-only species return live at threshold0, so they are not being lost to live NoData, missing files or missing metadata at this point.',
'- The archived container has no explicit server-side WG-membership test, masked/finite/range check, or CRS transformation. It reads raw TIFF values and bounds. The ASC-to-TIFF converter in the archived local trainer also does not write the parsed NoData header into raster metadata. These are source-level robustness differences, not demonstrated causes at this valid point.',
'- Archived live logic requires an AUC **row**, not AUC≥0.5. The nine live results actually include four AUC values below0.5. Staging has no historical AUC-row gate. Nevertheless, all27 union species have archived AUC rows, so this policy difference does not explain their50% list differences.',
'- Donella_lanceolata is a separate metadata-gating example: staging returns it at0 with25.7954%; its historical TIFF exists but the archived AUC row is absent, and live does not return it at0. This is consistent with the archived metadata gate, but does not cause a50% difference because the staging score is also below50.',
'- Both archived predicates and staging use probability≥minProbability/100. UI default50 is confirmed. Live exposes integer percentages; staging exposes full precision and truncates only its display. Numeric POST reproductions match browser lists, so precision handling, GET versus POST, and UI rounding do not account for the membership difference. Exact unrounded original pixels are not exposed and were not fabricated. The archived API sorts truncated percentages, so relative order within reported ties can depend on worker completion; staging sorts full-precision scores.',
'- The66 extra original-source species are excluded by design, but none of the27 response-union species is among them. None of the current live threshold0 IDs is outside the selected448 either. That source-superset difference does not explain this query.',
'',
'## Training and prediction comparison','',
'Only the staging training configuration is fully evidenced by its run/model artifacts. The archived InitialImplementation.py is a patched local direct-Java trainer. Its active command and jar defaults describe that source; they do not establish how every original deployed TIFF was produced. container/app.py is serving code, not a trainer.',
'',
'| Aspect | Archived local direct-Java runner / supplied historical material | Verified staging |',
'|---|---|---|',
'| Input source | Splitter reads514-species Final_Species.csv; historical production maps cover368 selected species | Exact448-species /14,180-row selected CSV |',
'| Predictors | Reads final_attributes directory; historical report includes BIO20 | Numeric BIO1–19 only |',
'| Extra BIO20 evidence | Nonzero contribution in25 of27 union rows in archived report; actual matching raster-run provenance still needed | Not present or used |',
'| Background | No explicit bias/background file in active command; supplied jar defaults cap random background at10,000 valid cells | Fixed10,000 supplied effort-weighted background coordinates, all valid after WG/all-predictor checks |',
'| Occurrences | Active wrapper accepts raw presence count>2; jar default removes within-cell duplicates / invalid environmental records | Explicit finite/geographic/WG/complete-case filtering and unique-cell counts; require≥8 unique cells and≥2 per four blocks |',
'| Geographic mask | No explicit polygon-mask step in active Python command; reads already supplied raster folder | Explicit WG crop/mask before fitting and mapping |',
'| Features | No override; supplied jar default autofeature=true | L and LQ tuning only; automatic feature selection disabled by ENMeval |',
'| Regularization | No override; supplied jar default multiplier1 | Tune1 and2; select finite eligible AICc, deterministic ties |',
'| Evaluation | randomtestpoints=30 in active command; jackknife flag is variable-importance jackknife, NOT leave-one-out CV | Four spatial blocks, held-out mean/SD, full supplied validation background |',
'| Served fit | If this command produced a map, it is a random holdout workflow; exact original full-data/refit policy unverified | Selected single model contains all usable occurrences; not fold averaging or an ensemble |',
'| Seeds | No explicit seed in command; supplied jar randomseed default false | R set.seed(123), fixed background; Java randomseed not explicitly overridden |',
'| Jar/software | Local omitted jar matches supplied SHA; historical map runtime version not independently proven | Loaded Java class path/hash verified; Maxent3.4.4 /ENMeval2.0.5.2 /predicts0.2.2 |',
'| Link/output | Command has no outputformat override; supplied jar resource default is CLoglog, not Logistic | Explicit outputformat=cloglog for map and model inference |',
'| Clamping | Supplied jar default doClamp=true; actual original settings unverified | ENMeval clamping workflow and final Java prediction defaults; stored models verified |',
'',
'BIO1–19 being identical does not imply identical fitted maps: background distribution, predictor20, occurrence treatment, feature/regularization choice, selection criterion, and full-data fit all can affect predictions. WG masking can affect the fitting/background domain even when the query itself is valid. We cannot apportion those effects without exact original model provenance and controlled comparisons; no ablation or retraining was performed.',
'',
'Changing only the **reported AUC metric** does not change a fixed TIFF score. But holdout versus full-data fitting and choosing settings by AICc can change the fitted map. AUC numbers from random holdout and spatial blocks with different backgrounds are not the same evaluation. There is no numeric AUC quality cutoff in either serving implementation examined.',
'',
'### Saved-model score verification and weak-model caveat','',
f"All {len(checks['model_checks'])} available staging models in the union were reloaded in a fresh isolated JVM, with no fitting. Explicit cloglog predictions at the exact query-cell center equal their GeoTIFF samples with maximum error {max(v['absolute_error'] for v in checks['model_checks'].values())}. Staging API percentages also match direct raster samples. This confirms staging scores come directly from its saved models/maps without serving-side normalization or a stale preview. Exact correspondence between original TIFF samples and live integer output remains unverified until those TIFFs are available.",
'',
'Chrysophyllum_flexuosum is an important counterexample to “more recommendations means better”: selected ncoef=0; its entire valid map is constant0.632120549678802, and its block-CV AUC is0.335738... (exact metrics in CSV). It passes50 because of that constant cloglog output, not a site-specific signal. Offline logistic prediction of the same fit is0.5. Five of the23 returned staging models have block AUC<0.5. No filtering or model selection was changed during this investigation.',
'',
'The supplied3.4.4 jar itself defaults to CLoglog. Therefore an assertion that the old maps must be Logistic and the new maps Cloglog is **not established**. Matching old HTML/lambdas/settings or other provenance is needed to identify the actual old scale. Scores alone cannot identify it.',
'',
'## Ranked explanation and unresolved questions','',
'**Established:** (1) three live recommendations have no staging model because of explicit data eligibility exclusions; (2) one fitted staging species falls below50 while18 other fitted species cross above50 relative to current live output; (3) both sites use identical numeric coordinates and requested cutoff; (4) latitude/WG/NoData/AUC-row differences do not explain those27 membership outcomes; (5) original metadata coverage and latitude gating are strongly consistent with current live behavior.',
'',
'**Plausible contributors to changed fitted scores, not isolated causes:** effort-weighted versus default background, BIO20, feature/regularization selection, filtered/deduplicated/full-data training and training-domain masking. Legacy output scale and exact runtime/configuration are unresolved; do not assume Logistic, a fixed seed, or a particular historical fit solely from the local patched command.',
'',
'**Unresolved:** exact original pixels/transforms/NoData metadata, prediction scale/clamping, exact original map-training commands, background, jar/software versions and any per-species refitting. A single coordinate is not an ecological quality assessment.',
'',
'## Selective transfer, if pursuing exact original-map attribution','',
'Initial useful production TIFFs (not March reruns):','',
'```text',
'container/tif_data_final/Drypetes_venusta.tif',
'container/tif_data_final/Alseodaphne_semecarpifolia.tif',
'container/tif_data_final/Croton_zeylanicus.tif',
'container/tif_data_final/Clausena_anisata.tif',
'```','',
'These cover a large upward change (12→57.35), another large upward change (27→62.72), a near-cutoff crossing (49→66.89), and the reverse crossing (54→44.21). selective-transfer-manifest.json lists these four, the remaining20 original TIFFs for all24 paired fitted models, and three optional old maps for excluded species. Original TIFFs are not required to establish the observed threshold/exclusion explanation; they are needed to verify exact original pixel/geometry/metadata and pursue deeper attribution.',
'',
'If available, transfer the matching production-generated HTML, lambdas, maxentResults/logs and saved settings for those four, with evidence linking them to the TIFFs. Do not substitute arbitrary current res/ files or March reruns. TIFFs alone cannot prove their exact training settings. No duplicate BIO1–19, occurrences, WG polygon or jar is needed.',
'',
'## Reproduction and evidence','',
'1. Run scripts/compare_sites_browser.cjs in the existing Playwright container setup; capture the real network and displayed lists first.',
'2. Run scripts/compare_sites_capture.py for identical numeric JSON POST requests at50 and diagnostic0, then scripts/compare_sites_analyze.py.',
'3. Run scripts/compare_sites_model_predictions.R in a fresh network-isolated inference container with staging mounted read-only and this evidence directory mounted at/evidence.',
'4. Run scripts/compare_sites_report.py to render this report. Set PLANTWISE_COMPARISON_DIR to a fresh evidence directory for a new capture; prior captured evidence should be retained.',
'',
'Key files: *-browser-http.json, *-browser-response-body.json, *-results-desktop.png, *-threshold-{0,50}-http.json, *-threshold-{0,50}.json, response-union-comparison.csv, all-species-diagnostics.csv, all-180-exclusions-at-query.csv, summary.json, model-inference-verification.json, maxent-3.4.4-parameters.csv, archive-integrity.log, service-identity.txt and selective-transfer-manifest.json.',
'',
'Services, filters, thresholds, active release and archived files were not changed. No training, deletion or push was performed.']
# Use the exact stored CV metric in the narrative.
metric=rows.loc['Chrysophyllum_flexuosum','block_cv_auc']
text='\n'.join(lines).replace('0.335738... (exact metrics in CSV)',f'{metric:.12f} (exact metrics in CSV)')+'\n'
(OUT/'findings.md').write_text(text)
print(OUT/'findings.md')
