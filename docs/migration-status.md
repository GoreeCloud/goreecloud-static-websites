# Static Website Consolidation Status

**Canonical target:** `GoreeCloud/goreecloud-static-websites`  
**Reviewed:** 2026-09-10  
**GLAZE UI source/build baseline:** V1.3 / 1.3.0  
**Verified Security production revision:** `256daf235066b4fd1f931e50e45e366fa92f45e7`  
**Verified Privacy production revision:** `80379f6962a5ded6c01317542941a2c55aedd922`  
**Verified Identity production revision:** `43141921a2c4915dd6e536dfa7af8d5da70a3319`  
**Verified Suite production revision:** `f03b0c5d62f870a52fda286636771db2a34d3aaf`

## Current state

Source consolidation and GLAZE UI V1.3 source/build reconciliation are complete for the thirteen authoritative static website packages on canonical `main`.

Production deployment migration is proceeding site by site. **Security Center, Privacy Center, Identity Center, and GoreeCloud Suite are now `production-verified`.** The other nine packages remain `legacy-source` until their own Cloudflare source cutover and exact production verification are completed.

Production verification is independent per site. A central source build, CI pass, or another site's successful cutover never establishes production acceptance for a different site.

## Mandatory consolidation rule

Every GoreeCloud standalone static public website must be stored, maintained, and referenced from `GoreeCloud/goreecloud-static-websites` unless an explicit governed architectural exception is approved.

Application frontends, authenticated product UIs, extension pages, generated artifacts, test fixtures, internal/debug pages, demos, reference pages, and inherited upstream documentation are not reclassified as standalone websites merely because they contain browser-renderable files.

No legacy repository may remain a second website source authority after its site's deployment and retirement gates are complete.

## Authoritative website inventory and deployment state

| Site | Domain | Central path | Migration state | Deployment state |
| --- | --- | --- | --- | --- |
| Main | `www.goreecloud.com` | `sites/main` | `validated-in-central-repo` | `legacy-source` |
| Projects | `projects.goreecloud.com` | `sites/projects` | `validated-in-central-repo` | `legacy-source` |
| Roadmap | `roadmap.goreecloud.com` | `sites/roadmap` | `validated-in-central-repo` | `legacy-source` |
| Blog | `blog.goreecloud.com` | `sites/blog` | `validated-in-central-repo` | `legacy-source` |
| Archive | `archive.goreecloud.com` | `sites/archive` | `validated-in-central-repo` | `legacy-source` |
| Suite | `suite.goreecloud.com` | `sites/suite` | `validated-in-central-repo` | **`production-verified`** |
| Design Center | `design.goreecloud.com` | `sites/design` | `validated-in-central-repo` | `legacy-source` |
| Privacy Center | `privacy.goreecloud.com` | `sites/privacy` | `validated-in-central-repo` | **`production-verified`** |
| Security Center / Wardveil | `security.goreecloud.com` | `sites/security` | `validated-in-central-repo` | **`production-verified`** |
| Continuity Center / Everkeep | `everkeep.goreecloud.com` | `sites/everkeep` | `validated-in-central-repo` | `legacy-source` |
| Identity Center | `id.goreecloud.com` | `sites/identity` | `validated-in-central-repo` | **`production-verified`** |
| Manager public site | `manage.goreecloud.com` | `sites/manager` | `validated-in-central-repo` | `legacy-source` |
| Mesh Center | `mesh.goreecloud.com` | `sites/mesh` | `validated-in-central-repo` | `legacy-source` |

The manifest remains the machine-readable controlling registry for these states.

## Production-verification evidence

### Security Center

Security Center was verified after Cloudflare Pages was cut over to the central repository using `main`, root `sites/security`, build command `python3 website/build.py`, and output `website/dist`. The successful production deployment was tied to central revision `256daf235066b4fd1f931e50e45e366fa92f45e7`.

Live verification established HTTP 200 for the canonical root, HTTP 404 with `Cache-Control: no-store` for an intentionally missing path, committed security headers, GLAZE UI `1.3.0`, exact Glaze source revision `8354308445da9ac35ced2b37a7f503a08a0aaf72`, and successful rendered review.

See `docs/production-verification-security-2026-09-10.md`.

### Privacy Center

Privacy Center was verified after Cloudflare Pages was cut over to the central repository using `main`, root `sites/privacy`, build command `python3 website/build.py`, and output `website/dist`. The successful production deployment was tied to central revision `80379f6962a5ded6c01317542941a2c55aedd922`.

Live verification established HTTP 200 for the canonical root, HTTP 404 with `Cache-Control: no-store` for an intentionally missing path, committed security headers, GLAZE UI `1.3.0`, exact Glaze source revision `8354308445da9ac35ced2b37a7f503a08a0aaf72`, and exact production Git blob SHA `4c3ad293ba9196e2e5a32700b530ec67fd01cef6` for `/assets/glaze-v1.3.0.css`. Rendered review confirmed the current Privacy Center V1.3 surface loaded successfully.

