# GoreeCloud Labs — Public Development Center

Canonical centralized static source for `labs.goreecloud.com`.

## Publication contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Production branch target: `main`
- Site root: `sites/labs`
- Build command: `python3 build.py`
- Build output directory: `dist`
- Intended custom domain: `labs.goreecloud.com`
- Current publication target: **GLAZE UI V1.4 / 1.4.0 Stable**
- Exact Glaze revision: `84cb3db4884042f0fa25ed6d475a127fb110f596`
- Exact Stable entrypoint: `glaze-v1.4.0.css`
- Entrypoint Git blob: `d48a9bc317090d152799769271de0fb4325494c4`
- Consumer state: `build-migrated-rendered-acceptance-pending`

The retained Labs source template preserves its earlier **GLAZE UI V1.3 / 1.3.0** marker as migration provenance. `build.py` deterministically produces the current V1.4 publication identity, adds the exact V1.4 Stable stylesheet dependency closure, and keeps source/build acceptance distinct.

## Product boundary

Labs is the public GoreeCloud development center. It does **not** replace `suite.goreecloud.com`, the authoritative 45-product Suite directory, and it does not redefine lifecycle status for any product.

The current Labs presentation highlights 27 source-tracked development workstreams across six engineering lanes:

1. Intelligence and developer tools — AI, Index, Code, Terminal.
2. Home and edge — Home, Home Security, Router OS, Boot.
3. Core platform services — Containers, App Store, Sync, Gateway, Network, DNS, Monitor.
4. Native product rebuilds — Search, Browser, Photos, Video, Music, Messenger, Launcher.
5. Emerging personal experiences — Health, Reader, Social, Location.
6. Browser extension ecosystem — Firefox Extensions.

The complete Suite portfolio, detailed implementation status, and release acceptance remain controlled by the authoritative Suite inventory and each project's own specification/repository evidence. Labs must not infer Stable or production status from repository existence.

The seven Integral Platform Systems remain separate from the 27 Labs workstreams and from the 45-product Suite count: GoreeCloud Manager, GoreeCloud Identity, Glaze UI, Wardveil Security, Privacy Shield, Everkeep, and GoreeCloud Mesh.

## Source authority

This site is reconciled against the authoritative Suite inventory, verified owned-repository inventory, applicable project specifications, and the canonical Glaze UI lifecycle registry. Publication content must remain bounded by those sources and must not strengthen project lifecycle claims beyond verified evidence.

## Build and acceptance

From `sites/labs`:

```bash
python3 validate.py
GLAZE_UI_SOURCE=/path/to/goreecloud-glaze-ui python3 build.py
python3 validate.py dist
python3 browser_smoke.py
python3 verify_v14_public_deployment.py --check-config
```

The browser gate rebuilds and validates the exact static artifact, then exercises the site at 1180, 768, 390, and 320 CSS pixels with filter controls, System/Light/Dark behavior, viewport containment, image loading, interaction-target sizing, and responsive workstream layouts.

Canonical production verification is deliberately separate. After the Cloudflare Pages source has been independently switched to the centralized publication contract, run:

```bash
python3 build.py
python3 validate.py dist
python3 verify_v14_public_deployment.py --target production
python3 browser_production_smoke.py
```

The V1.4 production verifier is fixed to `https://labs.goreecloud.com/`. It compares every fetchable built artifact byte-for-byte with production, validates committed security headers, canonical host behavior, true 404 output, the exact V1.4 publication markers, and Cloudflare delivery. The production browser gate independently reruns responsive/interaction acceptance against the live canonical hostname.

The dedicated GitHub workflow runs source/build/browser verification for ordinary pull requests and pushes. Live canonical-host checks run only through `workflow_dispatch`, so repository CI cannot silently convert a source change into production acceptance.

## Indexing boundary

The rebuilt central source remains `noindex,nofollow` until Cloudflare source cutover, exact deployed-revision verification, public production acceptance, and an independently authorized indexing release are complete. Indexing release is a separate gate and must not be inferred merely from a successful deployment.
