# PlantWise staging frontend

Original React 18 / Bootstrap / Leaflet visual identity. Same-origin `/api` only.
Build with Node 22 using npm ci then npm run build; serve the result through
staging/backend. Do not deploy a public development server.

The ignored public/wgg.geojsonl.json is the supplied WG map asset. The backend
uses the release's independently exported exact supplied shapefile geometry.
No occurrence CSV or raster directories are public. The original layout and result columns are preserved. Release identity, coverage
and block-CV evaluation remain in API metadata and operational docs. Read-only
GET recommendations work through GET-only preview forwarders; POST remains
available for compatibility.

See ../docs/runbook.md and ../tests/browser.spec.cjs for build and validation.
Obsolete scaffold tests and commented implementations are kept in ../archive/.
