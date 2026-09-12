# GoreeCloud Roadmap

Canonical static website source for `roadmap.goreecloud.com`.

The Roadmap is a public, evidence-scoped view of GoreeCloud development direction. It does not replace internal project specifications, roadmaps, tasks, release evidence, governance, or change logs, and published dates are not promises.

## Current design and portfolio boundary

- GLAZE UI: **V1.3 / 1.3.0 Stable**
- Exact Stable source revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Consumer state: `source-migrated-rendered-acceptance-pending`
- Canonical static-site repository: `GoreeCloud/goreecloud-static-websites`
- Current authoritative registered package scope: **13 websites**
- Labs: separate candidate scope, not part of the accepted 13-package manifest unless later governed integration is verified

The current public roadmap uses the seven integral platform-system model and the authoritative Suite Inventory rather than publishing fast-changing repository-count snapshots.

## Governed Cloudflare Pages cutover contract

The approved centralized publication contract is:

- Cloudflare Pages project: `goreecloud-roadmap`
- Pages namespace: `goreecloud-roadmap.pages.dev`
- Repository: `GoreeCloud/goreecloud-static-websites`
- Production branch: `main`
- Root directory: repository root (leave the Cloudflare Root directory setting blank)
- Build command: `python3 scripts/build_simple_static_site.py sites/roadmap`
- Build output directory: `sites/roadmap/dist`
- Canonical custom domain: `roadmap.goreecloud.com`
- Legacy deployment/source repository: `GoreeCloud/goreecloud-website`

The Pages project identity and namespace are verified from legacy-repository Cloudflare deployment evidence. The root/build/output settings above match the centralized exact-build workflow and are the governed target for source reconnection; documenting them does not establish that Cloudflare has already been re-pointed to the central repository.

After an independently authorized source cutover, run the Roadmap workflow manually so the allowlisted production verifier can compare the canonical domain against the reviewed `dist/` artifact, required security headers, canonical-host and 404 behavior, and the live Chrome rendering contract. Provider deployment success by itself is not production acceptance.

## Acceptance boundary

The isolated V1.3 build and source validation establish website source/build state only. Representative rendering, accessibility/adaptive behavior, Cloudflare source cutover, deployment, custom-domain verification, and exact production acceptance remain separate gates. The Roadmap must not convert planned work, source progress, or one component's accepted state into a broader GoreeCloud production claim.
