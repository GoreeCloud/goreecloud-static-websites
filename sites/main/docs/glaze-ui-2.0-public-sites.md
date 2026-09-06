# Glaze UI 2.0.0 public-site adoption

- Stable target: **2.0.0**
- Canonical repository: `GoreeCloud/goreecloud-glaze-ui`
- Stable promotion reference: `ff3fff4306bd53ea9c0715a7c0d64265bb038617`
- Surfaces: Main, Projects, Roadmap, Blog, Archive
- Delivery: same-origin CSS per independently deployed Cloudflare Pages surface
- Runtime third-party UI dependencies: none

The integration maps the web-relevant Glaze UI 2.0 material and interaction contract onto the GoreeCloud public portfolio: Soft Glaze navigation surfaces, Glaze material cards and summaries, Navigation Capsule behavior, 48px interaction floors, connected press/hover transformation, focus-visible semantics, reduced-motion and reduced-transparency behavior, increased-contrast support, forced-colors support, and non-backdrop fallbacks.

The migration preserves each site’s existing information architecture, product identity, privacy/security headers, and evidence-authority boundaries. Glaze UI changes presentation and interaction; it does not manufacture application, Privacy Shield, Wardveil Security, Everkeep, Mesh, or GoreeCloud Identity state.

Source conformance and rendered deployment acceptance are separate. A site is not used as proof of production-rendered 2.0 conformance until its Cloudflare Pages preview/production verification passes for the exact reviewed revision.