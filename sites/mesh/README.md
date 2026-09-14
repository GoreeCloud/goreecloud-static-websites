# GoreeCloud Mesh Center Static Website

Canonical static website repository: `GoreeCloud/goreecloud-static-websites`

- Site root: `sites/mesh`
- Canonical domain: `mesh.goreecloud.com`
- Canonical Mesh implementation/runtime repository: `GoreeCloud/goreecloud-mesh`
- Current publication target: **GLAZE UI V1.4 / 1.4.0 Stable**
- Exact Glaze source revision: `84cb3db4884042f0fa25ed6d475a127fb110f596`
- Stable entrypoint: `glaze-v1.4.0.css`
- Entrypoint Git blob: `d48a9bc317090d152799769271de0fb4325494c4`
- Glaze consumer state: `build-migrated-rendered-acceptance-pending`
- Current Mesh runtime/source truth baseline referenced by the site: `8da8e52593dad045ed2356182b7ba755b789b79f`

The retained public-site source template preserves its reviewed **GLAZE UI V1.3 / 1.3.0** migration provenance at revision `8354308445da9ac35ced2b37a7f503a08a0aaf72`. The build projects that source deterministically into the current V1.4 publication identity and keeps `v1.3-site.css` as an inherited adaptation layer. It is not the active shared Glaze entrypoint.

This central package contains the public Mesh Center source, canonical Interlace mark, deterministic V1.4 publication build, source/artifact validators, exact canonical-domain production verifier, and real-browser responsive/production smoke gates. Generated `dist/`, Mesh runtime code, private APIs, service identity, transport/runtime integrations, and platform-system execution remain outside static-site authority.

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

The Pages project identity and namespace are verified from legacy `GoreeCloud/goreecloud-mesh` Cloudflare deployment evidence. Reconnecting the Pages project to the central repository changes only standalone public website source authority; it does not retire or replace the Mesh runtime repository.

## Validation

From the repository root:

```bash
python sites/mesh/scripts/validate_public_site.py
GLAZE_UI_SOURCE=/path/to/goreecloud-glaze-ui python sites/mesh/scripts/build_public_site.py
python sites/mesh/scripts/validate_public_site.py --dist
python sites/mesh/scripts/browser_responsive_smoke.py
python sites/mesh/scripts/verify_v14_public_deployment.py --check-config
node --check sites/mesh/website/site.js
```

After independently authorized provider cutover, rebuild the exact artifact and run `python sites/mesh/scripts/verify_v14_public_deployment.py --target production` plus the production Chrome gate.

## Acceptance boundary

Source/template validation, V1.4 build validation, rendered candidate acceptance, Cloudflare deployment success, canonical-domain HTTP equivalence, production browser verification, and production acceptance are separate gates.

The production verifier must compare the canonical live domain against the exact reviewed built artifact and verify true 404 behavior, canonical URLs, committed security headers, Interlace identity, local site assets, exact V1.4 publication markers, and Cloudflare delivery. The browser gate must exercise desktop, tablet, narrow mobile, and 320-pixel layouts plus System/Light/Dark controls.

A public website pass does **not** establish GoreeCloud Mesh runtime interoperability, authenticated service access, authority transfer, platform-system production acceptance, product Stable qualification, authorization, security/privacy acceptance, or another technical authority claim. `authority_transfer = false` remains a substantive Mesh invariant.
