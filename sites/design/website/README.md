# GoreeCloud Design Center — GLAZE UI V1.4

Canonical centralized static source for `design.goreecloud.com`.

## Repository and publication contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/design/website`
- Build command: `python3 build_v14.py`
- Build output directory: `dist`
- Production branch target: `main`
- Custom domain: `design.goreecloud.com`
- Cloudflare Pages project identity: `goreecloud-design`
- Pages namespace: `goreecloud-design.pages.dev`
- Legacy deployment/source repository: `GoreeCloud/goreecloud-glaze-ui`

The Cloudflare project identity and Pages namespace are verified from legacy-repository deployment evidence. They do **not** establish a central-repository source cutover or production acceptance.

## Current Glaze UI authority

- Current Official Stable publication target: **GLAZE UI V1.4 / `1.4.0` Stable**
- Exact canonical Glaze revision: `84cb3db4884042f0fa25ed6d475a127fb110f596`
- Exact Stable web entrypoint: `glaze-v1.4.0.css`
- Exact entrypoint Git blob: `d48a9bc317090d152799769271de0fb4325494c4`
- Canonical Glaze repository: `GoreeCloud/goreecloud-glaze-ui`
- Consumer lock: `glaze.lock.json`
- Current consumer state: **build migrated; rendered/browser source acceptance is validated independently; Cloudflare cutover, exact deployed-revision verification, rollback, and production acceptance remain separate gates**

The reviewed Design Center source still retains the **GLAZE UI V1.3 / `1.3.0`** consumer adaptation layer (`v1.3-site.css`) as an inherited compatibility layer. Its retained template/source anchor is `8354308445da9ac35ced2b37a7f503a08a0aaf72`. `build_v14.py` deterministically projects that retained source into the current V1.4 publication identity and adds the exact V1.4 Stable stylesheet dependency closure. The inherited V1.3 layer is not represented as the active shared Glaze entrypoint.

## Build and validation

From `sites/design/website`:

```bash
python3 validate.py
python3 build_v14.py
python3 validate_v14_artifact.py
python3 browser_v14_artifact_smoke.py
node --check site.js
```

`validate.py` continues to validate the retained source/template and synchronized Facet identity. `build_v14.py` then produces the current publication artifact from the exact V1.4 Stable source. `validate_v14_artifact.py` verifies the V1.4 publication markers, entrypoint integrity, security-header contract, and artifact closure. `browser_v14_artifact_smoke.py` exercises the exact built artifact in real Chrome across governed desktop, tablet, and mobile widths.

## Canonical production acceptance

Canonical production verification remains manual until the external Cloudflare Pages source cutover has been independently performed and verified. After that provider-side source change, rebuild the reviewed artifact and run:

```bash
python3 build_v14.py
python3 validate_v14_artifact.py
python3 verify_v14_deployment.py --target production
```

`verify_v14_deployment.py` accepts only the canonical Design Center host and the verified `goreecloud-design.pages.dev` namespace. It compares every fetchable `dist/` artifact byte-for-byte with the live deployment, requires the reviewed security headers and true HTTP 404 behavior, and checks the current V1.4 fail-closed publication markers.

The GitHub workflow exposes canonical-host verification only on `workflow_dispatch`; pull-request and push validation cannot silently become production acceptance.

## Production boundary

The central package is not production-authoritative merely because it is build-valid. Keep the migration registry fail-closed until Cloudflare Pages is verified to use `GoreeCloud/goreecloud-static-websites`, branch `main`, root `sites/design/website`, build command `python3 build_v14.py`, output `dist`, and the canonical domain passes exact deployed-content and rendered-browser acceptance. Legacy-source retirement remains a separate final migration gate.
