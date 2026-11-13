# Visual parity and preview request correction

User supplied a mobile screenshot showing extra release/method paragraphs and
an `Unexpected end of JSON input` error. They requested the original site's
appearance with nothing extra, and human screenshot verification.

Fetched https://plantwise-india.org/ and its deployed source map read-only.
Captured desktop/mobile Home, About, Model and Tool pages in Playwright, then
inspected rendered screenshots. Earlier local testing did not compare against
the deployed original; the added diagnostic paragraphs shifted mobile inputs
by roughly 200px. Removed those paragraphs and the added AUC result column.
Restored original three-column results and integer percentage display. Detailed
model identity, coverage and evaluation remain in API metadata and repo docs.
The Model page retains its original structure with accurate input counts.

The user's exact coordinates (17.519216206515345, 73.60814321375223), threshold50,
return HTTP200 and 20 recommendations directly. No recommendation POST reached
our backend during the user's screenshot session; initial assets and health GETs
did. The full preview address was requested because the screenshot truncates it.
We have not verified that unknown external URL or changed cloudflared/DNS.

An empty HTTP405 rejecting POST at a simulated read-only preview forwarder
reproduced the exact JSON exception. Added a validated, read-only GET form of
/api/get-results, retaining POST compatibility and identical WG/latitude/NoData
checks. The frontend now uses GET and handles empty/non-JSON responses safely.
An actual request error no longer also shows a misleading no-results message.
This confirms the failure mode; the external forwarding diagnosis remains an
inference until its full URL is provided.

Built a fresh immutable frontend snapshot and restarted only our staging service.
The 268-model release and all training artifacts remain unchanged. New snapshot:
runtime/frontend-20261111T154907Z. Previous frontend snapshots remain available.

Verification: 26 API cases pass. Playwright at 1440x1050 and 390x844 verified the
exact screenshot coordinates (20 results), GET-only forwarding, three result
columns, previews, map click, navigation and friendly handling of empty errors.
The general browser regression also passes with no production API fallback,
JS exceptions or missing local assets. Waited for image/boundary loading and
inspected final screenshots. Desktop controls/footer pixels (x708..1439) are
identical to production; latitude field bounds match exactly at both viewports.
Basemap tiles are external OSM content and can vary between captures.

Private screenshot/network evidence: runtime/visual-parity-20261111/. No model
retraining, input changes, existing-service changes, deletions or pushes.
