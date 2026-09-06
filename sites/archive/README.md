# GoreeCloud Archive Public Website

Canonical static source for `https://archive.goreecloud.com`.

## Repository contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/archive`
- Production branch target: `main`
- Build command: `python sites/archive/build.py`
- Build output directory: `sites/archive/dist`
- Custom domain: `archive.goreecloud.com`
- Migration source: `GoreeCloud/goreecloud-website` at `sites/archive`
- Reviewed legacy source tree: `261f21095d912d0ee915553f52d41c3861a4cff1`

## GLAZE UI boundary

Archive source targets **GLAZE UI V1.1 / 1.1.0** and publishes the exact pinned Stable web bundle same-origin from canonical promotion revision `15cc76d2bcd4065552dc31c77145b63f34d9e7b2`.

The immutable Stable bundle currently contains one known dangling `glaze-v1.candidate.css` import. The isolated build fails closed unless that exact pinned dependency is still absent, then removes only that single dangling import in the generated artifact. Any other dependency drift fails the build. This bounded consumer workaround is not itself GLAZE conformance or production acceptance.

The pre-reset Glaze UI 2.1 source bundle is no longer an active Archive consumer dependency.

Cloudflare source cutover, exact deployed-revision verification, representative visual/accessibility review, and legacy-source retirement remain separate migration gates after central source/build validation.
