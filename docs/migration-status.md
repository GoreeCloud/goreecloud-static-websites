# Static Website Consolidation Status

**Canonical target:** `GoreeCloud/goreecloud-static-websites`  
**Reviewed:** 2026-09-10  
**GLAZE UI source/build baseline:** V1.3 / 1.3.0  
**Verified Security production revision:** `256daf235066b4fd1f931e50e45e366fa92f45e7`  
**Verified Privacy production revision:** `80379f6962a5ded6c01317542941a2c55aedd922`  
**Verified Identity production revision:** `43141921a2c4915dd6e536dfa7af8d5da70a3319`  
**Prior verified Suite revision:** `f03b0c5d62f870a52fda286636771db2a34d3aaf` — historical 27-product publication  
**Latest corrected Suite Cloudflare deployment candidate:** `0f35e3145e31a7f79950040db6a875b32374c54e` — provider deployment successful; custom-domain/rendered reverification pending

## Current state

Source consolidation and GLAZE UI V1.3 source/build reconciliation are complete for the thirteen authoritative static website packages on canonical `main`.

Production deployment migration is proceeding site by site. **Security Center, Privacy Center, and Identity Center are `production-verified`.** GoreeCloud Suite remains **`deployment-cutover-pending`** because a material portfolio correction expands the public directory from an incomplete 27-product publication to the reconciled 45-product authority. The corrected source and CI are complete, and the Cloudflare GitHub App reports a successful deployment of exact central revision `0f35e3145e31a7f79950040db6a875b32374c54e`; independent custom-domain delivery, rendered review, and exact public-response verification remain pending. The other nine packages remain `legacy-source` until their own Cloudflare source cutover and exact production verification are completed.

The earlier Suite deployment at revision `f03b0c5d62f870a52fda286636771db2a34d3aaf` remains valid historical evidence for that exact publication, but it must not be used as acceptance evidence for the corrected 45-product source.

Production verification is independent per site and per materially changed publication revision. A central source build, CI pass, another site's successful cutover, a deployment-provider success check, or an older accepted revision never establishes production acceptance for changed public bytes.

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
| Suite | `suite.goreecloud.com` | `sites/suite` | `validated-in-central-repo` | **`deployment-cutover-pending`** |
| Design Center | `design.goreecloud.com` | `sites/design` | `validated-in-central-repo` | `legacy-source` |
| Privacy Center | `privacy.goreecloud.com` | `sites/privacy` | `validated-in-central-repo` | **`production-verified`** |
| Security Center / Wardveil | `security.goreecloud.com` | `sites/security` | `validated-in-central-repo` | **`production-verified`** |
| Continuity Center / Everkeep | `everkeep.goreecloud.com` | `sites/everkeep` | `validated-in-central-repo` | `legacy-source` |
| Identity Center | `id.goreecloud.com` | `sites/identity` | `validated-in-central-repo` | **`production-verified`** |
| Manager public site | `manage.goreecloud.com` | `sites/manager` | `validated-in-central-repo` | `legacy-source` |
| Mesh Center | `mesh.goreecloud.com` | `sites/mesh` | `validated-in-central-repo` | `legacy-source` |

The manifest remains the machine-readable controlling registry for these states.

## Suite portfolio correction

The prior V1.3 migration incorrectly treated an older 27-application “Initial Suite Registry” as a complete current portfolio. A newer authoritative Suite specification preserves a September 1 baseline of 38 application/service cards, and later project specifications establish additional Suite products. The canonical Drive inventory has now been reconciled to **45 verified products across 9 functional product groups**.

The corrected current directory restores the products that were wrongly dropped from the recorded baseline—such as GoreeCloud Documents, Drive, File Manager, Mail, Messenger, Maps, Terminal, App Store, Gateway, AI, Index, and Code—and includes later verified products GoreeCloud Health, Reader, Router OS, Social, Home, and Home Security. GoreeCloud Website remains part of the broader Suite portfolio.

Shared Integral Platform Systems and application-centered capability identities retain their separate authority boundaries and are not inflated into the 45-product count merely because they integrate with the Suite. Products without approved canonical artwork use neutral identity treatment rather than fabricated official marks.

