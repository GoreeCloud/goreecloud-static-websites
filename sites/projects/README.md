# GoreeCloud Projects website

Canonical static source for `projects.goreecloud.com`.

## Repository contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/projects`
- Build command: none
- Build output directory: `.`
- Production branch target: `main`
- Custom domain: `projects.goreecloud.com`
- Migration source: `GoreeCloud/goreecloud-website` at `sites/projects`
- Reviewed legacy source tree: `2f7f5d096707bcc001e0e0ae46eb718c5ea3ab3f`

The site is static, dependency-free, tracking-free, and uses only local browser runtime code. `_headers` defines the public security-header baseline.

## Branding authority

- Canonical GoreeCloud branding repository: `GoreeCloud/goreecloud-branding-assets`.
- Canonical discovery and approval registry: `catalog.json` in that repository.
- Website `assets/suite/*.svg` files are synchronized publication derivatives of approved `products/*/app-icon.svg` sources; they are not independent branding authorities.
- Projects-local Glaze UI, Privacy Shield, Wardveil Security, Everkeep, GoreeCloud Mesh, and GoreeCloud platform artwork are synchronized publication derivatives of approved branding-repository sources.
- Wardveil Security uses the approved standalone **Sentinel Fold** emblem from `systems/wardveil-security/wardveil-security-icon.svg` as its primary visual mark. Wardveil wordmark and Security Center text are supporting identity, not part of the emblem.
- GoreeCloud Mesh uses the approved **Weave** mark from `systems/goreecloud-mesh/goreecloud-mesh-mark.svg`; Projects must not revert Mesh to the former text-only pending-artwork state while that canonical approval remains current.
- A project without approved catalog artwork remains text-only rather than inheriting the GoreeCloud platform logo or receiving a fabricated placeholder mark.
- Synchronized publication derivatives must remain byte-identical to their pinned canonical Git blobs.

## Production boundary

Source validation does not itself authorize production claims. Branch-preview and production verification must confirm that the deployed Projects surface matches the reviewed source. Platform artwork identifies the relevant system but does not establish technical runtime acceptance, protection, privacy, recovery, or coordination state.

Cloudflare Pages source cutover and legacy-source retirement remain separate migration gates after central validation.
