# GoreeCloud Main Website — GLAZE UI V1.4 Consumer Contract

## Current contract

- Target GLAZE UI version: **V1.4 / 1.4.0 Stable**
- Canonical design-system repository: `GoreeCloud/goreecloud-glaze-ui`
- Pinned Stable release revision: `84cb3db4884042f0fa25ed6d475a127fb110f596`
- Stable web entrypoint: `glaze-v1.4.0.css`
- Entrypoint Git blob: `d48a9bc317090d152799769271de0fb4325494c4`
- Consumer build state: **build-migrated-rendered-acceptance-pending**
- Rendered, accessibility, deployment, and production acceptance: **Separate gates**

The authoritative Glaze lifecycle registry identifies GLAZE UI V1.4 / `1.4.0` as the current Official Stable and consumer-eligible release. V1.4.1 is a separate follow-up hardening/qualification track and is not substituted for the current Stable consumer target.

## Source and build model

Main is built against the exact V1.4 Stable web entrypoint and its complete relative CSS import closure. The V1.4 entrypoint is committed byte-identical to the pinned Stable release for reviewability. The isolated build resolves the entrypoint's same-origin dependency graph from the exact pinned Glaze revision and writes that closure into the deployment artifact under `css/`.

During this migration, the reviewed HTML authoring templates are deterministically projected to the V1.4 runtime contract by `scripts/glaze_v1_4.py`. The build rewrites the version, source-revision, consumer-state, and Stable stylesheet markers; adds the Main V1.4 consumer stylesheet; and marks the site header for the V1.4 adaptive-optical CSS treatment. The deployed artifact must contain only V1.4 current markers. The build validator byte-compares that transformed artifact against the reviewed transformation contract.

The browser receives only same-origin design-system and consumer assets. The build fails closed on an unexpected version, lifecycle, source revision, entrypoint name, entrypoint blob, unsafe dependency path, remote CSS import, or missing pinned dependency.

## V1.4 runtime boundary

Main adopts the Stable V1.4 CSS entrypoint. The optional V1.4 JavaScript Optical Engine is **not required by this website migration** and is not loaded by the public site. This avoids adding any new context or capability collection merely to satisfy a version label. Presentation adaptation remains CSS/local-state based, and PostHog telemetry remains governed by its independent consent-first privacy contract.

## Consumer adaptation and navigation redesign

The V1.4 consumer layer preserves Main's accessibility and interaction requirements while redesigning the global header/navigation around a single aligned content grid. Desktop navigation uses a bounded Glaze navigation capsule with the brand, navigation, and appearance controls on one optical centerline. Tablet and compact layouts switch to the existing explicit menu control before the desktop navigation becomes crowded. The consent surface is aligned to the same content grid so it no longer behaves like a detached full-width banner.

The consumer layer retains a 48px general interaction floor, coarse-pointer/Touch Assistance behavior inherited from the established Main adaptation, visible keyboard focus, safe-area handling, bounded mobile navigation, reduced-motion behavior, reduced-transparency behavior, increased-contrast treatment, forced-colors operability, and print fallbacks.

Source/build validation proves that these contracts are present. It does not substitute for representative rendered review or accessibility acceptance.

## Public information boundary

The Main homepage identifies the authoritative GoreeCloud public website surfaces and the seven Integral Platform Systems. Repository totals are intentionally not treated as live authority because repository creation is continuous; the connected GitHub organization remains authoritative for the current inventory.

Public product direction uses first-party GoreeCloud identities. Mature third-party technology used underneath GoreeCloud products remains a bounded implementation detail unless an authoritative product record says otherwise.

## Authority boundary

GLAZE UI governs presentation and interaction. It does not grant privacy authorization, security protection, continuity state, identity authority, coordination authority, administrative authority, or application production acceptance. Privacy Shield, Wardveil Security, Everkeep, GoreeCloud Identity, GoreeCloud Mesh, GoreeCloud Manager, and each application retain their own applicable evidence and acceptance boundaries.

## Deployment boundary

This record establishes the reviewed V1.4 source/build target in `GoreeCloud/goreecloud-static-websites`. It does not by itself prove the exact deployed V1.4 revision at `www.goreecloud.com` or mark the Main website Stable. Exact Cloudflare deployment, responsive rendering, accessibility behavior, navigation behavior, and production PostHog consent behavior remain independent verification gates.

Historical Glaze releases remain exact-revision evidence for their time. They are not current consumer-target authority.
