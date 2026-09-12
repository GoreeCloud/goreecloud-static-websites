# GoreeCloud Design Center — GLAZE UI V1.3

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

- Current Official Stable consumer target: **GLAZE UI V1.3 / `1.3.0`**
- Exact reviewed Glaze source revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Canonical Glaze repository: `GoreeCloud/goreecloud-glaze-ui`
- Design Center consumer presentation layer: `v1.3-site.css`
- Current consumer state: **source migrated; rendered/browser, accessibility, performance, rollback, Cloudflare cutover, exact deployed-revision, and production acceptance remain separate gates**

The Design Center uses repository-local publication derivatives and consumer layers while identifying the exact canonical Stable source revision. A successful source build or Cloudflare provider deployment must never be treated as proof of downstream rendered or production acceptance.

## Build and validation

From `sites/design/website`:

```bash
python3 validate.py
python3 browser_artifact_smoke.py
python3 browser_header_smoke.py
node --check site.js
```

`validate.py` rebuilds `dist/`, verifies the exact V1.3 source anchors, synchronized Facet identity, required artifact closure, accessibility/adaptation markers, security-header source contract, and fail-closed consumer-state language.

Repository CI additionally exercises the built `dist/` artifact in real Chrome at 1180, 768, 390, and 320 CSS pixels and verifies the full canonical `GoreeCloud · Design Center · GLAZE UI` identity at 1440 pixels without clipping or overlap.

## Canonical production acceptance

Canonical production verification remains manual until the external Cloudflare Pages source cutover has been independently performed and verified. After that provider-side source change, rebuild the reviewed artifact and run:

```bash
python3 validate.py
python3 verify_remote.py --target production
python3 browser_remote_smoke.py
python3 browser_header_remote_smoke.py
```

`verify_remote.py` accepts only the canonical Design Center host and the verified `goreecloud-design.pages.dev` namespace. For production it compares every fetchable `dist/` artifact byte-for-byte with the canonical live deployment, requires the reviewed security headers and true HTTP 404 behavior, and checks the current V1.3/fail-closed consumer markers.

`browser_remote_smoke.py` reruns the production-responsive and appearance-control checks at 1180, 768, 390, and 320 CSS pixels. `browser_header_remote_smoke.py` separately requires the live 1440-pixel header to show the complete canonical Design Center identity without ellipsis, clipping, document overflow, brand/navigation collision, or navigation/appearance-control collision.

The dedicated GitHub workflow exposes those canonical-host checks only on `workflow_dispatch`; pull-request and push validation cannot silently become production acceptance.

## Production boundary

The central package is not production-authoritative merely because it is build-valid. Keep the migration registry fail-closed until Cloudflare Pages is verified to use `GoreeCloud/goreecloud-static-websites`, branch `main`, the Design Center site root/build contract, and the canonical domain passes exact deployed-content, responsive browser, and wide-header acceptance.
