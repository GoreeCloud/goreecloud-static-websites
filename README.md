# GoreeCloud Static Websites

Canonical source repository for every GoreeCloud-controlled static website.

## Mandatory repository policy

**All GoreeCloud static websites MUST be stored, maintained, and referenced from `GoreeCloud/goreecloud-static-websites`.** This repository is the single authoritative source location for static website source across the GoreeCloud ecosystem.

This requirement includes, without limitation:

- the main GoreeCloud website;
- Wardveil Security website;
- GoreeCloud Identity website;
- GoreeCloud Privacy website;
- GoreeCloud Roadmap website;
- GoreeCloud Archive website;
- Projects, Blog, Suite, Design, Everkeep, Manager, Mesh, and other existing static websites;
- static websites currently embedded in individual application, service, system, or historical repositories; and
- every new GoreeCloud static website created in the future.

Other GoreeCloud repositories may reference or deploy a site from this repository, but they must not remain the authoritative home of separate static website copies after migration. Repository documentation, deployment configuration, build references, automation, and other source references must be cut over to the corresponding package in `goreecloud-static-websites` as each migration is completed.

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

`GoreeCloud/goreecloud-website` is transitional and MUST be deleted once the consolidation is complete.

Deletion is permitted only after:

1. every static website currently stored in `goreecloud-website` has been successfully migrated here;
2. static websites embedded in other GoreeCloud application, service, system, design-system, or historical repositories have also been migrated here;
3. all required build, deployment, documentation, automation, and repository references have been updated to use `goreecloud-static-websites`;
4. the migrated sites have passed their required central validation and production verification gates where applicable;
5. obsolete website copies have been retired from their previous repositories; and
6. no required source, asset, configuration, dependency, deployment, or reference remains dependent on `goreecloud-website`.

After these conditions are satisfied, `GoreeCloud/goreecloud-website` MUST be deleted rather than retained as a second website authority.

## Safety boundary

Do not move authenticated application code, backend services, private administrative interfaces, databases, secrets, or non-static runtime code into this repository merely because their owning product also has a public informational website. Only static public website source and website-specific build/validation resources required to reproduce it belong here.
