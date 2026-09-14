# GoreeCloud Projects website

Canonical static source for `projects.goreecloud.com`.

## Repository contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/projects`
- Build command: `python3 build.py`
- Build output directory: `dist`
- Production branch target: `main`
- Custom domain: `projects.goreecloud.com`
- Cloudflare Pages project: `goreecloud-projects`
- Pages namespace: `goreecloud-projects.pages.dev`
- Migration source: `GoreeCloud/goreecloud-website` at `sites/projects`
- Reviewed legacy source tree: `2f7f5d096707bcc001e0e0ae46eb718c5ea3ab3f`

The Cloudflare project identity and Pages namespace are verified from legacy `GoreeCloud/goreecloud-website` deployment evidence. The desired central Pages source is `GoreeCloud/goreecloud-static-websites`, branch `main`, root `sites/projects`, build command `python3 build.py`, and output `dist`. Recording that target does not establish that the provider has already been reconnected or that production serves the reviewed central revision.

The publication artifact is deterministic and generated from the reviewed Projects source plus the exact pinned GLAZE UI Stable source. `_headers` defines the public security-header baseline. The site remains dependency-minimized and uses local browser runtime code.

## Portfolio authority

Projects is a broader project directory, not the authoritative definition of Suite membership. The authoritative portfolio registry is the current GoreeCloud `Inventory — Suite Applications` record in Google Drive, reconciled on September 10, 2026 to **45 verified Suite products across 9 functional product groups**.

`assets/suite-portfolio.js` is the publication projection of that verified portfolio for this website. It marks exactly those 45 product identities as Suite members, adds current products that are not present in the older Projects data file, and provides the dedicated **Suite products** filter. Additional GoreeCloud repository-level projects may remain visible in Projects without being counted as Suite products.

The current Suite projection includes later products such as GoreeCloud Health, Reader, Router OS, Social, Home, and Home Security; restores GoreeCloud Index to the directory; and uses **GoreeCloud Vault** as the canonical Suite credential-management product. Former product naming is retired and must not be published as current. **GoreeCloud Vault Server** remains the separately governed backend identity/project rather than a second Suite product. The canonical current Vault repository is `GoreeCloud/goreecloud-vault`.

The seven Integral Platform Systems are GoreeCloud Manager, GoreeCloud Identity, Glaze UI, Wardveil Security, Privacy Shield, Everkeep, and GoreeCloud Mesh. Manager and Identity may also have Suite product surfaces without transferring or duplicating their distinct platform authority. Quill, Waypoint, and Resonance remain application-centered capability identities rather than standalone Suite products unless later governing architecture changes that classification.

Portfolio membership does not establish Stable, production, security, privacy, recovery, platform-conformance, or deployment acceptance for a listed product. Detailed lifecycle truth remains controlled by each product's authoritative specification, repository, validation, and acceptance evidence.

## Current Glaze UI publication target

- Required publication version: **GLAZE UI V1.4 / `1.4.0` Stable**.
- Exact canonical Glaze revision: `84cb3db4884042f0fa25ed6d475a127fb110f596`.
- Exact Stable entrypoint: `glaze-v1.4.0.css`.
- Exact entrypoint Git blob: `d48a9bc317090d152799769271de0fb4325494c4`.
- Canonical Glaze repository: `GoreeCloud/goreecloud-glaze-ui`.
- Consumer lock: `glaze.lock.json`.
- Publication builder: `build.py`.
- Built-artifact validator: `validate_v14_artifact.py`.
- Built-artifact browser gate: `browser_v14_artifact_smoke.py`.
- Exact deployment verifier: `verify_v14_deployment.py`.
- Current consumer state: **source/build migrated; production deployment acceptance pending**.

Projects retains the reviewed V1.3 document and repository-local consumer adaptation as an inherited compatibility template. The builder projects that source deterministically into the current V1.4 publication identity, adds the exact V1.4 Stable stylesheet dependency closure, and preserves the V1.3 adaptation layer as an inherited consumer stylesheet rather than representing it as the active shared Glaze entrypoint. This follows the same controlled build-projection model used by the main GoreeCloud website.

GLAZE UI V1.4 being Official Stable and consumer-eligible does not grant Projects production conformance. The generated artifact must independently pass exact source/build integrity and rendered-browser validation, then the deployed custom domain must match that exact artifact before production acceptance can be recorded.

## Branding authority

- Canonical GoreeCloud branding repository: `GoreeCloud/goreecloud-branding-assets`.
- Canonical discovery and approval registry: `catalog.json` in that repository.
- Website `assets/suite/*.svg` files are synchronized publication derivatives of approved `products/*/app-icon.svg` sources; they are not independent branding authorities.
- Projects-local Manager, Glaze UI, Privacy Shield, Wardveil Security, Everkeep, GoreeCloud Mesh, and GoreeCloud Identity artwork are synchronized publication derivatives of approved branding-repository sources.
- GoreeCloud Index uses the approved canonical `products/index/app-icon.svg` identity through the synchronized Suite publication derivative.
- Wardveil Security uses the approved standalone **Sentinel Fold** emblem from `systems/wardveil-security/wardveil-security-icon.svg` as its primary visual mark. Wardveil wordmark and Security Center text are supporting identity, not part of the emblem.
- GoreeCloud Mesh uses the approved **Weave** mark from `systems/goreecloud-mesh/goreecloud-mesh-mark.svg`; Projects must not revert Mesh to the former text-only pending-artwork state while that canonical approval remains current.
- A project without approved catalog artwork remains text-only rather than inheriting the GoreeCloud platform logo or receiving a fabricated placeholder mark.
- Synchronized publication derivatives must remain byte-identical to their pinned canonical Git blobs.

## Production boundary

Source validation and successful V1.4 artifact generation do not themselves authorize production claims. Branch-preview and production verification must confirm that the deployed Projects surface matches the exact generated artifact. Platform artwork identifies the relevant system but does not establish technical runtime acceptance, protection, privacy, recovery, identity, management, or coordination state.

The canonical production verifier requires byte equality for the generated publication, a true reviewed 404 response, the complete committed security-header baseline, canonical HTTPS host behavior, and the exact V1.4 publication markers. Representative desktop/tablet/mobile browser acceptance remains a separate rendered evidence gate.

Cloudflare Pages source cutover and legacy-source retirement remain separate migration gates after central validation. Do not advance the manifest deployment state from `legacy-source` until the provider source/root/build/output contract is verified, the exact deployed artifact is accepted on `projects.goreecloud.com`, and rollback/legacy-source retirement requirements are satisfied.
