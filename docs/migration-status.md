# Static Website Consolidation Status

**Canonical target:** `GoreeCloud/goreecloud-static-websites`  
**Reviewed:** 2026-09-06  
**Prior accepted thirteen-site checkpoint:** `c8e5629f323de850b8d345786713056ff0dc0ff1`  
**Current Labs validated candidate evidence:** `1acf890ca45cb7e92f8c802c86c090f0ce259b0c` plus the manifest-state follow-up on this branch  
**Overall state:** All fourteen identified standalone GoreeCloud static public website packages are now present in the canonical repository and are `validated-in-central-repo`. Deployment cutover, exact production verification, legacy-source retirement, remaining Glaze UI V1.1 migrations, and final Website deletion remain open.

## Mandatory consolidation rule

Every GoreeCloud standalone static public website must be stored, maintained, and referenced from `GoreeCloud/goreecloud-static-websites` unless an explicit governed architectural exception is approved.

Application frontends, authenticated product UIs, extension pages, generated artifacts, test fixtures, internal/debug pages, demos, reference pages, and inherited upstream documentation are not reclassified as standalone websites merely because they contain browser-renderable files.

No legacy repository may remain a second source authority after its site's deployment and retirement gates are complete. Build configuration, deployment configuration, documentation, automation, and references must ultimately point to the corresponding centralized package.

## Current source-migration state

All fourteen currently identified standalone public static website packages are `validated-in-central-repo`.

| Site | Domain | Central path | Migration state | Deployment state |
| --- | --- | --- | --- | --- |
| Main | `www.goreecloud.com` | `sites/main` | `validated-in-central-repo` | `legacy-source` |
| Projects | `projects.goreecloud.com` | `sites/projects` | `validated-in-central-repo` | `legacy-source` |
| Roadmap | `roadmap.goreecloud.com` | `sites/roadmap` | `validated-in-central-repo` | `legacy-source` |
| Blog | `blog.goreecloud.com` | `sites/blog` | `validated-in-central-repo` | `legacy-source` |
| Archive | `archive.goreecloud.com` | `sites/archive` | `validated-in-central-repo` | `legacy-source` |
| Suite | `suite.goreecloud.com` | `sites/suite` | `validated-in-central-repo` | `legacy-source` |
| Design Center | `design.goreecloud.com` | `sites/design` | `validated-in-central-repo` | `legacy-source` |
| Privacy Center | `privacy.goreecloud.com` | `sites/privacy` | `validated-in-central-repo` | `legacy-source` |
| Security Center / Wardveil | `security.goreecloud.com` | `sites/security` | `validated-in-central-repo` | `legacy-source` |
| Continuity Center / Everkeep | `everkeep.goreecloud.com` | `sites/everkeep` | `validated-in-central-repo` | `legacy-source` |
| Identity Center | `identity.goreecloud.com` | `sites/identity` | `validated-in-central-repo` | `legacy-source` |
| Manager public site | `manage.goreecloud.com` | `sites/manager` | `validated-in-central-repo` | `legacy-source` |
| Mesh Center | `mesh.goreecloud.com` | `sites/mesh` | `validated-in-central-repo` | `legacy-source` |
| Labs product center | `labs.goreecloud.com` | `sites/labs` | `validated-in-central-repo` | `legacy-source` |

The migration state and deployment state are intentionally separate. A validated central source package does not prove that Cloudflare Pages or production traffic uses that package.

## Labs reconciliation — September 6, 2026

Labs was introduced in `GoreeCloud/goreecloud-website` draft PR #116 after the original thirteen-site discovery checkpoint and therefore was not part of the earlier manifest. As a standalone static public site, it is automatically in scope for the centralization directive.

The original six-product migration base was captured from Website candidate `7d9b03c90d3ea2c74dacd2f03430a86dd93a3ba6`. The transitional Labs source was subsequently synchronized at `4179a935307396e71b8d28d8607cb2ad009d9cfa` so its current Cloudflare path follows the same visual-identity policy while cutover is pending.

The central Labs package includes GoreeCloud Home Security, GoreeCloud Home, GoreeCloud AI, GoreeCloud Containers, GoreeCloud Code, and GoreeCloud Boot. Boot remains Development-only and does not claim physical writes, filesystems, bootable runtime/media, signed releases, broader storage qualification, Stable status, or production deployment.

