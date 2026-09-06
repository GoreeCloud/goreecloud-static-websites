# GoreeCloud Everkeep Static Website

Canonical source repository: `GoreeCloud/goreecloud-static-websites`

- Site root: `sites/everkeep`
- Public source root: `sites/everkeep/website`
- Canonical domain: `everkeep.goreecloud.com`
- Legacy source repository: `GoreeCloud/goreecloud-everkeep`
- Reviewed source commit: `684ee5567392446e00df8e7f94139db51704a9e3`
- Exact legacy `website/` tree: `82263e30f90810133b7f8ad0847efe7bce966798`
- Build command: `python sites/everkeep/scripts/build_public_site.py`
- Build output: `sites/everkeep/website/dist`

This package contains the Continuity Center public static source, approved Everkeep public mark, deterministic public-site build and validation scripts, and indexing/security metadata. Generated `website/dist`, Everkeep runtime/service code, recovery/failover implementation, contracts, persistence, continuity-control logic, and unrelated repository governance remain outside static-site authority.

The current central candidate is a controlled **GLAZE UI V1.1 / 1.1.0** consumer. Its build uses immutable source revision `15cc76d2bcd4065552dc31c77145b63f34d9e7b2`, publishes the generated bundle same-origin under `assets/glaze-v1/`, and applies only the documented bounded workaround for the known immutable Stable dangling import. That workaround is not consumer-conformance or production acceptance evidence.

Everkeep remains the continuity/recovery/preservation authority. The public website keeps simulation-only recovery behavior, source/runtime evidence, production recovery effects, and production acceptance as distinct states. GoreeCloud Manager, Privacy Shield, Wardveil Security, Glaze UI, GoreeCloud Mesh, and GoreeCloud Identity retain their own authorities.

Cloudflare Pages source cutover, DNS/HTTPS validation, rendered/human acceptance where required, formal GLAZE consumer acceptance, production recovery/failover acceptance, and legacy-source retirement remain separate gates.