See `docs/production-verification-privacy-2026-09-10.md`.

### Identity Center

Identity Center was verified after Cloudflare Pages was cut over to the central repository using `main` with root `sites/identity` and no build step. The successful Cloudflare Pages deployment was tied to exact central revision `43141921a2c4915dd6e536dfa7af8d5da70a3319` by the Cloudflare GitHub App deployment check.

Public DNS at both `1.1.1.1` and `8.8.8.8` resolved the canonical `id.goreecloud.com` CNAME to `goreecloud-identity.pages.dev`. The Cloudflare custom domain was observed Active with SSL enabled. Live verification through the current public-DNS-resolved Cloudflare address established HTTP 200 for the canonical root, HTTP 404 with `Cache-Control: no-store` for an intentionally missing path, committed security headers, GLAZE UI `1.3.0`, exact Glaze source revision `8354308445da9ac35ced2b37a7f503a08a0aaf72`, and a live sitemap containing `https://id.goreecloud.com/`. Rendered review confirmed the current Identity Center V1.3 surface loaded successfully.

The explicit 404 behavior was corrected during acceptance after the initial centralized package returned SPA-style HTTP 200 for missing paths. The resulting 404 publication contract is now guarded by dedicated CI.

See `docs/production-verification-identity-2026-09-10.md`.

### GoreeCloud Suite

GoreeCloud Suite was verified after Cloudflare Pages was cut over to the central repository using `main`, root `sites/suite`, build command `python3 scripts/build_public_site.py`, and output `dist`. The Cloudflare GitHub App tied the successful production deployment to exact central revision `f03b0c5d62f870a52fda286636771db2a34d3aaf`.

Live verification established HTTP 200 for `https://suite.goreecloud.com/`, HTTP 404 with `Cache-Control: no-store` for an intentionally missing path, the committed Suite response-header contract, GLAZE UI `1.3.0`, exact Glaze source revision `8354308445da9ac35ced2b37a7f503a08a0aaf72`, canonical sitemap output for `https://suite.goreecloud.com/`, and exact production Git blob SHA `4c3ad293ba9196e2e5a32700b530ec67fd01cef6` for `/assets/glaze-v1.3.0.css`. Rendered review confirmed the current Suite V1.3 directory surface loaded successfully.

The Suite 404 behavior was hardened before cutover by PR #34 and is guarded by dedicated publication-contract CI.

See `docs/production-verification-suite-2026-09-10.md`.

## Authority boundaries

These production decisions apply only to the public website deployments.

Security Center production verification does not establish Wardveil runtime protection, scan, detect, quarantine, response, incident, or other execution success. Privacy Center production verification does not establish any Privacy Shield authorization decision, consent state, purpose grant, durable authorization state, or runtime acceptance. Identity Center production verification does not establish production authentication, SSO, account, session, device, credential, authorization, recovery, delegated-authority, or backend-runtime acceptance. Suite production verification does not establish production readiness, release promotion, or runtime acceptance for any application or capability identity listed by the Suite directory.

None of these website decisions transfers Everkeep, Mesh, Manager, or other platform authority.

## Legacy-source retirement remains separate

`production-verified` does not mean `legacy-source-retired`.

For Security, `GoreeCloud/goreecloud-wardveil-security` remains the Wardveil project/runtime authority. For Privacy, `GoreeCloud/goreecloud-privacy-shield` remains the Privacy Shield project/runtime authority. For Identity, `GoreeCloud/goreecloud-identity` remains the Identity project/runtime authority. For Suite, `GoreeCloud/goreecloud-suite` remains a GoreeCloud project source and is not deleted or retired by the public website cutover. Before removing former website subtrees or related deployment references, verify that no Cloudflare, automation, rollback, documentation, preservation, or other governed dependency still requires those legacy website materials.

The same rule applies to every other site after its future production cutover.

## Remaining production migration sequence

For each of the remaining nine sites:

1. pause automatic production deployments before source reassignment when appropriate;
2. connect the existing Cloudflare Pages project to `GoreeCloud/goreecloud-static-websites`;
3. keep production branch `main` and configure the site's exact central root/build/output contract;
4. verify the custom production domain remains attached;
5. deploy the reviewed central revision;
6. verify HTTP status, headers, 404 behavior, GLAZE UI V1.3 markers, assets, navigation, and rendered behavior;
7. bind the result to the exact deployed central Git revision;
8. only then advance that site's manifest deployment state to `production-verified`;
9. retire legacy website source only after its separate dependency/rollback/preservation review passes.

## Next site

Continuity Center / Everkeep remains a good next controlled cutover because it uses the same public-system-site family and already has a current V1.3 central package:

- domain: `everkeep.goreecloud.com`
- central path: `sites/everkeep`
- legacy website source: `GoreeCloud/goreecloud-everkeep`

Do not batch the remaining sites into a single unverified cutover. Preserve per-site deployment and acceptance evidence.
