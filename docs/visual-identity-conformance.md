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

Repository validation now checks the exact Git blob identity of these canonical assets and rejects the forbidden artwork-pending placeholder.

## Open branding-authority blockers

The branding authority does not currently publish approved canonical product artwork for:

- GoreeCloud Home
- GoreeCloud Home Security
- GoreeCloud Containers
- GoreeCloud Boot

The approval gate is `GoreeCloud/goreecloud-branding-assets#16`. Until approval occurs, centralized websites must keep the canonical product names but must not invent substitute artwork or repurpose third-party identity.

## Glaze UI namespace-reset review

Visual identity conformance is separate from design-system consumer conformance. The current Stable Glaze UI namespace is V1.1 / 1.1.0, while several centralized site packages still preserve active pre-reset 2.x consumer bundles or locks from their migration source. These sites require controlled V1.1 consumer migration rather than filename substitution:

- Archive
- Blog
- Everkeep / Continuity Center
- Identity Center
- Main
- Manager
- Mesh
- Privacy Center
- Projects
- Roadmap
- Suite

Security Center, Design Center, and Labs already contain V1.1-era source, but their own exact consumer acceptance remains governed separately. Pre-reset source retained solely as historical/reference evidence must be clearly non-active and must not be loaded by the public artifact.

## Completion boundary

This record does not declare the full website portfolio conformant yet. Identity defects with available approved canonical replacements are corrected in the current candidate and protected by CI. Missing canonical product identities and active pre-reset Glaze consumers remain explicit blockers until their respective approval/migration and deployment verification gates close.
