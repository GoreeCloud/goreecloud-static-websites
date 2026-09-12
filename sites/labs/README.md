# GoreeCloud Labs — Public Development Center

Canonical centralized static source for `labs.goreecloud.com`.

## Publication contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Production branch target: `main`
- Site root: `sites/labs`
- Build command: `python3 build.py`
- Build output directory: `dist`
- Intended custom domain: `labs.goreecloud.com`
- Current design target: GLAZE UI V1.3 / 1.3.0

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

This site is reconciled against:

- `Inventory — Suite Applications` (authoritative current 45-product / 9-group portfolio record),
- `Inventory — GitHub Repositories` (verified owned-repository inventory),
- applicable project specifications for specialized products and services,
- the canonical Glaze UI lifecycle registry for the current design target.

## Indexing boundary

The rebuilt central candidate remains `noindex,nofollow` until central source integration, Cloudflare source cutover, exact deployed-revision verification, and public production acceptance are complete. Indexing release is a separate gate.
