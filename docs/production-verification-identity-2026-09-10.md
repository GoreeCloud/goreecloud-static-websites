# Identity Center Production Verification — 2026-09-10

## Decision

**Production verification accepted for `id.goreecloud.com` at central repository revision `43141921a2c4915dd6e536dfa7af8d5da70a3319`.**

This record establishes that the public Identity Center deployment has been cut over from its former website source to the centralized GoreeCloud static-website repository and that the observed production response matches the reviewed GLAZE UI V1.3 publication contract described below.

This decision applies only to the public Identity Center website. It does **not** establish production acceptance for GoreeCloud Identity runtime authentication, authorization, accounts, devices, credentials, sessions, application/service identity, recovery, or delegated-authority execution.

## Central repository and Cloudflare deployment evidence

The Identity Pages project was observed after cutover with:

- Git repository: `GoreeCloud/goreecloud-static-websites`
- Production branch: `main`
- Root directory: `sites/identity`
- Build command: none
- Build output directory: the configured site root
- Automatic deployments: enabled
- Pages project: `goreecloud-identity`
- Canonical custom domain: `id.goreecloud.com`
- Custom-domain status: Active with SSL enabled

The Cloudflare GitHub App recorded a successful `Cloudflare Pages: goreecloud-identity` deployment for exact central repository revision:

`43141921a2c4915dd6e536dfa7af8d5da70a3319`

The corresponding Cloudflare check reported `Deployed successfully` for commit prefix `4314192`.

## Canonical hostname and DNS evidence

The authoritative GoreeCloud public website namespace assigns Identity Center to:

`https://id.goreecloud.com/`

During cutover, the central sitemap and CI contract were corrected from the superseded `identity.goreecloud.com` hostname to the approved `id.goreecloud.com` hostname.

Public DNS checks against both Cloudflare DNS (`1.1.1.1`) and Google Public DNS (`8.8.8.8`) returned:

`goreecloud-identity.pages.dev.`

for the `id.goreecloud.com` CNAME, establishing that public DNS had been cut over to the Pages project. A stale client-local resolver path temporarily continued returning Porkbun Pixie records; production verification therefore used an address resolved from the updated public DNS path rather than treating that client cache as authoritative production state.

## Live production response evidence

A direct HTTPS request to the canonical hostname through the current Cloudflare-resolved production address returned `HTTP/2 200` with `server: cloudflare`.

The live root response included the committed Identity Center response policy, including:

- `Content-Security-Policy`
- `Permissions-Policy`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`

The rendered production page visibly loaded the current GoreeCloud Identity Center presentation rather than the former publication surface.

## Explicit 404 correction and verification

Initial post-cutover verification discovered that an unknown path returned `HTTP 200` because the centralized Identity package lacked an explicit top-level `404.html` and Cloudflare fell back to SPA-style behavior.

That defect was corrected by adding `sites/identity/404.html`. The corrective file was committed directly to `main` as `17cb54fd82ec457f598931fc3cd3b0735dedba16`; this bypass of the normal short-lived-branch/PR process was explicitly recorded in PR #32 rather than hidden. PR #32 then added a durable Identity publication-contract CI gate through the normal review path, and both the dedicated Identity publication validation and repository validation passed before merge.

After deployment of the corrected source, the deliberately missing path:

`https://id.goreecloud.com/__goreecloud-deployment-smoke__/missing/path`

returned:

- `HTTP/2 404`
- `Cache-Control: no-store`
- `server: cloudflare`
- the intended Identity Center 404 body

The 404 body explicitly states that no identity, authorization, session, credential, recovery, or production-runtime state is implied by the error response.

## GLAZE UI V1.3 evidence

The live production HTML reported:

- `data-glaze-version="1.3.0"`
- `<meta name="goreecloud-glaze-ui" content="1.3.0">`
- `<meta name="goreecloud-glaze-source-revision" content="8354308445da9ac35ced2b37a7f503a08a0aaf72">`

The rendered production page visibly loaded the current Identity Center V1.3 presentation.

## Sitemap evidence

The live production sitemap returned:

`https://id.goreecloud.com/`

confirming that the deployed publication advertises the approved canonical hostname.

## Authority boundary

This record verifies the **public Identity Center website deployment** only.

It does not by itself prove or authorize:

- successful production authentication or SSO;
- account, session, device, credential, passkey, MFA, recovery, or authorization behavior;
- delegated authority or service-identity execution;
- Privacy Shield authorization;
- Wardveil security-control success;
- Everkeep recovery readiness;
- Mesh runtime acceptance;
- any private Identity Center or backend runtime state.

Those remain producer-authoritative and independently evidenced.

## Legacy-source retirement

`GoreeCloud/goreecloud-identity` remains the GoreeCloud Identity project/runtime authority. Production verification of the centralized public website does not authorize deletion or retirement of the Identity repository itself.

Before any former website subtree, deployment reference, or rollback material in that repository is removed, verify that:

1. no Cloudflare Pages configuration still depends on it;
2. no rollback or automation path requires it;
3. documentation and deployment references have been reconciled to the centralized package; and
4. preservation requirements have been satisfied.

## Result

Identity Center may advance in `sites/manifest.json` from `deployment_state: legacy-source` to `deployment_state: production-verified` for central deployment revision `43141921a2c4915dd6e536dfa7af8d5da70a3319`.

`legacy-source-retired` remains a later, separately verified state.
