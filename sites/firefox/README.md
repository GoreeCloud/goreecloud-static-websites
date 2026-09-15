# GoreeCloud Firefox Extensions — Public Website

Canonical centralized static source for the GoreeCloud Firefox Extensions informational website.

## URL namespace

- Current public compatibility host: `https://firefox.goreecloud.com/`
- Governed unified canonical target: `https://www.goreecloud.com/firefox-extensions/`
- Current cutover state: `migration-preparation`
- Compatibility requirement: retain `firefox.goreecloud.com` as a redirect source after the unified path is published and production-verified.

The unified URL must not be recorded as production-accepted until the exact deployed revision, canonical metadata, redirect behavior, responsive rendering, accessibility, and applicable security headers have been verified. Until that acceptance closes, the existing Firefox hostname remains the verified live destination.

## Publication contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Production branch target: `main`
- Site root: `sites/firefox`
- Build command: `python3 build.py`
- Build output directory: `dist`
- Unified publication builder: `scripts/build_www_namespace.py`
- Extension source authority: `GoreeCloud/goreecloud-firefox-extensions`
- Branding authority: `GoreeCloud/goreecloud-branding-assets`
- Historical standalone design target: GLAZE UI V1.3 / 1.3.0
- Unified mounted publication target: current governed GLAZE UI Stable contract

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

Unified-namespace validation additionally builds this site beneath `/firefox-extensions/`, rewrites the legacy hostname to the governed `www.goreecloud.com` path, and verifies the mounted canonical entrypoint. Production acceptance remains separate from source/build acceptance.