Exact central validation passed for the Labs source, isolated build artifact, JavaScript syntax, migration manifest, Main, Projects, Manager, and repository-level visual-identity enforcement at candidate `1acf890ca45cb7e92f8c802c86c090f0ce259b0c`. That evidence is sufficient to advance Labs from `source-copied` to `validated-in-central-repo`; it is not sufficient to advance deployment state.

## Visual identity reconciliation

The central candidate also corrects confirmed identity drift:

- Projects uses the canonical GoreeCloud Mesh Interlace mark.
- Manager uses the canonical GoreeCloud Manager icon.
- Labs uses exact canonical GoreeCloud AI and GoreeCloud Code artwork.
- Labs suppresses former Home, Security, OCI, and Boot text/acronym badges because those four products do not yet have approved canonical artwork.
- Main no longer carries the obsolete `goreecloud-artwork-pending.svg` placeholder in active centralized source.
- Repository CI now fails closed on the exact pinned canonical assets and on reintroduction of the forbidden artwork-pending placeholder.

Canonical artwork approval for GoreeCloud Home, Home Security, Containers, and Boot remains tracked in `GoreeCloud/goreecloud-branding-assets#16`.

## Glaze UI namespace-reset boundary

Current Stable is GLAZE UI V1.1 / 1.1.0. Several centralized packages still retain active pre-reset 2.x consumer bundles or locks and require controlled V1.1 migration rather than filename substitution. This remaining work is tracked in `GoreeCloud/goreecloud-static-websites#14`.

The source-consolidation state does not imply those design-system consumer migrations are complete or production-accepted.

## Preserved authority boundaries

- Manager's centralized package is the public informational site at `manage.goreecloud.com`; the authenticated Manager application remains outside this static-site source.
- Identity Center centralization does not transfer Identity backend/runtime authority.
- Mesh Center centralization does not transfer Mesh runtime authority.
- Privacy Shield, Wardveil Security, and Everkeep centralization does not transfer private runtime, service, contract, or platform-system authority.
- Generated `dist` directories are deployment artifacts/evidence, not central source authority.
- Design Center includes only the website and required public build inputs; broader Glaze UI authority remains in its own canonical system source.
- Labs contains public development information only; Home, Home Security, AI, Containers, Code, and Boot runtime authority remains in their respective repositories.

## Deployment and retirement gate

Every manifest entry still records `deployment_state: legacy-source`, including Labs.

No site may advance to `production-verified` or `legacy-source-retired` merely because its central source builds or passes CI. For each site, the remaining controlled sequence is:

1. change the Cloudflare Pages project repository/root/build references to the accepted central package;
2. update remaining deployment/configuration references that still identify the legacy source;
3. verify the exact deployed production revision and required public behavior/bytes against accepted central source;
4. retire the legacy static source only after production cutover, rollback/dependency, and preservation requirements pass; and
5. revalidate the resulting state.

No central-source validation entry by itself claims DNS, HTTPS, custom-domain, or production-traffic cutover.

## `goreecloud-website` deletion gate

`GoreeCloud/goreecloud-website` remains a protected transitional repository. It must not be deleted until every static website source or candidate still depending on it—including Labs—has been cut over to the centralized repository, exact production verification has passed, all required references and dependencies have been removed or redirected, legacy copies have been retired, and any applicable preservation/deletion gate has been satisfied.

After those gates are satisfied, the repository must not remain as a competing website authority.

## Next implementation tranche

1. Complete controlled Cloudflare Pages source cutover for the fourteen central packages, including Labs.
2. Verify exact production state after each cutover and update each manifest deployment state only with evidence.
3. Complete the GLAZE UI V1.1 consumer migrations tracked by issue #14.
4. Approve and publish missing canonical artwork tracked by branding-assets issue #16, then replace the intentionally suppressed Labs gaps with exact governed assets.
5. Retire legacy static copies only after their production and rollback/dependency gates pass.
6. Perform the final dependency and preservation review for `GoreeCloud/goreecloud-website`, then delete it only if every deletion precondition is verified.
