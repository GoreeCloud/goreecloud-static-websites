# Security Center Production Verification — 2026-09-10

## Decision

**Production verification accepted for `security.goreecloud.com` at central repository revision `256daf235066b4fd1f931e50e45e366fa92f45e7`.**

This record establishes that the public Security Center deployment has been cut over from its legacy website source to the centralized GoreeCloud static-website repository and that the observed production response matches the reviewed V1.3 deployment contract described below.

This decision does **not** retire or delete `GoreeCloud/goreecloud-wardveil-security`, transfer Wardveil runtime authority, or establish any security-control execution claim beyond the public website deployment itself.

## Cloudflare Pages configuration evidence

The production Pages project `goreecloud-security` was observed with:

- Git repository: `GoreeCloud/goreecloud-static-websites`
- Production branch: `main`
- Root directory: `sites/security`
- Build command: `python3 website/build.py`
- Build output directory: `website/dist`
- Automatic deployments: enabled after cutover verification
- Production custom domain: `security.goreecloud.com`

The Cloudflare deployment view showed a successful production deployment sourced from `main` revision prefix `256daf2`, corresponding to the exact canonical repository revision:

`256daf235066b4fd1f931e50e45e366fa92f45e7`

## Live production response evidence

A direct HTTPS request to the canonical production origin returned `HTTP/2 200`.

The deployed root response included the committed Security Center policy, including:

- `Content-Security-Policy`
- `Cross-Origin-Opener-Policy: same-origin`
- `Cross-Origin-Resource-Policy: same-origin`
- `Permissions-Policy`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`

The live response policy matched `sites/security/website/_headers` for the reviewed source revision.

A deliberately missing path under:

`https://security.goreecloud.com/__goreecloud-deployment-smoke__/missing/path`

returned `HTTP/2 404` with `Cache-Control: no-store`, confirming the production missing-path behavior.

## GLAZE UI V1.3 evidence

The live production HTML reported:

- `data-glaze-version="1.3.0"`
- `<meta name="goreecloud-glaze-ui" content="1.3.0">`
- `<meta name="goreecloud-glaze-source-revision" content="8354308445da9ac35ced2b37a7f503a08a0aaf72">`

The reviewed rendered page also visibly loaded the current Security Center V1.3 presentation and Sentinel Fold identity rather than the former website surface.

## Authority boundary

This record verifies the **public Security Center website deployment** only.

It does not by itself prove or authorize:

- Wardveil runtime enforcement success;
- protection, scan, quarantine, detection, response, or incident-execution success;
- Privacy Shield authorization;
- Identity authority;
- Everkeep recovery readiness;
- Mesh runtime acceptance;
- any private application or service runtime state.

Those remain producer-authoritative and independently evidenced.

## Legacy-source retirement

`GoreeCloud/goreecloud-wardveil-security` remains a project/runtime authority and may still contain the former website subtree or references. The website deployment source has been cut over, but **legacy website source retirement is not recorded by this verification alone**.

Before any legacy website subtree or deployment reference is removed, verify that:

1. no Cloudflare Pages configuration still depends on the legacy website source;
2. no rollback or automation path requires the legacy static website subtree;
3. documentation and deployment references have been reconciled to the centralized package; and
4. the resulting state is revalidated.

## Result

Security Center may advance in `sites/manifest.json` from `deployment_state: legacy-source` to `deployment_state: production-verified` for this verified deployment revision.

`legacy-source-retired` remains a later, separately verified state.
