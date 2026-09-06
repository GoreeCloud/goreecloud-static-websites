# Static Website Consolidation Status

**Canonical target:** `GoreeCloud/goreecloud-static-websites`  
**Reviewed:** 2026-09-05  
**Overall state:** Migration in progress; no deployment cutover or legacy deletion is claimed.

## Mandatory consolidation rule

Every GoreeCloud static website MUST be stored, maintained, and referenced from `GoreeCloud/goreecloud-static-websites`.

This includes the main GoreeCloud website, Wardveil Security website, GoreeCloud Identity website, GoreeCloud Privacy website, GoreeCloud Roadmap website, GoreeCloud Archive website, and every other static website currently stored in a standalone website repository or embedded inside an application, service, Platform System, design-system, or historical repository.

No legacy repository may remain a second authoritative source after its site has completed migration. Build configuration, deployment configuration, documentation, automation, and repository references must be updated to point to the corresponding centralized site package.

All future GoreeCloud static websites must also be created in this repository unless an explicit architectural exception is documented.

## Confirmed inventory

The first repository audit identified thirteen static public-site source packages that must be consolidated:

| Site | Canonical hostname | Current source | Current path | Central target |
| --- | --- | --- | --- | --- |
| Main | `www.goreecloud.com` | `GoreeCloud/goreecloud-website` | `/` | `sites/main` |
| Projects | `projects.goreecloud.com` | `GoreeCloud/goreecloud-website` | `sites/projects` | `sites/projects` |
| Roadmap | `roadmap.goreecloud.com` | `GoreeCloud/goreecloud-website` | `sites/roadmap` | `sites/roadmap` |
| Blog | `blog.goreecloud.com` | `GoreeCloud/goreecloud-website` | `sites/blog` | `sites/blog` |
| Archive | `archive.goreecloud.com` | `GoreeCloud/goreecloud-website` | `sites/archive` | `sites/archive` |
| Suite | `suite.goreecloud.com` | `GoreeCloud/goreecloud-suite` | `/` website package | `sites/suite` |
| Design | `design.goreecloud.com` | `GoreeCloud/goreecloud-glaze-ui` | `website` | `sites/design` |
| Privacy | `privacy.goreecloud.com` | `GoreeCloud/goreecloud-privacy-shield` | `website` | `sites/privacy` |
| Security / Wardveil | `security.goreecloud.com` | `GoreeCloud/goreecloud-wardveil-security` | `website` | `sites/security` |
| Everkeep | `everkeep.goreecloud.com` | `GoreeCloud/goreecloud-everkeep` | `website` plus site-specific build resources | `sites/everkeep` |
| Identity | `identity.goreecloud.com` | `GoreeCloud/goreecloud-identity` | `identity-center-site` | `sites/identity` |
| Manager | `manage.goreecloud.com` | `GoreeCloud/goreecloud-manager` | `website` | `sites/manager` |
| Mesh | `mesh.goreecloud.com` | `GoreeCloud/goreecloud-mesh` | `website` plus site-specific build resources | `sites/mesh` |

This is a verified initial inventory, not a declaration that no additional static source exists. Repository-wide discovery remains a migration gate. Any additional static website discovered later is automatically in scope for consolidation.

## Important boundaries found during inventory

- Manager's public informational site is `manage.goreecloud.com`. The authenticated private Manager application at `manager.goreecloud.com` is not static-site migration scope.
- Identity public source is isolated under `identity-center-site`; Identity backend/authenticated runtime code must remain outside this repository.
- Mesh's visible `website/` subtree is not self-contained: its accepted build checks out pinned Glaze UI 2.2.0 source and uses `scripts/build_public_site.py`, `scripts/validate_public_site.py`, and `scripts/verify_public_deployment.py`. Those website-specific build inputs must be reconciled before source-copy status can advance.
- Privacy Shield and Wardveil Security track generated `website/dist` output today. Generated output is deployment evidence/artifact, not the new canonical source; central migration must preserve the reproducible source/build contract instead of simply copying `dist`.
- Everkeep's website build and validation scripts live outside `website/`, so the site must be migrated as a bounded package rather than a blind subtree copy.
- The Glaze UI Design site consumes design-system assets outside its small `website/` presentation subtree; those dependencies require explicit provenance when centralized.

## Migration policy

A site advances only when all requirements for the next state are satisfied. In particular, `source-copied` requires a reproducible central package, not just HTML/CSS files. `production-verified` requires deployment evidence against the central accepted revision. `legacy-source-retired` requires old source/reference cleanup after cutover.

`GoreeCloud/goreecloud-website` remains in service only as a migration source. It MUST be deleted after every static site across the GoreeCloud ecosystem has completed source migration, validation, deployment/reference cutover, required production verification, and legacy-source retirement, and after no required dependency remains on that repository.

The repository must not be deleted prematurely. Conversely, after all retirement gates are satisfied, it must not be retained as a competing website authority.

## Next implementation tranche

1. Establish repository-level manifest validation and site-boundary checks.
2. Continue repository-wide discovery so every static website is represented in the central manifest.
3. Migrate self-contained/reproducible site packages in small reviewable tranches.
4. Port each site's validation/build contract into `sites/<id>/` or shared repository tooling without changing its public behavior.
5. Validate candidate source centrally.
6. Change Cloudflare Pages source/root and every repository reference only after central validation is accepted.
7. Verify exact deployed production bytes/behavior where the legacy site already has a production acceptance contract.
8. Remove legacy static source and obsolete references only after successful cutover.
9. Delete `GoreeCloud/goreecloud-website` after all ecosystem-wide migration and retirement gates are complete.
