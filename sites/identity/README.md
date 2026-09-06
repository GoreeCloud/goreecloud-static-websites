# GoreeCloud Identity Center Public Website

Canonical static source for the approved public Identity Center namespace `https://id.goreecloud.com`.

## Repository contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/identity`
- Production branch target: `main`
- Build command: `python sites/identity/build.py`
- Build output directory: `sites/identity/dist`
- Approved public namespace: `id.goreecloud.com`
- Legacy repository: `GoreeCloud/goreecloud-identity`
- Legacy path: `identity-center-site`

## GLAZE UI boundary

Identity Center source targets **GLAZE UI V1.1 / 1.1.0** and publishes the exact pinned Stable web bundle same-origin from canonical promotion revision `15cc76d2bcd4065552dc31c77145b63f34d9e7b2`.

The immutable Stable bundle currently contains one known dangling `glaze-v1.candidate.css` import. The isolated build fails closed unless that exact pinned dependency remains absent, then removes only that single dangling import in the generated artifact. Any other dependency drift fails the build. This bounded consumer workaround is not itself GLAZE conformance or production acceptance.

The former active Glaze UI 2.1 source bundle is not part of the current Identity Center artifact.

## Identity and authority boundary

GoreeCloud Identity is the platform authority for identity, authentication, authorization, accounts, devices, credentials, sessions, service identity, and delegated authority. The public Identity Center is an informational and administrative surface; it does not manufacture production Identity acceptance.

The inherited authentik-derived runtime remains transitional while the first-party GoreeCloud Identity implementation advances. GoreeCloud Manager, Wardveil Security, Privacy Shield, Everkeep, Glaze UI, and GoreeCloud Mesh retain their own authorities.

The canonical Identity artwork is maintained by `GoreeCloud/goreecloud-branding-assets`; the copy in this package is a deployable derivative, not a separate branding authority.

## Acceptance boundary

Central source/build validation does not establish Cloudflare source cutover, `id.goreecloud.com` DNS/TLS activation, exact deployed-revision equivalence, production Identity runtime acceptance, GLAZE conformance, or legacy-source retirement. Those remain separate evidence gates.
