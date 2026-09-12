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
node --check site.js
```

`validate.py` rebuilds `dist/`, verifies the exact V1.3 source anchors, synchronized Facet identity, required artifact closure, accessibility/adaptation markers, security-header source contract, and fail-closed consumer-state language.

Repository CI additionally exercises the built `dist/` artifact in real Chrome. Canonical production byte/header and browser verification remain manual until the external Cloudflare Pages source cutover has been independently performed and verified.

## Production boundary

The central package is not production-authoritative merely because it is build-valid. Keep the migration registry fail-closed until Cloudflare Pages is verified to use `GoreeCloud/goreecloud-static-websites`, branch `main`, the Design Center site root/build contract, and the canonical domain passes exact deployed-content and browser acceptance.
