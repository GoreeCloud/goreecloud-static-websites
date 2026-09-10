# GoreeCloud Blog

Canonical static website source for `blog.goreecloud.com`.

The Blog is GoreeCloud's public editorial surface for development writing, homelab lessons, architecture explanations, product and project updates, privacy, security, continuity, open-source development, self-hosting, and GLAZE UI topics. It summarizes public-safe information; authoritative project specifications, repositories, policies, standards, inventories, and evidence remain the controlling records.

## Current design target

- GLAZE UI: **V1.3 / 1.3.0 Stable**
- Canonical source revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Official Stable entrypoint: `css/glaze-v1.3.0.css`
- Consumer state: `source-migrated-rendered-acceptance-pending`

The isolated build vendors only the recursive CSS dependency closure reachable from that exact Stable entrypoint. Analytics, advertising, behavioral tracking, remote fonts, and unreviewed external runtime dependencies remain excluded.

## Acceptance boundary

Source/build migration, rendered visual review, accessibility/adaptive acceptance, Cloudflare source cutover, custom-domain verification, and exact production acceptance are separate gates. Historical Blog entries may preserve superseded decisions when clearly identified as history, but the landing page must not present obsolete versions, repository counts, or platform models as current state.
