# GoreeCloud Main Website

Canonical static website repository: `GoreeCloud/goreecloud-static-websites`

- Site root: `sites/main`
- Canonical public domain: `https://www.goreecloud.com/`
- Legacy deployment/source lineage: `GoreeCloud/goreecloud-website`
- Current design target: **GLAZE UI V1.3 / 1.3.0 Stable**
- Canonical Glaze revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Source state: `source-migrated-rendered-acceptance-pending`

This package contains the directly authored public HTML, reviewed assets, exact GLAZE UI consumer lock, build tooling, validation tooling, and public policy files required to reproduce the Main static artifact.

## Build

Check out `GoreeCloud/goreecloud-glaze-ui` at exact revision `8354308445da9ac35ced2b37a7f503a08a0aaf72`, then from the repository root run:

```bash
GLAZE_UI_SOURCE=/path/to/goreecloud-glaze-ui python sites/main/scripts/build_public_site.py
python sites/main/scripts/validate_build_artifact.py
```

The build verifies the exact V1.3 Stable entrypoint and recursively vendors its same-origin CSS dependency closure. It does not fetch or execute a runtime design-system dependency in the browser.

## Repository directory policy

The Main website no longer publishes a numeric claim for the "current" GoreeCloud repository total. Repository creation is continuous and the live GoreeCloud GitHub organization is authoritative for current inventory/counts. `repositories.html` is a reviewed public-safe source-role guide. `docs/repository-portfolio.json` is retained as historical/review provenance and must not be treated as current live inventory.

## Acceptance boundary

Central source/build migration is not production cutover. Cloudflare Pages repository/root configuration, exact deployment revision, custom-domain behavior, rendered visual review, accessibility acceptance, performance, rollback, and post-deployment verification remain separate gates. Historical production evidence for earlier source revisions remains valid within its original exact scope.
