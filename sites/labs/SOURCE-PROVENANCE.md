# Labs source provenance

The GoreeCloud Labs static-site package was introduced in the transitional `GoreeCloud/goreecloud-website` rebuild candidate and then brought under the mandatory `GoreeCloud/goreecloud-static-websites` authority after the original thirteen-site consolidation snapshot.

- Legacy repository: `GoreeCloud/goreecloud-website`
- Legacy branch: `agent/rebuild-public-site-v1-1`
- Legacy path: `sites/labs`
- Legacy Labs tree at migration: `60cf6dbefa274a19bbb7bf3ae75638ac6d20e1c7`
- Legacy candidate head at migration: `7d9b03c90d3ea2c74dacd2f03430a86dd93a3ba6`
- Canonical domain: `labs.goreecloud.com`
- Canonical central path: `sites/labs`

The central package is intentionally self-contained. Shared Website consumer CSS, JavaScript, logo artwork, and the pinned GLAZE build helper required by Labs were copied into `sites/labs` so the canonical package no longer depends on files remaining in the transitional Website repository.

The migration also corrects the product-center inventory from five products to six by adding GoreeCloud Boot using the current authoritative Boot project specification. This does not claim Boot Stable, bootable-release, physical-device-write, or production acceptance.
