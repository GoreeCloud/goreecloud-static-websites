# GoreeCloud Firefox Extensions — Public Website

Canonical centralized static source for `firefox.goreecloud.com`.

## Publication contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Production branch target: `main`
- Site root: `sites/firefox`
- Build command: `python3 build.py`
- Build output directory: `dist`
- Intended custom domain: `firefox.goreecloud.com`
- Extension source authority: `GoreeCloud/goreecloud-firefox-extensions`
- Current design target: GLAZE UI V1.3 / 1.3.0

## Content authority

The extension names, source versions, source lifecycle states, and independently accepted Stable release versions come from `GoreeCloud/goreecloud-firefox-extensions/docs/extension-inventory.json` schema v2. The website must not infer Stable status from source presence or unsigned packaging.

Current inventory represented by the site:

- GoreeCloud Bookmarks — source 0.1.1; source candidate; no accepted Stable release.
- GoreeCloud Download Manager Extension — source 0.2.12; accepted Stable 0.2.12.
- GoreeCloud Privacy Shield — source 0.2.0; accepted Stable 0.2.0.
- GoreeCloud Redirector — source 0.2.1; accepted Stable 0.2.0.
- GoreeCloud Source Resync — source 1.1.2; no accepted Stable release recorded.

## Validation

From this directory:

```bash
python3 validate.py
node --check site.js
```

The source is not production-accepted until a Cloudflare Pages project is configured to this repository/branch/root/build/output contract, `firefox.goreecloud.com` is attached, and canonical-domain byte/header/browser verification passes.
