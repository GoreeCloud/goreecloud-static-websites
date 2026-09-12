# GoreeCloud Firefox Extensions — Public Showcase

Canonical centralized static-site source for the planned public surface at `firefox.goreecloud.com`.

## Publication contract

- Canonical website repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/firefox`
- Production branch target: `main`
- Build command: `python3 ../../scripts/build_simple_static_site.py .`
- Build output directory: `dist`
- Planned custom domain: `firefox.goreecloud.com`
- Cloudflare Pages project identity: **not yet verified / not yet recorded**
- Pages namespace: **not yet verified / not yet recorded**
- Canonical extension source repository: `GoreeCloud/goreecloud-firefox-extensions`
- Extension inventory source: `docs/extension-inventory.json`
- Inventory snapshot source revision: `50491e3280545281bc67c31a32819855b265ab92`

The Firefox extension repository remains authoritative for extension implementation, manifests, signing, security/privacy documentation, and release evidence. This central package owns only the public showcase website.

## Current extension inventory represented publicly

| Extension | Source version | Source state | Accepted Stable |
| --- | --- | --- | --- |
| GoreeCloud Bookmarks | 0.1.1 | source-candidate | — |
| GoreeCloud Download Manager Extension | 0.2.12 | stable | 0.2.12 |
| GoreeCloud Redirector | 0.2.1 | canonical-source | 0.2.0 |
| GoreeCloud Source Resync | 1.1.2 | canonical-source | — |
| GoreeCloud Privacy Shield | 0.2.0 | stable | 0.2.0 |

The site deliberately keeps source state and accepted Stable release state separate.

## Glaze UI contract

The public showcase targets **GLAZE UI V1.3 / 1.3.0 Stable** at exact canonical source revision `8354308445da9ac35ced2b37a7f503a08a0aaf72`. `glaze.lock.json` pins the exact Stable entrypoint and Git blob. `v1.3-site.css` provides the local reachability/accessibility adaptation while shared Glaze source remains authoritative.

## Validation

From the repository root:

```bash
python scripts/validate_simple_static_site.py sites/firefox
python sites/firefox/validate.py
python scripts/build_simple_static_site.py sites/firefox
python scripts/validate_simple_static_site.py sites/firefox --dist
python scripts/browser_simple_static_site.py firefox
```

The exact built artifact must pass source validation, built-artifact validation, and real Chrome exercises at 1180×900, 768×900, 390×844, and 320×844 before merge.

## Publication boundary

The source intentionally uses `noindex,nofollow` and `robots.txt` disallows crawling while provider publication is pending. Do not remove those controls or represent `firefox.goreecloud.com` as production until all of the following are verified:

1. A Cloudflare Pages project exists and its actual Pages namespace is recorded.
2. The project reads `GoreeCloud/goreecloud-static-websites`, branch `main`, root `sites/firefox`.
3. Build command and output directory match this contract.
4. `firefox.goreecloud.com` is attached with working DNS/TLS.
5. Exact deployed bytes, required security headers, 404 behavior, and responsive browser behavior pass against the accepted central revision.
6. Only after that verification should indexing be enabled and the migration/deployment registry advance.
