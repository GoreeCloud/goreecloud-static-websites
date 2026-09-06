# GoreeCloud Static Websites

Canonical source repository for every GoreeCloud-controlled static website.

## Repository role

All GoreeCloud static website source must ultimately live in this repository. Product, service, design-system, Platform System, and historical website repositories remain migration sources only until their website packages have been copied, validated, deployment references have been cut over, production has been verified where applicable, and the legacy copies have been retired.

Centralized source ownership does not require a single deployment. Each site may retain its own hostname, Cloudflare Pages project, build root, validation gates, release lifecycle, and production-acceptance evidence.

## Layout

```text
sites/
  manifest.json
  <site-id>/
docs/
  migration-status.md
```

`sites/manifest.json` is the machine-readable migration registry. Each `sites/<site-id>/` directory is an independent static-site package or the source portion of one.

Generated deployment artifacts such as `dist/` are not authoritative source and should be regenerated from reviewed site source unless a site-specific contract explicitly requires otherwise.

## Migration states

- `inventory-confirmed` — legacy source and intended central path are verified.
- `source-copied` — source is present here, but central validation is not yet accepted.
- `validated-in-central-repo` — central source passed its migration validation gates.
- `deployment-cutover-pending` — source is accepted here but deployment still references the legacy repository/path.
- `production-verified` — the deployed site has been verified against accepted central source.
- `legacy-source-retired` — obsolete website source and references have been removed from the legacy repository.

A file copy alone is never a completed migration.

## `goreecloud-website` retirement

`GoreeCloud/goreecloud-website` is transitional. It must be deleted only after every static website it contains, plus static websites embedded in all other GoreeCloud repositories, has completed source migration, validation, reference/deployment cutover, production verification where applicable, and legacy-source retirement, with no remaining dependency on the old repository.

## Safety boundary

Do not move authenticated application code, backend services, private administrative interfaces, databases, secrets, or non-static runtime code into this repository merely because their owning product also has a public informational website. Only static public website source and website-specific build/validation resources required to reproduce it belong here.
