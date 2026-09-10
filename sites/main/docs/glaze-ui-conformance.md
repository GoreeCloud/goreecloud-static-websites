# GoreeCloud Main Website — GLAZE UI V1.3 Source Contract

## Current contract

- Target GLAZE UI version: **V1.3 / 1.3.0 Stable**
- Canonical design-system repository: `GoreeCloud/goreecloud-glaze-ui`
- Canonical source revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Stable web entrypoint: `glaze-v1.3.0.css`
- Entrypoint Git blob: `4c3ad293ba9196e2e5a32700b530ec67fd01cef6`
- Consumer source state: **source-migrated-rendered-acceptance-pending**
- Rendered, accessibility, deployment, and production acceptance: **Separate gates**

## Source and build model

The Main website authors its five public HTML surfaces directly against GLAZE UI V1.3. The exact Stable entrypoint is committed byte-identical to the canonical source for reviewability. The isolated build then resolves the entrypoint's complete relative CSS import graph from the exact pinned Glaze revision and vendors that dependency closure into the deployment artifact under `css/`.

The browser therefore receives only same-origin design-system assets. The build fails closed on an unexpected version, lifecycle, source revision, entrypoint name, entrypoint blob, unsafe dependency path, remote CSS import, or missing pinned dependency.

## Consumer adaptation

Main preserves its consumer-specific layout and interaction requirements while using the V1.3 design-system foundation. The consumer layer includes a 48px general interaction floor, a 56px coarse-pointer/Touch Assistance floor, visible keyboard focus, safe-area handling, bounded mobile navigation, reduced-motion behavior, reduced-transparency behavior, increased-contrast treatment, forced-colors operability, and print fallbacks.

Source validation proves that these adaptation contracts are present. It does not substitute for representative rendered review or accessibility acceptance.

## Public information boundary

The Main homepage identifies the thirteen authoritative GoreeCloud static website packages and the seven Integral Platform Systems. Repository totals are intentionally not published as live facts because repository creation is continuous; the connected GitHub organization is authoritative for the current inventory. The public repository page is a reviewed source-role guide rather than a complete count snapshot.

Public product direction uses first-party GoreeCloud identities. GoreeCloud Home and GoreeCloud Home Security replace upstream applications as product-level roadmap identities; any mature third-party technology used underneath them remains a bounded implementation detail.

## Authority boundary

GLAZE UI governs presentation and interaction. It does not grant privacy authorization, security protection, continuity state, identity authority, coordination authority, administrative authority, or application production acceptance. Privacy Shield, Wardveil Security, Everkeep, GoreeCloud Identity, GoreeCloud Mesh, GoreeCloud Manager, and each application retain their own applicable evidence and acceptance boundaries.

## Deployment boundary

This record establishes only the reviewed source/build target in `GoreeCloud/goreecloud-static-websites`. It does not prove that Cloudflare Pages is reading from the centralized repository, does not change DNS or TLS, and does not establish the exact deployed V1.3 revision at `www.goreecloud.com`.

Historical Glaze 1.x and 2.x production records remain exact-revision evidence for their time. They are not current consumer-target authority.
