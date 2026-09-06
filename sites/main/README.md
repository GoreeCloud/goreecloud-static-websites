# GoreeCloud Main Website

Canonical source repository: `GoreeCloud/goreecloud-static-websites`

Site root: `sites/main`
Canonical domain: `www.goreecloud.com`
Legacy source repository: `GoreeCloud/goreecloud-website`
Reviewed legacy revision: `18f5276d21b8eb3b55adc18e00e88aa11b6edfd8`

This package contains the main GoreeCloud public website source plus the build, rendering, validation, data-manifest, and test inputs required to reproduce its isolated public artifact. It intentionally excludes the legacy repository's `.github/` governance, the already separately centralized `sites/` subtree, generated `dist/`, and the legacy repository Platform Contract.

Production deployment cutover remains a separate acceptance gate. The presence of this source in the canonical repository does not itself prove that Cloudflare Pages, DNS, HTTPS, or production traffic has been cut over.
