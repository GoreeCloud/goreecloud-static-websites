# GoreeCloud Projects website

Canonical static source for `projects.goreecloud.com`.

## Repository contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/projects`
- Build command: none
- Build output directory: `.`
- Production branch target: `main`
- Custom domain: `projects.goreecloud.com`
- Cloudflare Pages project: `goreecloud-projects`
- Pages namespace: `goreecloud-projects.pages.dev`
- Migration source: `GoreeCloud/goreecloud-website` at `sites/projects`
- Reviewed legacy source tree: `2f7f5d096707bcc001e0e0ae46eb718c5ea3ab3f`

The Cloudflare project identity and Pages namespace are verified from legacy `GoreeCloud/goreecloud-website` deployment evidence. The desired central Pages source is `GoreeCloud/goreecloud-static-websites`, branch `main`, root `sites/projects`, with no build command and output `.`. Recording that target does not establish that the provider has already been reconnected or that production serves the reviewed central revision.

The site is static, dependency-free, tracking-free, and uses only local browser runtime code. `_headers` defines the public security-header baseline.

## Portfolio authority

Projects is a broader project directory, not the authoritative definition of Suite membership. The authoritative portfolio registry is the current GoreeCloud `Inventory — Suite Applications` record in Google Drive, reconciled on September 10, 2026 to **45 verified Suite products across 9 functional product groups**.

`assets/suite-portfolio.js` is the publication projection of that verified portfolio for this website. It marks exactly those 45 product identities as Suite members, adds current products that are not present in the older Projects data file, and provides the dedicated **Suite products** filter. Additional GoreeCloud repository-level projects may remain visible in Projects without being counted as Suite products.

The current Suite projection includes later products such as GoreeCloud Health, Reader, Router OS, Social, Home, and Home Security; restores GoreeCloud Index to the directory; and presents GoreeVault as the Suite-level credential-management product while GoreeCloud Vault Server remains a separately governed server component/project.

The seven Integral Platform Systems are GoreeCloud Manager, GoreeCloud Identity, Glaze UI, Wardveil Security, Privacy Shield, Everkeep, and GoreeCloud Mesh. Manager and Identity may also have Suite product surfaces without transferring or duplicating their distinct platform authority. Quill, Waypoint, and Resonance remain application-centered capability identities rather than standalone Suite products unless later governing architecture changes that classification.

Portfolio membership does not establish Stable, production, security, privacy, recovery, platform-conformance, or deployment acceptance for a listed product. Detailed lifecycle truth remains controlled by each product's authoritative specification, repository, validation, and acceptance evidence.

## Current Glaze UI consumer target

- Required design-system version: **GLAZE UI V1.3 / `1.3.0`**.
- Exact canonical Glaze revision used for this source migration: `8354308445da9ac35ced2b37a7f503a08a0aaf72`.
- Canonical Glaze repository: `GoreeCloud/goreecloud-glaze-ui`.
- Projects consumer layer: `assets/glaze-v1.3-consumer.css`.
- Current consumer state: **source migrated; rendered/browser, accessibility, performance, rollback, and production acceptance pending**.

GLAZE UI V1.3 being Official Stable and consumer-eligible does not grant Projects conformance. This repository must independently validate the actual Projects surface and bind acceptance to the exact consumer revision before any production-complete V1.3 claim is made.

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

Source validation does not itself authorize production claims. Branch-preview and production verification must confirm that the deployed Projects surface matches the reviewed source. Platform artwork identifies the relevant system but does not establish technical runtime acceptance, protection, privacy, recovery, identity, management, or coordination state.

Cloudflare Pages source cutover and legacy-source retirement remain separate migration gates after central validation.
