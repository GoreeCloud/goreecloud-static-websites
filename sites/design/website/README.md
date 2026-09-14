# GoreeCloud Design Center — GLAZE UI V1.4

Canonical centralized static source for `design.goreecloud.com`.

## Repository and publication contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/design/website`
- Build command: `python3 build.py`
- Build output directory: `dist`
- Production branch target: `main`
- Custom domain: `design.goreecloud.com`
- Cloudflare Pages project identity: `goreecloud-design`
- Pages namespace: `goreecloud-design.pages.dev`
- Legacy deployment/source repository: `GoreeCloud/goreecloud-glaze-ui`

The Cloudflare project identity and Pages namespace are verified from current legacy-repository deployment evidence. They do **not** establish a central-repository source cutover.

## Current Glaze UI authority

- Current Official Stable publication target: **GLAZE UI V1.4 / `1.4.0`**
- Exact reviewed Glaze source revision: `84cb3db4884042f0fa25ed6d475a127fb110f596`
- Exact Stable entrypoint: `glaze-v1.4.0.css`
- Exact entrypoint Git blob: `d48a9bc317090d152799769271de0fb4325494c4`
- Canonical Glaze repository: `GoreeCloud/goreecloud-glaze-ui`
- Consumer lock: `glaze.lock.json`
- Inherited Design Center consumer adaptation: `v1.3-site.css`
- Current consumer state: **build migrated; rendered/browser, accessibility, performance, rollback, Cloudflare cutover, exact deployed-revision, and production acceptance remain separate gates**

The checked-in Design Center HTML directly targets V1.4. `build.py` copies that reviewed source into the publication artifact, adds the exact pinned V1.4 Stable CSS dependency closure, preserves `v1.3-site.css` only as an inherited repository-local compatibility/adaptation layer, and keeps the approved Facet identity byte-for-byte. V1.4 is the active shared Glaze publication identity; the inherited stylesheet is not represented as the current shared Glaze release.

GLAZE UI V1.4 being Official Stable and consumer-eligible does not grant Design Center production conformance. A successful source build or Cloudflare provider deployment must never be treated as proof of downstream rendered or production acceptance.

## Build and validation

From `sites/design/website`:

```bash
python3 validate.py
python3 browser_artifact_smoke.py
python3 browser_header_smoke.py
node --check site.js
```

CI checks out the exact GLAZE UI V1.4 Stable revision and exposes it to the builder through `GLAZE_UI_SOURCE`. `validate.py` verifies the consumer lock, direct V1.4 source markers, exact V1.4 entrypoint and dependency closure, synchronized Facet identity, required artifact closure, inherited accessibility/adaptation markers, security-header source contract, and fail-closed consumer-state language.

Repository CI additionally exercises the exact built `dist/` artifact in real Chrome at 1180, 768, 390, and 320 CSS pixels and verifies the full canonical `GoreeCloud · Design Center · GLAZE UI` identity at 1440 pixels without clipping or overlap.

## Canonical production acceptance

Canonical production verification remains manual until the external Cloudflare Pages source cutover has been independently performed and verified. After that provider-side source change, rebuild the reviewed artifact and run:

```bash
python3 validate.py
python3 verify_remote.py --target production
python3 browser_remote_smoke.py
python3 browser_header_remote_smoke.py
```

`verify_remote.py` accepts only the canonical Design Center host and the verified `goreecloud-design.pages.dev` namespace. For production it compares every fetchable `dist/` artifact byte-for-byte with the canonical live deployment, requires the reviewed security headers and true HTTP 404 behavior, and checks the current V1.4/fail-closed consumer markers.

`browser_remote_smoke.py` reruns the production-responsive and appearance-control checks at 1180, 768, 390, and 320 CSS pixels. `browser_header_remote_smoke.py` separately requires the live 1440-pixel header to show the complete canonical Design Center identity without ellipsis, clipping, document overflow, brand/navigation collision, or navigation/appearance-control collision.

The dedicated GitHub workflow exposes canonical-host checks only on `workflow_dispatch`; pull-request and push validation cannot silently become production acceptance.

## Production boundary

The central package is not production-authoritative merely because it is build-valid. Keep the migration registry fail-closed until Cloudflare Pages is verified to use `GoreeCloud/goreecloud-static-websites`, branch `main`, root `sites/design/website`, build command `python3 build.py`, output `dist`, and the canonical domain passes exact deployed-content, responsive-browser, and wide-header acceptance.
