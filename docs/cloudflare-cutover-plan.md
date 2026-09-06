# Cloudflare Pages Central-Source Cutover Plan

**Prepared:** 2026-09-06  
**Canonical repository:** `GoreeCloud/goreecloud-static-websites`  
**Accepted source/discovery baseline:** `c8e5629f323de850b8d345786713056ff0dc0ff1`  
**Current deployment state:** all 13 manifest entries remain `legacy-source`

## Purpose

This document converts the accepted central source/build contracts into an exact Cloudflare Pages cutover preflight. It does **not** claim that any Cloudflare setting has been changed.

The desired Git-side values below are derived from the accepted central packages and their validation/build tooling. The live Cloudflare project name, current connected repository, production branch, root directory, build command, output directory, environment variables, deploy hooks, preview settings, custom-domain attachment, and DNS/HTTPS state must be read from authenticated Cloudflare controls immediately before each change. Never overwrite a live value merely because an older document records a different value.

## Common target

For every migrated standalone static website:

- target repository: `GoreeCloud/goreecloud-static-websites`
- production branch: `main`
- source revision for the first controlled cutover: an explicitly recorded accepted `main` revision at cutover time
- deployment acceptance: exact-revision and evidence-backed
- rollback: preserve the previous verified Pages source/configuration and legacy repository source until central production verification passes

## Desired central package matrix

| Site | Custom domain | Pages root directory | Build command from that root | Build output directory |
| --- | --- | --- | --- | --- |
| Main | `www.goreecloud.com` | `sites/main` | `python scripts/build_public_site.py` | `dist` |
| Projects | `projects.goreecloud.com` | `sites/projects` | none | `.` |
| Roadmap | `roadmap.goreecloud.com` | `sites/roadmap` | none | `.` |
| Blog | `blog.goreecloud.com` | `sites/blog` | none | `.` |
| Archive | `archive.goreecloud.com` | `sites/archive` | none | `.` |
| Suite | `suite.goreecloud.com` | `sites/suite` | `python scripts/build_public_site.py` | `dist` |
| Design Center | `design.goreecloud.com` | `sites/design` | `python website/build.py` | `website/dist` |
| Privacy Center | `privacy.goreecloud.com` | `sites/privacy` | `python website/build.py` | `website/dist` |
| Security Center | `security.goreecloud.com` | `sites/security` | `python website/build.py` | `website/dist` |
| Continuity Center | `everkeep.goreecloud.com` | `sites/everkeep` | `python scripts/build_public_site.py` | `dist` |
| Identity Center | `identity.goreecloud.com` | `sites/identity` | none | `.` |
| Manager public site | `manage.goreecloud.com` | `sites/manager` | `python scripts/build_public_site.py` | `dist` |
| Mesh Center | `mesh.goreecloud.com` | `sites/mesh` | `python scripts/build_public_site.py` | `dist` |

`none` means the package is already the publication artifact and should not be wrapped in an unrelated generated-output step. A Cloudflare UI may represent the output directory for a direct-static project as blank rather than `.`; preserve the provider-supported representation that publishes the selected root itself.

## Source of each build contract

### Main

Central validation executes:

```bash
python sites/main/scripts/build_public_site.py
python sites/main/scripts/validate_build_artifact.py
```

The builder writes `sites/main/dist`. With Pages root set to `sites/main`, the corresponding build command is `python scripts/build_public_site.py` and output is `dist`.

### Projects, Roadmap, Blog, and Archive

These packages are direct static roots. Their accepted central workflows validate the source package in place rather than producing a separate deployment artifact. Pages should publish the selected `sites/<id>` root directly.

### Suite

The accepted package builder is `sites/suite/scripts/build_public_site.py`, which creates `sites/suite/dist` from an explicit allowlist. With Pages root `sites/suite`, use `python scripts/build_public_site.py` and output `dist`.

### Design Center

`sites/design/website/build.py` treats `sites/design` as its package root and creates `sites/design/website/dist`. With Pages root `sites/design`, use `python website/build.py` and output `website/dist`.

### Privacy Center

The accepted central workflow runs `python sites/privacy/website/build.py` and validates `sites/privacy/website/dist`. With Pages root `sites/privacy`, use `python website/build.py` and output `website/dist`.

### Security Center

The accepted central workflow runs `python sites/security/website/build.py` and validates `sites/security/website/dist`. With Pages root `sites/security`, use `python website/build.py` and output `website/dist`.

### Everkeep Continuity Center

The accepted central workflow runs `python sites/everkeep/scripts/build_public_site.py` and validates `sites/everkeep/dist`. With Pages root `sites/everkeep`, use `python scripts/build_public_site.py` and output `dist`.

### Identity Center

The accepted central package is the direct static publication boundary under `sites/identity`; its workflow validates the required HTML, JavaScript, CSS, headers, robots, sitemap, and identity asset in place. No build step is required.

### Manager public site

The accepted builder is `sites/manager/scripts/build_public_site.py`, which creates `sites/manager/dist`. With Pages root `sites/manager`, use `python scripts/build_public_site.py` and output `dist`.

