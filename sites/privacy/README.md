# GoreeCloud Privacy Shield Static Website

Canonical source repository: `GoreeCloud/goreecloud-static-websites`

- Site root: `sites/privacy`
- Canonical domain: `privacy.goreecloud.com`
- Legacy source repository: `GoreeCloud/goreecloud-privacy-shield`
- Reviewed legacy source commit: `345b4bd42aaed09afb0e2384c421aab8661f1d5c`
- Exact legacy website tree: `467d95f979a18e13b83ffa7dde6a68165720ebad`
- Canonical GLAZE UI release: `1.3.0` Stable
- Exact GLAZE UI source revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Exact GLAZE UI entrypoint blob: `4c3ad293ba9196e2e5a32700b530ec67fd01cef6`
- Verified Privacy Center production revision: `80379f6962a5ded6c01317542941a2c55aedd922`
- Current accepted Privacy Center subtree tree: `50d11f2ba52f7009ee8d1b08973ad1f4d75eff2c`

This package contains only the Privacy Center public static source, deterministic build contract, and approved public Privacy Shield icon. Generated `website/dist`, Privacy Shield runtime code, adapters, internal contracts, configuration, and service implementation remain outside static-site authority.

## Current publication truth

The canonical Privacy Center source is migrated to **GLAZE UI V1.3 / 1.3.0 Stable**, not the historical Glaze UI 2.1.0 website runtime.

`sites/privacy/website/glaze.lock.json` pins the exact Stable GLAZE UI source revision and entrypoint blob listed above. `website/build.py` independently checks that lock, verifies the exact entrypoint Git blob, rejects unsafe/remote CSS dependency traversal, and reconstructs the publication from canonical local source plus the pinned GLAZE UI dependency tree.

The public Privacy Center deployment was production-verified on September 10, 2026 at exact central repository revision `80379f6962a5ded6c01317542941a2c55aedd922`. The accepted verification established the central Cloudflare Pages source/build/output contract, canonical HTTPS root and 404 behavior, committed response headers, GLAZE UI `1.3.0`, exact GLAZE UI source revision and entrypoint blob, and rendered review. See `docs/production-verification-privacy-2026-09-10.md`.

The Privacy Center subtree at current canonical `main` remains byte-for-byte represented by the same Git tree accepted at that production revision: `50d11f2ba52f7009ee8d1b08973ad1f4d75eff2c`. Production verification is revision/publication-specific; any future material change to this subtree requires independent re-verification before the changed publication may inherit `production-verified` status.

The website source still carries the fail-closed consumer state `source-migrated-rendered-acceptance-pending`. That source marker must not be interpreted as reversing the recorded website production verification. It preserves the broader qualification boundary: the existing production record does not by itself establish dedicated assistive-technology/accessibility acceptance, Privacy Shield runtime authorization, rollback retirement, or lifecycle promotion for Privacy Shield 2.0.

## Authority and retirement boundaries

Production verification applies only to the public Privacy Center website deployment. It does **not** establish a Privacy Shield `ALLOW`, `DENY`, `ALLOW_WITH_CONSTRAINTS`, or `REQUIRE_USER_DECISION` result; consent or purpose authorization; durable authorization-state acceptance by any application, adapter, or runtime; Wardveil protection; Identity authority; Everkeep recovery readiness; or Mesh runtime acceptance.

The website deployment source has been cut over to this central repository, but the legacy Privacy Shield repository remains the Privacy Shield project/runtime authority. Legacy website-source retirement is a separate gate. Do not remove the former website subtree, deployment references, rollback material, automation references, or preservation material until those dependencies are independently reviewed and the resulting state is revalidated.

Historical Glaze UI 2.1.0 material may remain in repository history or preservation records, but it must not return as an active Privacy Center runtime dependency.
