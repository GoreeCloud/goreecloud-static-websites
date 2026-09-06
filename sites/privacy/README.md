# GoreeCloud Privacy Shield Static Website

Canonical source repository: `GoreeCloud/goreecloud-static-websites`

- Site root: `sites/privacy`
- Public source root: `sites/privacy/website`
- Canonical domain: `privacy.goreecloud.com`
- Legacy source repository: `GoreeCloud/goreecloud-privacy-shield`
- Reviewed source commit: `345b4bd42aaed09afb0e2384c421aab8661f1d5c`
- Exact legacy website tree: `467d95f979a18e13b83ffa7dde6a68165720ebad`
- Build command: `python sites/privacy/website/build.py`
- Build output: `sites/privacy/website/dist`

This package contains only the Privacy Center public static source, deterministic build/validation contract, and approved public Privacy Shield icon. Generated `website/dist`, Privacy Shield runtime code, adapters, internal contracts, configuration, and service implementation remain outside static-site authority.

The current central candidate is a controlled **GLAZE UI V1.1 / 1.1.0** consumer. Its isolated build uses the shared immutable source revision `15cc76d2bcd4065552dc31c77145b63f34d9e7b2`, publishes the generated bundle same-origin under `assets/glaze-v1/`, and applies only the documented bounded workaround for the known immutable Stable dangling import. That workaround is not consumer-conformance or production acceptance evidence.

Privacy Center content preserves Privacy Shield as the platform privacy authority while keeping GoreeCloud Manager, Wardveil Security, Everkeep, Glaze UI, GoreeCloud Mesh, and GoreeCloud Identity as separate Integral Platform Systems with their own authority and evidence.

Production source cutover, Cloudflare Pages configuration, DNS/HTTPS verification, rendered/human acceptance where required, formal GLAZE consumer acceptance, Privacy Shield production acceptance, and legacy-source retirement remain separate gates.
