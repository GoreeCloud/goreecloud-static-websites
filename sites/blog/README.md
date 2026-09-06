# GoreeCloud Blog Public Website

Canonical static source for `https://blog.goreecloud.com`.

## Repository contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/blog`
- Production branch target: `main`
- Build command: none
- Build output directory: `.`
- Custom domain: `blog.goreecloud.com`
- Migration source: `GoreeCloud/goreecloud-website` at `sites/blog`
- Reviewed legacy source tree: `fd6064a27667bf7214de7c8418ef3629cded054b`

The inactive Glaze UI 1.5.0 and 2.0.0 bundles from the legacy directory are intentionally not promoted into the new authority. The current Blog activates Glaze UI 2.1.0.

Cloudflare source cutover, exact production acceptance, and legacy-source retirement remain separate migration gates after central validation.
