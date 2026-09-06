# Static Website Consolidation Status

**Canonical target:** `GoreeCloud/goreecloud-static-websites`  
**Reviewed:** 2026-09-06  
**Accepted central revision:** `4bfee305550e2e43991188816f4fc80c16ccfad5`  
**Overall state:** Source consolidation and current repository-discovery gates are complete for the thirteen identified standalone static website packages. Deployment cutover, exact production verification, legacy-source retirement, and final deletion remain open.

## Mandatory consolidation rule

Every GoreeCloud standalone static public website must be stored, maintained, and referenced from `GoreeCloud/goreecloud-static-websites` unless an explicit governed architectural exception is approved.

Application frontends, authenticated product UIs, extension pages, generated artifacts, test fixtures, internal/debug pages, demos, reference pages, and inherited upstream documentation are not reclassified as standalone websites merely because they contain browser-renderable files.

No legacy repository may remain a second source authority after its site's deployment and retirement gates are complete. Build configuration, deployment configuration, documentation, automation, and references must ultimately point to the corresponding centralized package.

## Current source-migration state

All thirteen current standalone public static website packages are present in the central repository and are `validated-in-central-repo`.

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

The migration state and deployment state are intentionally separate. A validated central source package does not prove that Cloudflare Pages or production traffic uses that package.

## Accepted source-migration evidence

The source consolidation was completed in bounded, reviewable tranches with exact-candidate validation:

- Roadmap — PR #2; source-copy evidence `7b416ce7d280e7bf91bf3c973ab0bd4831f3341b`; accepted merge `2982b1b77272698bd4ac48e049475af45e98a61c`.
- Archive — PR #3; source-copy evidence `f48a5cc287436972f1a215878530ae0ac40e44e0`; accepted merge `4997bf74ee3e2bf2bc5f379638f4ef5e169645a3`.
- Blog — PR #4; source-copy evidence `9f3d3a2adf47ccb890847a61a3d253cafff563b6`; accepted merge `70504569c81362f688edee889b40614ef30f702a`.
- Projects — PR #5; source-copy evidence `c353b1c14aecf081646b3fab5337e646e59780a6`; accepted merge `d66e4746e9f23a5edd43f8b5c2ebad01a2a1dc9d`.
- Manager — PR #6; central-copy evidence `4fcbe7ce370ecf765a393a41cdfc65ef3f403676`; accepted merge `075fa1817bd75b7cf1a9dc175c1b4524c745df77`.
- Design, Identity, Mesh, and Suite — PR #7; bounded source-copy evidence `f9be2cf9b3e02c1b56a2b6ea00fc958572db589d`; accepted merge `b8817cea54cad3cd03c040409ec8b65c92aeffdc`.
- Main — PR #8; immutable legacy source revision `18f5276d21b8eb3b55adc18e00e88aa11b6edfd8`; central source-copy evidence `bb95964e0a1f28c7d5f1eae1dc111c43daea1317`; final validated candidate `c945108b7f5dd59ce69ce71264a47d8a22a72829`; accepted merge `553e42f59573f8cacc5e6ab8bb2223d6b7575bb3`.
- Privacy, Wardveil Security, and Everkeep — superseding PR #10 after Main changed the shared registry; exact final candidate `ba3b254f624e13d886a9cdbea6ae64b5f515addd`; accepted merge `4bfee305550e2e43991188816f4fc80c16ccfad5`.

The accepted `main` revision `4bfee305550e2e43991188816f4fc80c16ccfad5` passed the repository migration-registry workflow and the dedicated Privacy/Security/Everkeep post-merge workflow.

## Current inventory-discovery result

Repository-wide discovery is no longer an open source-migration gate for the current repository inventory.

The discovery evidence scanned 66 public, non-archived GoreeCloud repositories using recursive Git trees. Every signature-bearing candidate repository was then classified. The authenticated GitHub installation inventory was also reviewed to cover the accessible private GoreeCloud repositories.

The review found no additional standalone GoreeCloud public static website package beyond the thirteen manifest entries. Browser-extension pages, application UIs, generated `dist` output, validation fixtures, demos, design references, internal service pages, OpenAPI pages, portability templates, and inherited upstream documentation were excluded from standalone-site authority.

See `docs/static-site-discovery-review.md` for the classification record. A future repository or a future distinct public static website remains automatically in scope for centralization.

## Preserved authority boundaries

- Manager's centralized package is the public informational site at `manage.goreecloud.com`; the authenticated Manager application remains in `GoreeCloud/goreecloud-manager`.
- Identity Center is centralized from `identity-center-site`; the inherited authentik Docusaurus documentation and Identity backend/runtime remain outside static-site authority.
- Mesh Center is centralized with only the public build/validation inputs needed to reproduce it; Mesh runtime code remains in the Mesh repository.
- Privacy Shield, Wardveil Security, and Everkeep were migrated as bounded public packages from private repositories. Their private runtime, service, contract, and security/continuity implementation authority was not copied into this public repository.
- Generated `dist` directories are deployment artifacts/evidence, not central source authority.
- Design Center includes the exact Glaze UI build inputs required by its public site without transferring the design system's broader authority into this repository.

## Deployment and retirement gate

Every manifest entry still records `deployment_state: legacy-source`.

No site may advance to production-verified or legacy-source-retired merely because its central source builds or passes CI. For each site, the remaining controlled sequence is:

1. change the Cloudflare Pages project repository/root/build references to the accepted central package;
2. update any remaining deployment/configuration references that still identify the legacy source;
3. verify the exact deployed production revision and required public behavior/bytes against the accepted central source;
4. retire the legacy static source only after the production cutover is proven and rollback/dependency requirements permit retirement; and
5. revalidate the resulting state.

No Cloudflare Pages, DNS, HTTPS, or production-traffic change is claimed by the source migration work recorded here.

## `goreecloud-website` deletion gate

`GoreeCloud/goreecloud-website` remains a protected transitional repository.

It must not be deleted until all five sites historically sourced there have been cut over to the centralized repository, exact production verification has passed, all required references and dependencies have been removed or redirected, legacy copies have been retired, and any applicable preservation/deletion gate has been satisfied.

After those gates are satisfied, the repository must not remain as a competing website authority.

## Next implementation tranche

1. Obtain an authenticated Cloudflare Pages management path capable of changing project repository/root/build settings.
2. Cut over the thirteen site deployments in controlled, individually verifiable steps using their central paths.
3. Verify exact production state after each cutover and record the accepted deployed revision.
4. Update remaining deployment/reference documentation after each accepted cutover.
5. Retire legacy static copies only after their individual production and rollback/dependency gates pass.
6. Perform the final dependency and preservation review for `GoreeCloud/goreecloud-website`, then delete it only if every deletion precondition is verified.
