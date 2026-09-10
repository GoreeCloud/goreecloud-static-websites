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

## Build and validation

From the repository root:

```bash
python sites/manager/scripts/validate_public_site.py
GLAZE_UI_SOURCE=/path/to/goreecloud-glaze-ui python sites/manager/scripts/build_public_site.py
python sites/manager/scripts/validate_public_site.py --dist
node --check sites/manager/site.js
```

The build validates the exact Stable V1.3 entrypoint blob and vendors only the recursive CSS dependency closure reachable from that entrypoint. Historical implementation-stage filenames reached through the official Stable entrypoint remain provenance, not direct site imports.

## Authority and acceptance boundary

The public page may summarize verified Manager project state, including its visibility-first/read-only architecture and current Development direction, but it must not manufacture runtime, integration, deployment, or production truth.

Source/build migration, rendered visual acceptance, accessibility/adaptive acceptance, Cloudflare/source cutover, private Manager runtime acceptance, integral-platform-system acceptance, production-readiness evidence, release approval, and production activation remain separate gates. A green static-site build does not approve or deploy the Manager application.
