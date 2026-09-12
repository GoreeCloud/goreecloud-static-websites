# GoreeCloud Manager public website

Canonical static website source for `manage.goreecloud.com`.

This package contains only the public informational website for GoreeCloud Manager. The authenticated private Manager application, runtime integrations, application clients, production-readiness evidence, credentials, and operational state remain in the authoritative Manager project and are outside this static-site authority.

## Current public-site design target

- GLAZE UI: **V1.3 / 1.3.0 Stable**
- Canonical Glaze repository: `GoreeCloud/goreecloud-glaze-ui`
- Exact Stable source revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Official Stable entrypoint: `css/glaze-v1.3.0.css`
- Consumer state: `source-migrated-rendered-acceptance-pending`
- Product identity: byte-identical copy of `GoreeCloud/goreecloud-branding-assets/products/manager/app-icon.svg`

The public site remains `noindex,nofollow,noarchive` until its independent public deployment/acceptance boundary is satisfied. It intentionally does not advertise the private Manager application hostname.

## Governed Cloudflare Pages contract

The approved centralized publication contract is:

- Repository: `GoreeCloud/goreecloud-static-websites`
- Production branch: `main`
- Root directory: `sites/manager`
- Build command: `python3 scripts/build_public_site.py`
- Build output directory: `dist`
- Canonical public domain: `manage.goreecloud.com`

This contract is the desired source configuration for the public informational website only. It does not establish that Cloudflare has already been reconnected to the central repository, that the custom domain serves the reviewed central revision, or that the private Manager application is deployed or accepted.

## Build and validation

From the repository root:

```bash
python sites/manager/scripts/validate_public_site.py
GLAZE_UI_SOURCE=/path/to/goreecloud-glaze-ui python sites/manager/scripts/build_public_site.py
python sites/manager/scripts/validate_public_site.py --dist
python sites/manager/scripts/browser_responsive_smoke.py
python sites/manager/scripts/verify_public_deployment.py --check-config
node --check sites/manager/site.js
```

The build validates the exact Stable V1.3 entrypoint blob and vendors only the recursive CSS dependency closure reachable from that entrypoint. Historical implementation-stage filenames reached through the official Stable entrypoint remain provenance, not direct site imports.

The responsive Chrome smoke exercises the exact built artifact at 1180×900, 768×900, 390×844, and 320×844. It checks viewport containment, responsive grids, 48px interaction floors, header behavior, image loading, and System/Light/Dark appearance controls.

After an independently authorized Cloudflare source cutover, run the Manager publication workflow manually. The production gates rebuild the reviewed artifact and compare the canonical live root, explicit 404, robots, local CSS/JS, Manager identity asset, and the complete built Glaze stylesheet closure against the exact candidate before running the live Chrome smoke. Provider deployment success by itself is not production acceptance.

## Authority and acceptance boundary

The public page may summarize verified Manager project state, including its visibility-first/read-only architecture and current Development direction, but it must not manufacture runtime, integration, deployment, or production truth.

Source/build migration, rendered visual acceptance, accessibility/adaptive acceptance, Cloudflare/source cutover, private Manager runtime acceptance, integral-platform-system acceptance, production-readiness evidence, release approval, and production activation remain separate gates. A green static-site build does not approve or deploy the Manager application.

Do not advance `sites/manifest.json` from `legacy-source` until the Cloudflare source configuration is verified against the contract above, the exact reviewed central revision is bound to the provider deployment, and canonical-domain HTTP/browser acceptance passes.
