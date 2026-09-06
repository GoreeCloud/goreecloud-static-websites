# GoreeCloud Roadmap Public Website

Canonical static source for `https://roadmap.goreecloud.com`.

## Repository contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/roadmap`
- Production branch target: `main`
- Build command: `python sites/roadmap/build.py`
- Build output directory: `sites/roadmap/dist`
- Custom domain: `roadmap.goreecloud.com`
- Migration source: `GoreeCloud/goreecloud-website` at `sites/roadmap`
- Reviewed legacy source tree: `918281e90cc886938b7bdfd341e151fd841391c5`

## GLAZE UI boundary

Roadmap interface source targets **GLAZE UI V1.1 / 1.1.0** and publishes the exact pinned Stable web bundle same-origin from canonical promotion revision `15cc76d2bcd4065552dc31c77145b63f34d9e7b2`.

The immutable Stable bundle currently contains one known dangling `glaze-v1.candidate.css` import. The isolated build fails closed unless that exact pinned dependency is still absent, then removes only that single dangling import in the generated artifact. Any other dependency drift fails the build. This bounded consumer workaround is not itself GLAZE conformance or production acceptance.

The former active Glaze UI 2.1 source bundle is no longer part of the Roadmap runtime. Historical platform/design milestones belong in the public Archive or explicitly historical content rather than being presented as the current Roadmap target.

## Public-information boundary

The roadmap is deliberately broader and less detailed than internal task trackers, project specifications, change logs, infrastructure plans, and security records. It communicates public direction without exposing private topology, operational details, sensitive remediation work, credentials, private hostnames, internal addresses, or unpublished project information.

Roadmap states describe direction and maturity, not guaranteed delivery dates. Dates and commitments must not be inferred from ordering alone. Platform-system, Stable, production, protected, preserved, conformance, and deployment claims remain evidence-scoped.

## Validation

Run:

```bash
python3 sites/roadmap/build.py
python3 scripts/validate_v1_static_site.py sites/roadmap
python3 sites/roadmap/validate.py
node --check sites/roadmap/site.js
```

Cloudflare source cutover, custom-domain verification, exact production acceptance, representative visual/accessibility review, and legacy-source retirement remain separate migration gates after central validation.
