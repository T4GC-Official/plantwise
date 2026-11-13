# Original appearance and preview query correction — 2026-11-11

The frontend now uses the original Tool page layout, with no added release,
ENMeval protocol, suitability explanation or AUC column. Results retain the
original three columns and integer display. Score filtering still uses full
precision. Model provenance/coverage/evaluation remain available through API
metadata and operational documentation. Model page paragraph structure follows
the original; current input counts replace historical counts.

The screenshot coordinates 17.519216206515345 / 73.60814321375223 at threshold50
return **20 results**, verified by clicking Enter in desktop and mobile Chromium.
Previews and actual Leaflet map queries work. Screenshots were inspected against
https://plantwise-india.org/ after waiting for images and WG geometry to load.
Desktop controls/footer pixels are identical; coordinate-input bounds match at
1440x1050 and 390x844. External OSM tiles may vary.

An empty response rejecting POST reproduces the supplied JSON exception. The
frontend now calls the read-only GET endpoint, which works through GET-only
preview forwarders; POST is retained for compatibility. Both use the same
validation, WG membership, latitude and raster sampling code. Empty/non-JSON
responses produce a friendly error rather than a JSON parsing exception or a
false no-results message. The user's complete external preview URL is still
needed to verify that exact route; only its truncated address was supplied.
No cloudflared or DNS configuration was changed.

```bash
staging/.venv/bin/python -m pytest staging/serving/tests -q
curl -fsS 'http://127.0.0.1:8175/api/get-results?latitude=17.519216206515345&longitude=73.60814321375223&minProbability=50'
docker run --name plantwise-parity-UNIQUE --network host --cpus 2 --memory 2g -v "$PWD/staging:/work" -v "$PWD/staging/runtime/browser:/browser" -w /work mcr.microsoft.com/playwright:v1.61.0-noble node tests/visual-parity.cjs
```

26 API cases pass, including GET/POST equivalence and invalid GET inputs. The
visual regression fetches the original reference read-only, captures both
viewports, rejects added UI and exercises screenshot coordinates, preview,
map interaction and empty-response handling. The existing full browser test
also passes. Evidence stays ignored under runtime/visual-parity-20261111/:

- reference-desktop-settled-tool.png / verified-desktop-settled-tool.png
- reference-mobile-settled-tool.png / verified-mobile-settled-tool.png
- verified-mobile-results-visible.png
- after-verification.json / settled-captures.json
- forwarder-reproduction.json / reproduced-empty-post.png

Current frontend snapshot: runtime/frontend-20261111T154907Z, resolved through
runtime/frontend-active. The full_20261111T1252Z model release is unchanged.
