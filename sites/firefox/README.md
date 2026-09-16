# GoreeCloud Firefox Extensions — Public Website

Canonical centralized static source for the GoreeCloud Firefox Extensions informational website.

## URL namespace

- Canonical public URL: `https://www.goreecloud.com/firefox-extensions/`
- Legacy compatibility host: `https://firefox.goreecloud.com/`
- Current cutover state: `provider-cutover-verified`
- Compatibility requirement: retain `firefox.goreecloud.com` as a permanent-redirect source while legacy links remain operationally relevant.

The unified path is the canonical Firefox Extensions informational destination. The legacy hostname is not a second publication authority; it redirects to the governed `www.goreecloud.com` path using the shared GoreeCloud compatibility-redirect layer.

Production acceptance is fail-closed and revision-specific. The unified publication must continue to pass exact deployed-byte comparison, canonical metadata, GLAZE UI Stable metadata, required security headers, explicit 404 behavior, the legacy 301 redirect contract, responsive rendering, keyboard/focus checks, and automated accessibility-semantic checks. A later material source or publication change requires fresh acceptance evidence.

## Publication contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Production branch target: `main`
- Site root: `sites/firefox`
- Build command: `python3 build.py`
- Build output directory: `dist`
- Unified publication builder: `scripts/build_www_namespace.py`
- Unified production verifier: `scripts/verify_firefox_unified_production.py`
- Unified production browser gate: `scripts/browser_firefox_unified_production.py`
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

Unified-namespace validation builds this site beneath `/firefox-extensions/`, rewrites the legacy hostname to the governed `www.goreecloud.com` path, normalizes the mounted artifact to the current GLAZE UI Stable publication contract, and verifies the mounted canonical entrypoint.

For production acceptance from the repository root:

```bash
python scripts/build_www_namespace.py
python scripts/verify_firefox_unified_production.py
python scripts/browser_firefox_unified_production.py
```

Provider deployment success alone is not production acceptance; the live-verification gates above must pass against the deployed publication.
