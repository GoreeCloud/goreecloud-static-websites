# GoreeCloud Main Website

Canonical source for `https://www.goreecloud.com/`.

## Repository contract

- Canonical repository: `GoreeCloud/goreecloud-static-websites`
- Site root: `sites/main`
- Production branch target: `main`
- Build command: `python sites/main/scripts/build_public_site.py`
- Build output directory: `sites/main/dist`
- Custom domain: `www.goreecloud.com`
- Transitional migration source: `GoreeCloud/goreecloud-website`

The current canonical candidate is rebuilt as a controlled **GLAZE UI V1.1 / 1.1.0** consumer. The build pins immutable promotion revision `15cc76d2bcd4065552dc31c77145b63f34d9e7b2` and publishes the generated GLAZE bundle same-origin under `assets/glaze-v1/`.

The immutable 1.1.0 Stable bundle currently contains one known dangling `glaze-v1.candidate.css` import. The shared central build tooling proves the exact dependency still returns HTTP 404 and removes only that single directive from the generated artifact. This bounded workaround is not GLAZE consumer-conformance or production acceptance evidence.

The rebuilt Main source uses one responsive V1.1 shell across the homepage, repository focus page, privacy page, security page, and 404 surface. The repository focus reflects the six current GoreeCloud Labs Development products: Home Security, Home, AI, Containers, Code, and Boot. Product source or a public status label does not imply Stable or production acceptance.

Only an explicit allowlist of reviewed public files plus the pinned generated GLAZE bundle can enter `dist/`; historical source assets, migration provenance, repository documentation, validators, and other repository-only material are excluded from publication.

Cloudflare Pages source cutover, custom-domain deployment equivalence, DNS/TLS verification, responsive/human visual acceptance where required, indexing/deployment review, GLAZE consumer acceptance, and legacy-source retirement remain separate gates. Central source validation alone does not establish any of those production outcomes.
