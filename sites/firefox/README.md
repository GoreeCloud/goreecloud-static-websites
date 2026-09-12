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
- Branding authority: `GoreeCloud/goreecloud-branding-assets`
- Current design target: GLAZE UI V1.3 / 1.3.0

## Content authority

The extension names, source versions, source lifecycle states, and independently accepted Stable release versions come from `GoreeCloud/goreecloud-firefox-extensions/docs/extension-inventory.json` schema v2. The website must not infer Stable status from source presence or unsigned packaging.

Current inventory represented by the site:

- GoreeCloud Bookmarks — source 0.1.1; source candidate; no accepted Stable release.
- GoreeCloud Download Manager Extension — source 0.2.12; accepted Stable 0.2.12.
- GoreeCloud Privacy Shield — source 0.2.0; accepted Stable 0.2.0.
- GoreeCloud Redirector — source 0.2.1; accepted Stable 0.2.0.
- GoreeCloud Source Resync — source 1.1.2; no accepted Stable release recorded.

## Branding contract

Official extension visual identity is controlled by `GoreeCloud/goreecloud-branding-assets`. Consumer copies in this website must remain derivative copies of approved canonical assets and must not establish independent branding authority.

Approved artwork currently synchronized into the website:

- GoreeCloud Bookmarks → `products/bookmarks/app-icon.svg` → `assets/extensions/bookmarks.svg`.
- GoreeCloud Download Manager Extension → `products/download-manager-extension/app-icon.svg` → `assets/extensions/download-manager.svg`.
- GoreeCloud Privacy Shield → `systems/privacy-shield/privacy-shield-icon.svg` → `assets/extensions/privacy-shield.svg`.

GoreeCloud Redirector and GoreeCloud Source Resync do not currently have separate approved canonical artwork in the branding catalog. Until those identities are approved in the branding repository, the public site must use text-only branding-pending treatment and must not invent monograms, logos, icons, store artwork, or promotional graphics for them.

## Validation

From this directory:

```bash
python3 validate.py
node --check site.js
```

The source is not production-accepted until a Cloudflare Pages project is configured to this repository/branch/root/build/output contract, `firefox.goreecloud.com` is attached, and canonical-domain byte/header/browser verification passes.