The package has a pinned Glaze UI 2.2.0 Stable contract. Its builder can use a local `GLAZE_UI_SOURCE` when supplied by CI or fetch the pinned source when that environment value is absent. Live Pages environment settings must be inspected before deciding whether a Cloudflare build environment override is necessary.

### Mesh Center

The accepted builder is `sites/mesh/scripts/build_public_site.py`, which creates `sites/mesh/dist`. With Pages root `sites/mesh`, use `python scripts/build_public_site.py` and output `dist`.

Mesh also uses a pinned Glaze UI 2.2.0 Stable contract and supports `GLAZE_UI_SOURCE` or the builder's pinned-source retrieval path. Do not invent or copy an environment variable into Cloudflare without first reading the live project configuration.

## Required live Cloudflare readback before each cutover

For each Pages project, capture and preserve the pre-change values for:

1. Pages project name and account identifier.
2. Connected Git provider and repository.
3. Production branch.
4. Root directory.
5. Build command.
6. Build output directory.
7. Build-system/runtime version settings that can affect deterministic output.
8. Production and preview environment variables and bindings.
9. Deploy hooks or external automation that assumes the legacy repository.
10. Preview-branch behavior.
11. Custom domains attached to the project.
12. Current most recent successful production deployment identifier, source revision, and deployment URL.
13. DNS record used by the custom domain and its proxy state where exposed.
14. Current HTTPS/certificate state.

Store only non-secret configuration and evidence. Do not copy secret values into Git, Drive, chat, logs, screenshots, or migration notes.

## Controlled cutover sequence per site

1. **Freeze the candidate.** Record the exact accepted central `main` SHA to deploy. Re-run the applicable source/build CI if site source has changed since its last accepted validation.
2. **Read current Pages state.** Capture the live settings listed above before changing anything.
3. **Check hidden dependencies.** Identify deploy hooks, environment variables, external status checks, or downstream documentation that refers to the legacy repository/path.
4. **Change only the source contract.** Point the existing Pages project to `GoreeCloud/goreecloud-static-websites`, `main`, and the root/build/output values in this plan, unless authenticated live readback proves a provider-specific adjustment is required.
5. **Do not alter the custom domain merely to change source.** Preserve the existing domain attachment unless Cloudflare requires a controlled reattachment and the reason is documented.
6. **Wait for the exact central revision deployment to complete.** Record its provider deployment ID and deployed Git SHA.
7. **Verify the Pages preview/deployment URL first** where available, then the custom domain.
8. **Verify HTTPS and the intended DNS path.** Source cutover must not silently move the domain to an unintended project or origin.
9. **Verify public behavior.** At minimum: expected status code, canonical URL, security headers/CSP, 404 behavior, required assets, JavaScript syntax/runtime behavior where applicable, responsive-critical behavior, indexing files, and cross-site navigation.
10. **Run exact site-specific remote/integrity verification** where the package already supplies it. Do not replace an existing stronger acceptance contract with a weaker smoke check.
11. **Record production acceptance** with the exact central SHA and provider deployment evidence only after the custom domain is verified.
12. **Advance only that site's deployment state.** Do not bulk-promote unrelated sites.
13. **Update downstream references** that still describe the old repository as the active deployment source.
14. **Retain the legacy source for rollback** until the site's retirement condition and recovery/dependency requirements are satisfied.
15. **Retire the old copy only after the accepted cutover is stable and independently recorded.**

## Suggested order

Use small, individually reversible changes rather than changing all projects simultaneously:

1. Archive
2. Blog
3. Roadmap
4. Projects
5. Identity Center
6. Suite
7. Design Center
8. Manager public site
9. Mesh Center
10. Privacy Center
11. Security Center
12. Everkeep Continuity Center
13. Main

This ordering is operational guidance, not a new authority hierarchy. It starts with simpler direct-static sites, proceeds through deterministic builders, places private-system public surfaces later, and leaves the primary public domain until the migration procedure has been proven repeatedly.

## Rollback rule

If the central-source deployment fails validation or materially changes public behavior unexpectedly:

- stop advancement for that site;
- preserve the failed deployment evidence;
- restore the previously verified Pages source/configuration without deleting central source;
- verify the rollback on the custom domain;
- diagnose and fix the central package through a new exact candidate;
- repeat the controlled cutover only after the new candidate is accepted.

A rollback does not invalidate the central repository's source-authority rule. It means the legacy deployment copy remains temporarily required while the deployment defect is corrected.

## State transition rule

The manifest currently separates `migration_state` from `deployment_state` intentionally.

Do not change `deployment_state: legacy-source` merely because this plan exists. A site may advance only after an authenticated Cloudflare source cutover and exact custom-domain production verification establish the next state with evidence.

Do not mark a legacy source retired and do not delete `GoreeCloud/goreecloud-website` until all applicable project-level and repository-deletion gates in the governing Drive records are satisfied.

## Current blocker

At preparation time, the connected ChatGPT tool environment exposes GitHub and Google Drive controls but no authenticated Cloudflare Pages account-management integration. The plugin directory was re-checked on 2026-09-06 and did not expose Cloudflare Pages management. Therefore the live Cloudflare readback and changes in this plan remain an external authenticated operation; no substitute hosting provider or guessed Cloudflare setting is authorized.