Because this changes public bytes materially, the corrected Suite revision must pass source/build/CI and then be independently deployed and live-verified before Suite can return to `production-verified`. Source/build/CI and Cloudflare provider deployment are now complete for the current corrected candidate; custom-domain and rendered verification remain outstanding.

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

Public DNS at both `1.1.1.1` and `8.8.8.8` resolved the canonical `id.goreecloud.com` CNAME to `goreecloud-identity.pages.dev`. The Cloudflare custom domain was observed Active with SSL enabled. Live verification established HTTP 200 for the canonical root, HTTP 404 with `Cache-Control: no-store` for an intentionally missing path, committed security headers, GLAZE UI `1.3.0`, exact Glaze source revision `8354308445da9ac35ced2b37a7f503a08a0aaf72`, and a live sitemap containing `https://id.goreecloud.com/`.

See `docs/production-verification-identity-2026-09-10.md`.

### GoreeCloud Suite — historical exact-revision evidence

GoreeCloud Suite was previously verified at exact central revision `f03b0c5d62f870a52fda286636771db2a34d3aaf` after Cloudflare Pages was cut over to `main`, root `sites/suite`, build command `python3 scripts/build_public_site.py`, and output `dist`. That live result passed HTTP 200, true HTTP 404 with `no-store`, committed response headers, GLAZE UI V1.3 metadata, canonical sitemap, exact Glaze CSS blob integrity, and rendered review.

That evidence remains historical and exact-revision scoped. It covered the incomplete 27-product directory and therefore does not accept the corrected 45-product publication. See `docs/production-verification-suite-2026-09-10.md`.

### GoreeCloud Suite — corrected deployment candidate

Cloudflare's GitHub App reports a successful deployment for exact central `main` revision `0f35e3145e31a7f79950040db6a875b32374c54e`, which includes the reconciled 45-product Suite source. This proves provider-side deployment success for that revision. It does **not** yet establish `suite.goreecloud.com` custom-domain delivery, HTTP/security-header behavior, exact public-response equivalence, rendered/accessibility acceptance, or production verification. The manifest therefore correctly remains `deployment-cutover-pending`.

## Authority boundaries

These production decisions apply only to public website deployments. They do not establish Wardveil runtime protection, Privacy Shield authorization, Identity runtime acceptance, Suite product runtime readiness, Everkeep recovery state, Mesh authority, Manager state, or any other platform execution claim.

## Legacy-source retirement remains separate

`production-verified` does not mean `legacy-source-retired`. GoreeCloud's Wardveil, Privacy Shield, Identity, and Suite project repositories retain their non-site project/runtime authority. Former website subtrees or deployment references may be removed only after Cloudflare, automation, rollback, documentation, and preservation dependencies are independently cleared.

## Remaining production migration sequence

Ten production acceptance actions remain: Suite reverification for the corrected 45-product publication plus initial production verification for the nine sites that still show `legacy-source`.

For each site or materially changed publication:

1. use the exact centralized source/build/output contract;
2. verify the custom production domain and successful deployment of the exact reviewed central revision;
3. verify HTTP status, security headers, explicit 404 behavior, GLAZE UI V1.3 markers, assets, navigation, and rendered behavior;
4. bind the result to the exact deployed central Git revision;
5. only then advance that publication to `production-verified`;
6. retire any legacy website source only after its separate dependency/rollback/preservation review passes.

## Immediate next action

Independently reverify the corrected 45-product publication at `https://suite.goreecloud.com/` against exact deployed revision `0f35e3145e31a7f79950040db6a875b32374c54e`. Require canonical-domain HTTP behavior, committed security headers, true 404 behavior, GLAZE UI V1.3 markers and exact source revision, canonical sitemap, representative 45-product rendering, and exact deployment binding before restoring Suite to `production-verified`.

If Suite reverification passes, proceed next with the Continuity Center / Everkeep Cloudflare cutover using central root `sites/everkeep`, build command `python3 scripts/build_public_site.py`, and output directory `dist`; then independently verify `everkeep.goreecloud.com` before changing its deployment state.
