# Static Website Consolidation Status

**Canonical target:** `GoreeCloud/goreecloud-static-websites`  
**Reviewed:** 2026-09-10  
**GLAZE UI source/build baseline:** V1.3 / 1.3.0  
**Verified Security production revision:** `256daf235066b4fd1f931e50e45e366fa92f45e7`  
**Verified Privacy production revision:** `80379f6962a5ded6c01317542941a2c55aedd922`  
**Verified Identity production revision:** `43141921a2c4915dd6e536dfa7af8d5da70a3319`  
**Verified Suite production revision:** `807adc08c955e37711ec6ba2c64a656d3bff0bfb` — corrected 45-product / 9-group publication  
**Historical Suite production revision:** `f03b0c5d62f870a52fda286636771db2a34d3aaf` — incomplete 27-product publication

## Current state

Source consolidation and GLAZE UI V1.3 source/build reconciliation are complete for the thirteen authoritative static website packages on canonical `main`.

Production deployment migration is proceeding site by site. **Security Center, Privacy Center, Identity Center, and GoreeCloud Suite are `production-verified`.** The other nine packages remain `legacy-source` until their own Cloudflare source cutover and exact production verification are completed.

The corrected Suite publication is accepted at exact central revision `807adc08c955e37711ec6ba2c64a656d3bff0bfb`. The Cloudflare GitHub App reported a successful deployment for that exact revision, and the repository's independent read-only production workflow waited until `suite.goreecloud.com` matched the exact reviewed artifact before accepting the live result. The live HTTP and Chrome gates then passed for the reconciled 45-product / 9-group publication, including the corrected 320-pixel responsive behavior.

The earlier Suite deployment at revision `f03b0c5d62f870a52fda286636771db2a34d3aaf` remains valid historical evidence for that exact 27-product publication, but it is not the current accepted Suite revision.

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
| Suite | `suite.goreecloud.com` | `sites/suite` | `validated-in-central-repo` | **`production-verified`** |
| Design Center | `design.goreecloud.com` | `sites/design` | `validated-in-central-repo` | `legacy-source` |
| Privacy Center | `privacy.goreecloud.com` | `sites/privacy` | `validated-in-central-repo` | **`production-verified`** |
| Security Center / Wardveil | `security.goreecloud.com` | `sites/security` | `validated-in-central-repo` | **`production-verified`** |
| Continuity Center / Everkeep | `everkeep.goreecloud.com` | `sites/everkeep` | `validated-in-central-repo` | `legacy-source` |
| Identity Center | `id.goreecloud.com` | `sites/identity` | `validated-in-central-repo` | **`production-verified`** |
| Manager public site | `manage.goreecloud.com` | `sites/manager` | `validated-in-central-repo` | `legacy-source` |
| Mesh Center | `mesh.goreecloud.com` | `sites/mesh` | `validated-in-central-repo` | `legacy-source` |

The manifest remains the machine-readable controlling registry for these states.

## Suite portfolio correction and reacceptance

The prior V1.3 migration incorrectly treated an older 27-application “Initial Suite Registry” as a complete current portfolio. A newer authoritative Suite specification preserves a September 1 baseline of 38 application/service cards, and later project specifications establish additional Suite products. The canonical Drive inventory was reconciled to **45 verified products across 9 functional product groups**.

The corrected directory restores products that were wrongly dropped from the recorded baseline—such as GoreeCloud Documents, Drive, File Manager, Mail, Messenger, Maps, Terminal, App Store, Gateway, AI, Index, and Code—and includes later verified products GoreeCloud Health, Reader, Router OS, Social, Home, and Home Security. GoreeCloud Website remains part of the broader Suite portfolio.

Shared Integral Platform Systems and application-centered capability identities retain their separate authority boundaries and are not inflated into the 45-product count merely because they integrate with the Suite. Products without approved canonical artwork use neutral identity treatment rather than fabricated official marks.

PR #42 added a stronger production browser gate and exposed a real 320-pixel horizontal-overflow defect. The defect was corrected by allowing the hero grid to shrink and the exact Glaze revision token to wrap safely. The exact PR candidate passed local Chrome validation at 1180, 768, 390, and 320 pixels before merge.

After PR #42 merged as `807adc08c955e37711ec6ba2c64a656d3bff0bfb`, the production workflow initially detected stale live consumer CSS and failed closed for six polling attempts. It then observed exact byte convergence, passed the full canonical-domain HTTP verifier, and passed the live Chrome smoke at all four viewport widths. Suite is therefore restored to `production-verified` for the corrected 45-product publication.

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

### GoreeCloud Suite — current accepted revision

GoreeCloud Suite is production-verified at exact central revision `807adc08c955e37711ec6ba2c64a656d3bff0bfb` using `main`, root `sites/suite`, build command `python3 scripts/build_public_site.py`, output `dist`, and Cloudflare Pages project `goreecloud-suite`.

The Cloudflare GitHub App reported a successful deployment for that exact revision. Independent live verification established exact equality for the reviewed root, 404, sitemap, robots, consumer CSS, and Glaze bytes; committed response headers; true HTTP 404 with `no-store`; GLAZE UI V1.3 metadata and exact Glaze blob integrity; canonical Suite URLs; 45 products in 9 groups; and successful live Chrome rendering at 1180, 768, 390, and 320 pixels with all images loaded and no 320-pixel horizontal overflow.

See `docs/production-verification-suite-2026-09-10.md`.

### GoreeCloud Suite — historical exact-revision evidence

The earlier Suite result at exact revision `f03b0c5d62f870a52fda286636771db2a34d3aaf` remains historical evidence for the incomplete 27-product publication. It must not be used as the current acceptance revision.

## Authority boundaries

These production decisions apply only to public website deployments. They do not establish Wardveil runtime protection, Privacy Shield authorization, Identity runtime acceptance, Suite product runtime readiness, Everkeep recovery state, Mesh authority, Manager state, or any other platform execution claim.

## Legacy-source retirement remains separate

`production-verified` does not mean `legacy-source-retired`. GoreeCloud's Wardveil, Privacy Shield, Identity, and Suite project repositories retain their non-site project/runtime authority. Former website subtrees or deployment references may be removed only after Cloudflare, automation, rollback, documentation, and preservation dependencies are independently cleared.

## Remaining production migration sequence

Nine initial production acceptance actions remain for the nine sites that still show `legacy-source`.

For each site or materially changed publication:

1. use the exact centralized source/build/output contract;
2. verify the custom production domain and successful deployment of the exact reviewed central revision;
3. verify HTTP status, security headers, explicit 404 behavior, GLAZE UI V1.3 markers, assets, navigation, and rendered behavior;
4. bind the result to the exact deployed central Git revision;
5. only then advance that publication to `production-verified`;
6. retire any legacy website source only after its separate dependency/rollback/preservation review passes.

## Immediate next action

Proceed with the Continuity Center / Everkeep Cloudflare cutover using central root `sites/everkeep`, build command `python3 scripts/build_public_site.py`, and output directory `dist`; then independently verify `everkeep.goreecloud.com` before changing its deployment state.
