# GoreeCloud Projects — Suite Portfolio Reconciliation — 2026-09-10

## Decision

The Projects website portfolio projection is reconciled to the current authoritative GoreeCloud Suite registry: **45 verified products across 9 functional product groups**.

This is a public-directory source correction only. It does not establish production, Stable, platform-conformance, security, privacy, continuity, identity, or runtime acceptance for any listed product.

## Authority

The controlling portfolio-level record is the Google Drive document `Inventory — Suite Applications`, reconciled on September 10, 2026 as version `v0.9`, status `Active — Reconciled Suite Portfolio Registry`.

That record supersedes conflicting older 27-application/current-count statements and requires `suite.goreecloud.com` to present the reconciled 45-product portfolio or a newer verified successor. The Projects website is a broader project directory, so it projects that exact Suite membership while keeping additional GoreeCloud repository-level projects separate from the Suite count.

## Reconciled Projects behavior

`sites/projects/assets/suite-portfolio.js` contains the explicit publication projection of the 45-product Suite registry and nine functional groups. The runtime marks matching entries with Suite membership, adds current Suite products that were absent from the older Projects source, exposes a dedicated `Suite products` filter, and reports the authoritative count independently from the broader repository/project directory.

Projects-specific missing entries restored or added by this reconciliation are:

- GoreeCloud Index
- GoreeVault
- GoreeCloud Health
- GoreeCloud Reader
- GoreeCloud Router OS
- GoreeCloud Social
- GoreeCloud Home
- GoreeCloud Home Security

Additional GoreeCloud projects such as GoreeCloud GitHub Dashboard, GoreeCloud Firefox Extensions, GoreeCloud Autobiography, and the GoreeCloud Vault Server component may remain visible in Projects but are not counted as Suite products unless a later authoritative portfolio record changes that classification.

## Integral Platform Systems

The Projects summary and platform strip now represent the seven current Integral Platform Systems:

1. GoreeCloud Manager
2. GoreeCloud Identity
3. Glaze UI
4. Wardveil Security
5. Privacy Shield
6. Everkeep
7. GoreeCloud Mesh

Manager and Identity may also have user-facing Suite product surfaces without transferring or duplicating their platform authority.

## Branding

The canonical branding authority remains `GoreeCloud/goreecloud-branding-assets` and its `catalog.json` approval registry.

GoreeCloud Index now resolves to its approved `products/index/app-icon.svg` identity through the synchronized Suite publication derivative. Manager uses the approved Manager derivative locally in the Projects platform strip. Products without approved canonical artwork remain text-only; this reconciliation does not fabricate icons for Health, Reader, Router OS, Social, Home, or Home Security.

## GLAZE UI and verification

The Projects source remains targeted to **GLAZE UI V1.3 / 1.3.0 Stable** at exact canonical revision:

`8354308445da9ac35ced2b37a7f503a08a0aaf72`

The source validator, browser smoke test, mobile smoke test, and deployment verifier are reconciled to V1.3 and the current portfolio contract. Earlier browser/deployment verification assertions that still demanded Glaze UI 2.1 are superseded.

Source/CI success does not establish production deployment acceptance. `projects.goreecloud.com` remains independently deployment- and rendered-verification-gated according to the central website migration registry.

## Repository boundary

No new static website repository is introduced. The canonical static source remains `GoreeCloud/goreecloud-static-websites`, as required by GoreeCloud static-website governance.
