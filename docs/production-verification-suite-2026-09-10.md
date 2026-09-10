# GoreeCloud Suite Production Verification — 2026-09-10

## Decision

**Production verification accepted for `suite.goreecloud.com` at central repository revision `f03b0c5d62f870a52fda286636771db2a34d3aaf`.**

This record establishes that the public GoreeCloud Suite website has been cut over to the centralized GoreeCloud static-website repository and that the observed production response matches the reviewed GLAZE UI V1.3 publication contract described below.

This decision applies only to the public Suite website. It does **not** establish production acceptance for any Suite application, service, capability identity, backend, runtime, deployment, release, or lifecycle claim beyond the website itself.

## Central repository and Cloudflare deployment evidence

The Suite Cloudflare Pages project was observed after cutover with the centralized publication contract:

- Git repository: `GoreeCloud/goreecloud-static-websites`
- Production branch: `main`
- Root directory: `sites/suite`
- Build command: `python3 scripts/build_public_site.py`
- Build output directory: `dist`
- Pages project: `goreecloud-suite`
- Canonical custom domain: `suite.goreecloud.com`

The Cloudflare GitHub App recorded a successful `Cloudflare Pages: goreecloud-suite` deployment for exact central repository revision:

`f03b0c5d62f870a52fda286636771db2a34d3aaf`

The corresponding Cloudflare check reported `Deployed successfully` for commit prefix `f03b0c5`.

## Live production response evidence

A direct HTTPS request to:

`https://suite.goreecloud.com/`

returned:

- `HTTP/2 200`
- `server: cloudflare`
- `Cache-Control: public, max-age=0, must-revalidate`

The live root response included the committed Suite response policy, including:

- `Content-Security-Policy`
- `Cross-Origin-Opener-Policy: same-origin`
- `Cross-Origin-Resource-Policy: same-site`
- `Permissions-Policy`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`

The rendered production page visibly loaded the current GoreeCloud Suite V1.3 surface, including the authoritative 27-application, 7-functional-group, and 3-capability-identity directory presentation.

## Explicit 404 verification

Before production cutover, PR #34 added an explicit `sites/suite/404.html`, packaged it through the Suite build allowlist, removed the old general five-minute HTML cache policy, and added a dedicated Suite publication-contract CI gate.

After deployment, the deliberately missing path:

`https://suite.goreecloud.com/__goreecloud-deployment-smoke__/missing/path`

returned:

- `HTTP/2 404`
- `Cache-Control: no-store`
- `server: cloudflare`

This confirms the production site does not fall back to a false HTTP 200 for unknown paths.

## GLAZE UI V1.3 evidence

The live production HTML reported:

- `data-glaze-version="1.3.0"`
- `<meta name="goreecloud-glaze-ui" content="1.3.0">`
- `<meta name="goreecloud-glaze-source-revision" content="8354308445da9ac35ced2b37a7f503a08a0aaf72">`

The deployed canonical Glaze entrypoint:

`https://suite.goreecloud.com/assets/glaze-v1.3.0.css`

produced Git blob SHA:

`4c3ad293ba9196e2e5a32700b530ec67fd01cef6`

matching the reviewed canonical GLAZE UI V1.3 Stable entrypoint.

## Sitemap evidence

The live production sitemap returned the canonical Suite hostname:

`https://suite.goreecloud.com/`

## Authority boundary

This record verifies the **public GoreeCloud Suite website deployment** only.

It does not by itself prove or authorize:

- production readiness of any listed Suite application;
- correctness of an application's runtime, backend, security, privacy, continuity, identity, or networking behavior;
- release or lifecycle promotion for any application or capability identity;
- global GLAZE UI acceptance outside this reviewed website deployment;
- retirement or deletion of `GoreeCloud/goreecloud-suite`.

Application and service implementation/runtime authority remains with the applicable producer repository, specification, release process, and independently verified evidence.

## Legacy-source retirement

`GoreeCloud/goreecloud-suite` remains a GoreeCloud project source and is not retired or deleted by this website production verification.

Before any former website source, deployment reference, automation, rollback material, or preserved publication artifact in that repository is removed, verify that:

1. no Cloudflare Pages configuration still depends on it;
2. no rollback or automation path requires it;
3. documentation and deployment references have been reconciled to the centralized package; and
4. preservation requirements have been satisfied.

## Result

GoreeCloud Suite may advance in `sites/manifest.json` from `deployment_state: legacy-source` to `deployment_state: production-verified` for central deployment revision `f03b0c5d62f870a52fda286636771db2a34d3aaf`.

`legacy-source-retired` remains a later, separately verified state.
