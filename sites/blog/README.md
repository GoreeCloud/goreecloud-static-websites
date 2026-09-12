# GoreeCloud Blog

Canonical static website source for `blog.goreecloud.com`.

The Blog is GoreeCloud's public editorial surface for development writing, homelab lessons, architecture explanations, product and project updates, privacy, security, continuity, open-source development, self-hosting, and GLAZE UI topics. It summarizes public-safe information; authoritative project specifications, repositories, policies, standards, inventories, and evidence remain the controlling records.

## Current design target

- GLAZE UI: **V1.3 / 1.3.0 Stable**
- Canonical source revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Official Stable entrypoint: `css/glaze-v1.3.0.css`
- Consumer state: `source-migrated-rendered-acceptance-pending`

The isolated build vendors only the recursive CSS dependency closure reachable from that exact Stable entrypoint. Analytics, advertising, behavioral tracking, remote fonts, and unreviewed external runtime dependencies remain excluded.

## Governed Cloudflare Pages cutover contract

The approved centralized publication contract is:

- Cloudflare Pages project: `goreecloud-blog`
- Pages namespace: `goreecloud-blog.pages.dev`
- Repository: `GoreeCloud/goreecloud-static-websites`
- Production branch: `main`
- Root directory: repository root (leave the Cloudflare Root directory setting blank)
- Build command: `python3 scripts/build_simple_static_site.py sites/blog`
- Build output directory: `sites/blog/dist`
- Canonical custom domain: `blog.goreecloud.com`
- Legacy deployment/source repository: `GoreeCloud/goreecloud-website`

The Pages project identity and namespace are verified from legacy-repository Cloudflare deployment evidence. The root/build/output settings above match the centralized exact-build workflow and are the governed target for source reconnection; documenting them does not establish that Cloudflare has already been re-pointed to the central repository.

After an independently authorized source cutover, run the Blog workflow manually so the allowlisted production verifier can compare the canonical domain against the reviewed `dist/` artifact, required security headers, canonical-host and 404 behavior, and the live Chrome rendering contract. Provider deployment success by itself is not production acceptance.

## Acceptance boundary

Source/build migration, rendered visual review, accessibility/adaptive acceptance, Cloudflare source cutover, custom-domain verification, and exact production acceptance are separate gates. Historical Blog entries may preserve superseded decisions when clearly identified as history, but the landing page must not present obsolete versions, repository counts, or platform models as current state.
