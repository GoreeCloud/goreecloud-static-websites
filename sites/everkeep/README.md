# GoreeCloud Everkeep Static Website

Canonical source repository: `GoreeCloud/goreecloud-static-websites`

- Site root: `sites/everkeep`
- Canonical domain: `everkeep.goreecloud.com`
- Canonical Everkeep implementation repository: `GoreeCloud/goreecloud-everkeep`
- Current Glaze source target: **GLAZE UI V1.3 / 1.3.0 Stable**
- Exact Glaze source revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Glaze consumer state: `source-migrated-rendered-acceptance-pending`
- Current Everkeep repository main observed during this migration: `37f77a2c330a60c116aca107661a852bb8b5f031`

This package contains the Continuity Center public static source, approved Everkeep public mark, exact-source Glaze consumer lock, deterministic public-site build script, responsive/accessibility source validator, explicit public 404, local Chrome responsive smoke, and read-only canonical-domain production verifiers. Generated `dist/`, Everkeep runtime/service code, recovery/failover implementation, contracts, persistence, continuity-control logic, and unrelated repository governance remain outside static-site authority.

## Cloudflare Pages deployment contract

When the Continuity Center Cloudflare Pages project is cut over to the central static-site repository, the deployment contract is:

- Repository: `GoreeCloud/goreecloud-static-websites`
- Production branch: `main`
- Root directory: `sites/everkeep`
- Build command: `python3 scripts/build_public_site.py`
- Build output directory: `dist`
- Canonical custom domain: `everkeep.goreecloud.com`

A provider-side successful deployment is not production acceptance. After cutover, the exact deployed central revision must be bound to the live canonical domain and the read-only production verification must pass for exact artifact bytes, HTTP status, explicit 404 behavior, committed response headers, canonical sitemap/robots publication, Everkeep identity, GLAZE UI V1.3 integrity, and responsive browser rendering before `sites/manifest.json` may record this site as `production-verified`.

The approved Everkeep mark under `sites/everkeep/assets/` is synchronized with the canonical `GoreeCloud/goreecloud-branding-assets/systems/everkeep` asset tree. Website presentation cannot manufacture resilience or recovery state.

The V1.3 migration is a source/build migration only until independent production evidence is accepted. Rendered visual review, accessibility acceptance, performance, rollback, Cloudflare source cutover, DNS/HTTPS verification, exact production verification, Everkeep recovery-effect authority, and application-specific production continuity acceptance remain separate gates. Centralizing or modernizing this public site does not authorize production failover, traffic switching, data movement, rollback, or a global Recovery Ready state.
