# GoreeCloud Roadmap Public Website

Canonical static source for `https://roadmap.goreecloud.com`.

## Repository contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/roadmap`
- Production branch target: `main`
- Build command: none
- Build output directory: `.`
- Custom domain: `roadmap.goreecloud.com`
- Migration source: `GoreeCloud/goreecloud-website` at `sites/roadmap`
- Reviewed legacy source tree: `918281e90cc886938b7bdfd341e151fd841391c5`

The inactive Glaze UI 1.5.0 and 2.0.0 bundles from the legacy directory are intentionally not carried forward. The current site activates Glaze UI 2.1.0 and the site validator requires that current bundle.

## Public-information boundary

The roadmap is deliberately broader and less detailed than internal task trackers, project specifications, change logs, infrastructure plans, and security records. It communicates public direction without exposing private topology, operational details, sensitive remediation work, credentials, private hostnames, internal addresses, or unpublished project information.

Roadmap states describe direction and maturity, not guaranteed delivery dates. Dates and commitments must not be inferred from ordering alone.

## Validation

Run:

```bash
python3 sites/roadmap/validate.py
node --check sites/roadmap/site.js
```

Cloudflare source cutover, custom-domain verification, exact production acceptance, and legacy-source retirement remain separate migration gates after central validation.
