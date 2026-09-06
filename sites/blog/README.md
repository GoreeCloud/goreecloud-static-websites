# GoreeCloud Blog Public Website

Canonical static source for `https://blog.goreecloud.com`.

## Repository contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/blog`
- Production branch target: `main`
- Build command: `python sites/blog/build.py`
- Build output directory: `sites/blog/dist`
- Custom domain: `blog.goreecloud.com`
- Migration source: `GoreeCloud/goreecloud-website` at `sites/blog`
- Reviewed legacy source tree: `fd6064a27667bf7214de7c8418ef3629cded054b`

## GLAZE UI boundary

Blog interface source targets **GLAZE UI V1.1 / 1.1.0** and publishes the exact pinned Stable web bundle same-origin from canonical promotion revision `15cc76d2bcd4065552dc31c77145b63f34d9e7b2`.

The immutable Stable bundle currently contains one known dangling `glaze-v1.candidate.css` import. The isolated build fails closed unless that exact pinned dependency is still absent, then removes only that single dangling import in the generated artifact. Any other dependency drift fails the build. This bounded consumer workaround is not itself GLAZE conformance or production acceptance.

Dated editorial articles preserve the product and design-system state from their publication checkpoint, including historical version references. Those references are content, not active Blog runtime dependencies. The former active Glaze UI 2.1 source bundle is no longer part of the Blog consumer artifact.

Cloudflare source cutover, exact deployed-revision verification, representative visual/accessibility review, and legacy-source retirement remain separate migration gates after central source/build validation.
