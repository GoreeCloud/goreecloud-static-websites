# Static Website Visual Identity Conformance

**Authority:** `GoreeCloud/goreecloud-branding-assets`  
**Canonical website source:** `GoreeCloud/goreecloud-static-websites`  
**Reviewed:** 2026-09-06

## Governing rule

Every active GoreeCloud public website must use current approved first-party logos, icons, marks, favicons, and artwork from the canonical branding authority or from explicitly governed derivatives. Placeholder artwork, generic initials/acronyms used as product identity, local redraws, upstream substitutes, untraceable copies, and superseded identity assets are conformance defects.

## Corrections in the current candidate

- Projects: `assets/goreecloud-mesh-mark.svg` is pinned to the current canonical GoreeCloud Mesh Interlace blob `5362a52bd9fb38379f083a4d894934ed1acf9b67`.
- Manager: `assets/manager-mark.svg` is pinned to the canonical GoreeCloud Manager product icon blob `024d82d5b5911e426216dfbd6a19d95cd6d71fc3`.
- Labs: GoreeCloud AI is pinned to canonical blob `1cbe04748f50cb843eef0cbb7233e2769efa275a`.
- Labs: GoreeCloud Code is pinned to canonical blob `579f0416bd2839bf40e87de7751e319d80bd0bf9`.
- Labs: the former Home, Security, OCI, and Boot text badges are no longer rendered as surrogate product identity while canonical artwork is unapproved.
- Main: the obsolete `goreecloud-artwork-pending.svg` placeholder is removed from active centralized source.

Repository validation checks the exact Git blob identity of these canonical assets and rejects the forbidden artwork-pending placeholder.

## Open branding-authority blockers

The branding authority does not currently publish approved canonical product artwork for:

- GoreeCloud Home
- GoreeCloud Home Security
- GoreeCloud Containers
- GoreeCloud Boot

The approval gate is `GoreeCloud/goreecloud-branding-assets#16`. Until approval occurs, centralized websites must keep the canonical product names but must not invent substitute artwork or repurpose third-party identity.

## Glaze UI namespace-reset review

Visual identity conformance is separate from design-system consumer conformance. The current Stable Glaze UI namespace is V1.1 / 1.1.0.

### Source/build migration validated in the current stacked candidate

The following packages have completed controlled V1.1 source and isolated-artifact migration in PR #15. Their migration uses the immutable V1.1 authority, same-origin generated bundles, fail-closed validation, and the documented bounded workaround for the known immutable Stable import defect. This is source/build evidence, not production or GLAZE conformance acceptance.

- Archive
- Blog
- Identity Center
- Main
- Roadmap

The Main checkpoint at revision `6435e83ab3f9561e3662b74c355a6a71315c8073` passed Main source validation, isolated V1.1 artifact construction, shared V1.1 artifact validation, allowlist validation, JavaScript syntax, repository-wide validation, and all other workflows triggered by that exact revision.

### Remaining controlled migrations

These centralized packages still preserve active pre-reset 2.x consumer source or locks and require controlled migration rather than filename substitution:

- Everkeep / Continuity Center
- Manager
- Mesh
- Privacy Center
- Projects
- Suite

Security Center, Design Center, and Labs already contain V1.1-era source, but their own exact consumer acceptance remains separately governed. Pre-reset source retained solely as historical/reference evidence must be clearly non-active and must not be loaded by the public artifact.

## Completion boundary

This record does not declare the full website portfolio conformant. The current PR closes the source/build namespace-reset gate only for the five listed migrated consumers. Missing canonical product identities, the six remaining pre-reset consumers, rendered/human acceptance where required, Cloudflare source cutover, exact production deployment verification, and formal GLAZE consumer acceptance remain separate blockers.
