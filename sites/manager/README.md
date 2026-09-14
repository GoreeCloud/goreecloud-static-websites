# GoreeCloud Manager public website

Canonical static website source for `manage.goreecloud.com`.

This package contains only the public informational website for GoreeCloud Manager. The authenticated private Manager application, runtime integrations, application clients, production-readiness evidence, credentials, and operational state remain in the authoritative Manager project and are outside this static-site authority.

## Current public-site publication target

- GLAZE UI: **V1.4 / 1.4.0 Stable**
- Canonical Glaze repository: `GoreeCloud/goreecloud-glaze-ui`
- Exact Stable source revision: `84cb3db4884042f0fa25ed6d475a127fb110f596`
- Official Stable entrypoint: `css/glaze-v1.4.0.css`
- Entrypoint Git blob: `d48a9bc317090d152799769271de0fb4325494c4`
- Consumer state: `build-migrated-rendered-acceptance-pending`
- Product identity: byte-identical copy of `GoreeCloud/goreecloud-branding-assets/products/manager/app-icon.svg`

The retained HTML/CSS source template originated from the reviewed **GLAZE UI V1.3 / 1.3.0** migration at revision `8354308445da9ac35ced2b37a7f503a08a0aaf72`. The publication builder projects that retained source deterministically into the current V1.4 identity and keeps `v1.3-site.css` as an inherited compatibility/adaptation layer rather than representing it as the active shared Glaze entrypoint.

The public site remains `noindex,nofollow,noarchive` until its independent public deployment/acceptance boundary is satisfied. It intentionally does not advertise the private Manager application hostname.

## Governed Cloudflare Pages contract

- Cloudflare Pages project: `goreecloud-manager`
- Pages namespace: `goreecloud-manager.pages.dev`
- Repository: `GoreeCloud/goreecloud-static-websites`
- Production branch: `main`
- Root directory: `sites/manager`
- Build command: `python3 scripts/build_public_site.py`
- Build output directory: `dist`
- Canonical public domain: `manage.goreecloud.com`

The Pages project identity and namespace are verified from legacy `GoreeCloud/goreecloud-manager` deployment evidence. This contract is the desired source configuration for the public informational website only. It does not establish that Cloudflare has already been reconnected to the central repository, that the custom domain serves the reviewed central revision, or that the private Manager application is deployed or accepted.

## Build and validation

From the repository root:

```bash
python sites/manager/scripts/validate_public_site.py
GLAZE_UI_SOURCE=/path/to/goreecloud-glaze-ui python sites/manager/scripts/build_public_site.py
python sites/manager/scripts/validate_public_site.py --dist
python sites/manager/scripts/browser_responsive_smoke.py
python sites/manager/scripts/verify_v14_public_deployment.py --check-config
node --check sites/manager/site.js
```

Source validation preserves the inherited V1.3 template provenance and current Manager truth boundaries. The build validates the exact Stable V1.4 entrypoint blob, projects current publication markers to V1.4, and vendors only the recursive CSS dependency closure reachable from that entrypoint. Historical implementation-stage filenames reached through the official Stable entrypoint remain provenance, not direct site imports.

The responsive Chrome smoke exercises the exact built artifact at 1180×900, 768×900, 390×844, and 320×844. It checks viewport containment, responsive grids, 48px interaction floors, header behavior, image loading, and System/Light/Dark appearance controls.

After an independently authorized Cloudflare source cutover, rebuild the exact artifact and run `python sites/manager/scripts/verify_v14_public_deployment.py --target production`. The verifier compares all fetchable publication bytes, canonical host behavior, true 404 output, security headers, V1.4 markers, and Cloudflare delivery. Provider deployment success by itself is not production acceptance.

## Authority and acceptance boundary

The public page may summarize verified Manager project state, including its visibility-first/read-only architecture and current Development direction, but it must not manufacture runtime, integration, deployment, or production truth.

Source/template provenance, V1.4 publication build, rendered visual acceptance, accessibility/adaptive acceptance, Cloudflare/source cutover, private Manager runtime acceptance, integral-platform-system acceptance, production-readiness evidence, release approval, and production activation remain separate gates. A green static-site build does not approve or deploy the Manager application.

Do not advance `sites/manifest.json` from `legacy-source` until the Cloudflare source configuration is verified against the contract above, the exact reviewed central revision is bound to the provider deployment, canonical-domain HTTP/browser acceptance passes, and rollback/legacy-source retirement requirements are satisfied.
