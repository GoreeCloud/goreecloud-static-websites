# GoreeCloud Mesh Center Static Website

Canonical static website repository: `GoreeCloud/goreecloud-static-websites`

- Site root: `sites/mesh`
- Canonical domain: `mesh.goreecloud.com`
- Canonical Mesh implementation/runtime repository: `GoreeCloud/goreecloud-mesh`
- Current Glaze source target: **GLAZE UI V1.3 / 1.3.0 Stable**
- Exact Glaze source revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Glaze consumer state: `source-migrated-rendered-acceptance-pending`
- Current Mesh runtime/source truth baseline referenced by the site: `8da8e52593dad045ed2356182b7ba755b789b79f`

This central package contains the public Mesh Center source, canonical Interlace mark, deterministic Glaze V1.3 build, source/artifact validators, exact canonical-domain production verifier, and real-browser responsive/production smoke gates. Generated `dist/`, Mesh runtime code, private APIs, service identity, transport/runtime integrations, and platform-system execution remain outside static-site authority.

## Cloudflare Pages cutover contract

The governed central deployment target is:

- Pages project: `goreecloud-mesh`
- Pages namespace: `goreecloud-mesh.pages.dev`
- Git repository: `GoreeCloud/goreecloud-static-websites`
- Production branch: `main`
- Framework preset: `None`
- Root directory: `sites/mesh`
- Build command: `python3 scripts/build_public_site.py`
- Build output directory: `dist`
- Canonical custom domain: `mesh.goreecloud.com`

The Pages project identity and namespace are verified from legacy `GoreeCloud/goreecloud-mesh` Cloudflare deployment evidence. The legacy Pages project is currently sourced from that runtime repository, where the equivalent repository-local build used a blank root, `python scripts/build_public_site.py`, and `dist`. Reconnecting the Pages project to the central repository changes only the standalone public website source authority; it does not retire or replace the Mesh runtime repository.

## Acceptance boundary

Source/build validation, Cloudflare deployment success, canonical-domain HTTP equivalence, rendered browser verification, and production acceptance are separate gates.

The production verifier must compare the canonical live domain against the exact reviewed built artifact and verify true 404 behavior, canonical URLs, committed security headers, Interlace identity, local site assets, and the exact Glaze V1.3 dependency closure. The browser gate must exercise desktop, tablet, narrow mobile, and 320-pixel layouts plus System/Light/Dark controls.

A public website pass does **not** establish GoreeCloud Mesh runtime interoperability, authenticated service access, authority transfer, platform-system production acceptance, product Stable qualification, authorization, security/privacy acceptance, or another technical authority claim. `authority_transfer = false` remains a substantive Mesh invariant.
