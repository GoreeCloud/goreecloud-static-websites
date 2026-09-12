# GoreeCloud Main Website

Canonical static website repository: `GoreeCloud/goreecloud-static-websites`

- Site root: `sites/main`
- Canonical public domain: `https://www.goreecloud.com/`
- Legacy deployment/source lineage: `GoreeCloud/goreecloud-website`
- Current design target: **GLAZE UI V1.3 / 1.3.0 Stable**
- Canonical Glaze revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Source state: `source-migrated-rendered-acceptance-pending`

This package contains the directly authored public HTML, reviewed assets, exact GLAZE UI consumer lock, build tooling, validation tooling, browser acceptance tooling, deployment verification tooling, and public policy files required to reproduce the Main static artifact.

## Governed Cloudflare Pages contract

The approved centralized publication contract is:

- Repository: `GoreeCloud/goreecloud-static-websites`
- Production branch: `main`
- Root directory: `sites/main`
- Build command: `python3 scripts/build_public_site.py`
- Build output directory: `dist`
- Canonical public domain: `www.goreecloud.com`

This is the desired source configuration for the public website. It does not establish that Cloudflare Pages has already been reconnected from the legacy source repository, that a provider deployment corresponds to the reviewed central revision, or that production acceptance has occurred.

## Build and local acceptance

Check out `GoreeCloud/goreecloud-glaze-ui` at exact revision `8354308445da9ac35ced2b37a7f503a08a0aaf72`, then from the repository root run:

```bash
GLAZE_UI_SOURCE=/path/to/goreecloud-glaze-ui python sites/main/scripts/build_public_site.py
GLAZE_UI_SOURCE=/path/to/goreecloud-glaze-ui python sites/main/scripts/validate_build_artifact.py
python sites/main/scripts/browser_artifact_smoke.py
node --check sites/main/js/theme-init.js
node --check sites/main/js/main.js
```

The build verifies the exact V1.3 Stable entrypoint and recursively vendors its same-origin CSS dependency closure. It does not fetch or execute a runtime design-system dependency in the browser.

The built-artifact Chrome gate exercises 1180×900, 768×900, 390×844, and 320×844 CSS viewports. It checks horizontal containment, non-overlapping header/hero composition, responsive content-column reflow, hero typography, and bounded 48px mobile navigation before a change may merge.

## Production verification

Production checks are intentionally separate from source/build acceptance. After an independently authorized Cloudflare source cutover, the workflow may be dispatched manually to run:

```bash
python sites/main/scripts/verify_remote_deployment.py production
python sites/main/scripts/browser_responsive_smoke.py --target production
```

The deployment verifier is fixed to approved GoreeCloud HTTPS hosts and compares fetchable public files—including the complete pinned GLAZE UI CSS dependency closure—against the reviewed candidate byte-for-byte. It also checks required response-security headers, 404 behavior, and the public `security.txt` contract. The production Chrome gate then re-runs the responsive acceptance conditions against the canonical live site.

Provider deployment success alone is not evidence that Cloudflare is connected to the correct repository/root or that the exact reviewed revision is serving production. Those source-authority facts must be verified separately before the migration registry advances.

## Repository directory policy

The Main website no longer publishes a numeric claim for the "current" GoreeCloud repository total. Repository creation is continuous and the live GoreeCloud GitHub organization is authoritative for current inventory/counts. `repositories.html` is a reviewed public-safe source-role guide. `docs/repository-portfolio.json` is retained as historical/review provenance and must not be treated as current live inventory.

## Acceptance boundary

Central source/build migration is not production cutover. Cloudflare Pages repository/root configuration, exact deployment revision, custom-domain behavior, rendered visual review, accessibility acceptance, performance, rollback, and post-deployment verification remain separate gates. Historical production evidence for earlier source revisions remains valid within its original exact scope.

Do not advance `sites/manifest.json` from `legacy-source` until the Cloudflare source configuration is verified against the central contract, the provider deployment is bound to the exact reviewed central revision, and canonical-domain HTTP/browser acceptance passes.
