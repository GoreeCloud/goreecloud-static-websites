# Static Website Consolidation Status

**Canonical target:** `GoreeCloud/goreecloud-static-websites`  
**Reviewed:** 2026-09-10  
**GLAZE UI source/build baseline:** V1.3 / 1.3.0  
**Verified Security production revision:** `256daf235066b4fd1f931e50e45e366fa92f45e7`  
**Verified Privacy production revision:** `80379f6962a5ded6c01317542941a2c55aedd922`

## Current state

Source consolidation and GLAZE UI V1.3 source/build reconciliation are complete for the thirteen authoritative static website packages on canonical `main`.

Production deployment migration is proceeding site by site. **Security Center and Privacy Center are now `production-verified`.** The other eleven packages remain `legacy-source` until their own Cloudflare source cutover and exact production verification are completed.

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
| Suite | `suite.goreecloud.com` | `sites/suite` | `validated-in-central-repo` | `legacy-source` |
| Design Center | `design.goreecloud.com` | `sites/design` | `validated-in-central-repo` | `legacy-source` |
| Privacy Center | `privacy.goreecloud.com` | `sites/privacy` | `validated-in-central-repo` | **`production-verified`** |
| Security Center / Wardveil | `security.goreecloud.com` | `sites/security` | `validated-in-central-repo` | **`production-verified`** |
| Continuity Center / Everkeep | `everkeep.goreecloud.com` | `sites/everkeep` | `validated-in-central-repo` | `legacy-source` |
| Identity Center | `id.goreecloud.com` | `sites/identity` | `validated-in-central-repo` | `legacy-source` |
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

## Authority boundaries

These production decisions apply only to the public website deployments.

Security Center production verification does not establish Wardveil runtime protection, scan, detect, quarantine, response, incident, or other execution success. Privacy Center production verification does not establish any Privacy Shield authorization decision, consent state, purpose grant, durable authorization state, or runtime acceptance. Producer systems remain authoritative for those states.

Neither decision transfers Identity, Everkeep, Mesh, Manager, or other platform authority.

## Legacy-source retirement remains separate

`production-verified` does not mean `legacy-source-retired`.

For Security, `GoreeCloud/goreecloud-wardveil-security` remains the Wardveil project/runtime authority. For Privacy, `GoreeCloud/goreecloud-privacy-shield` remains the Privacy Shield project/runtime authority. Before removing former website subtrees or related deployment references, verify that no Cloudflare, automation, rollback, documentation, preservation, or other governed dependency still requires those legacy website materials.

The same rule applies to every other site after its future production cutover.

## Remaining production migration sequence

For each of the remaining eleven sites:

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

Continuity Center / Everkeep is a good next controlled cutover because it uses the same public-system-site family and already has a current V1.3 central package:

- domain: `everkeep.goreecloud.com`
- central path: `sites/everkeep`
- legacy website source: `GoreeCloud/goreecloud-everkeep`

Do not batch the remaining sites into a single unverified cutover. Preserve per-site deployment and acceptance evidence.
