# Static Website Consolidation Status

**Canonical target:** `GoreeCloud/goreecloud-static-websites`  
**Reviewed:** 2026-09-06  
**Accepted central revision:** `c8e5629f323de850b8d345786713056ff0dc0ff1` for the prior thirteen-site checkpoint  
**Overall state:** The thirteen sites in the completed discovery checkpoint remain `validated-in-central-repo`. Labs was created afterward in the Website rebuild candidate, has now been identified as the fourteenth standalone static public site, and is being migrated here with GoreeCloud Boot included. Deployment cutover, exact production verification, legacy-source retirement, and final Website deletion remain open.

## Mandatory consolidation rule

Every GoreeCloud standalone static public website must be stored, maintained, and referenced from `GoreeCloud/goreecloud-static-websites` unless an explicit governed architectural exception is approved.

Application frontends, authenticated product UIs, extension pages, generated artifacts, test fixtures, internal/debug pages, demos, reference pages, and inherited upstream documentation are not reclassified as standalone websites merely because they contain browser-renderable files.

No legacy repository may remain a second source authority after its site's deployment and retirement gates are complete. Build configuration, deployment configuration, documentation, automation, and references must ultimately point to the corresponding centralized package.

## Current source-migration state

The thirteen previously identified standalone public static website packages are `validated-in-central-repo`. Labs is newly `source-copied` in this migration candidate and must pass its exact central validation before that state can advance.

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
| Labs product center | `labs.goreecloud.com` | `sites/labs` | `source-copied` | `legacy-source` |

The migration state and deployment state are intentionally separate. A validated central source package does not prove that Cloudflare Pages or production traffic uses that package.

## Labs reconciliation — September 6, 2026

The earlier repository-discovery pass correctly described the repository inventory available at that checkpoint, but Labs was subsequently introduced in `GoreeCloud/goreecloud-website` draft PR #116 and therefore was not part of the original thirteen-site manifest.

Labs is a standalone static public site and is automatically in scope for the centralization directive. Its legacy source was captured from `sites/labs` tree `60cf6dbefa274a19bbb7bf3ae75638ac6d20e1c7` at Website candidate `7d9b03c90d3ea2c74dacd2f03430a86dd93a3ba6`. The central package copies the site plus the exact shared Website CSS, JavaScript, logo, and pinned GLAZE helper required to reproduce the isolated artifact without retaining a source dependency on the transitional repository.

The same migration candidate corrects the Labs inventory from five to six products by adding GoreeCloud Boot. Boot remains explicitly Development: the public card describes the validated read-only discovery, safety/revalidation, partition-planning, GPT metadata, catalog-validation, and development image-tooling foundation while preserving the gates around physical writes, filesystems, boot runtime, bootable releases, broader storage qualification, and Stable/production acceptance.

## Preserved authority boundaries

- Manager's centralized package is the public informational site at `manage.goreecloud.com`; the authenticated Manager application remains in `GoreeCloud/goreecloud-manager`.
- Identity Center is centralized from `identity-center-site`; the inherited authentik Docusaurus documentation and Identity backend/runtime remain outside static-site authority.
- Mesh Center is centralized with only the public build/validation inputs needed to reproduce it; Mesh runtime code remains in the Mesh repository.
- Privacy Shield, Wardveil Security, and Everkeep were migrated as bounded public packages from private repositories. Their private runtime, service, contract, and security/continuity implementation authority was not copied into this public repository.
- Generated `dist` directories are deployment artifacts/evidence, not central source authority.
- Design Center includes the exact Glaze UI build inputs required by its public site without transferring the design system's broader authority into this repository.
- Labs contains public development information only; GoreeCloud Home, Home Security, AI, Containers, Code, and Boot runtime authority remains in their respective repositories.

## Deployment and retirement gate

Every manifest entry still records `deployment_state: legacy-source`, including Labs.

No site may advance to production-verified or legacy-source-retired merely because its central source builds or passes CI. For each site, the remaining controlled sequence is:

1. change the Cloudflare Pages project repository/root/build references to the accepted central package;
2. update any remaining deployment/configuration references that still identify the legacy source;
3. verify the exact deployed production revision and required public behavior/bytes against the accepted central source;
4. retire the legacy static source only after the production cutover is proven and rollback/dependency requirements permit retirement; and
5. revalidate the resulting state.

No Cloudflare Pages, DNS, HTTPS, or production-traffic change is claimed by the source migration work recorded here.

## `goreecloud-website` deletion gate

`GoreeCloud/goreecloud-website` remains a protected transitional repository.

It must not be deleted until every static website source or candidate still depending on it—including Labs—has been cut over to the centralized repository, exact production verification has passed, all required references and dependencies have been removed or redirected, legacy copies have been retired, and any applicable preservation/deletion gate has been satisfied.

After those gates are satisfied, the repository must not remain as a competing website authority.

## Next implementation tranche

1. Complete exact central validation for the Labs package and advance its manifest state only with evidence.
2. Obtain an authenticated Cloudflare Pages management path capable of changing project repository/root/build settings.
3. Cut over the site deployments in controlled, individually verifiable steps using their central paths, including Labs.
4. Verify exact production state after each cutover and record the accepted deployed revision.
5. Update remaining deployment/reference documentation after each accepted cutover.
6. Retire legacy static copies only after their individual production and rollback/dependency gates pass.
7. Perform the final dependency and preservation review for `GoreeCloud/goreecloud-website`, then delete it only if every deletion precondition is verified.
