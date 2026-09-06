# GoreeCloud Website — Glaze UI 2.1.0 Conformance

## Conformance record

- Target Glaze UI version: **2.1.0**
- Canonical design-system repository: `GoreeCloud/goreecloud-glaze-ui`
- Stable promotion reference used for this alignment: `c49113eb8b93c267613fdf1bbca1f814495acad7`
- Conformance state: **Source-aligned — Glaze UI 2.1.0 Stable web contract prepared across all independently deployed GoreeCloud website surfaces in this repository**
- Rendered/production acceptance: **Separate gate; preview and production evidence must pass before the deployment is used as proof of portfolio-wide rendered conformance.**

## Scope

This record covers the Main, Projects, Roadmap, Blog, and Archive public surfaces. Each deployment carries a same-origin Glaze UI 2.1.0 web layer so design-system availability does not depend on another GoreeCloud domain at runtime.

The Main deployment uses the isolated build pipeline to normalize all deployable HTML onto the current Stable contract. Projects, Roadmap, Blog, and Archive carry their own same-origin 2.1.0 asset because they are independently deployed Cloudflare Pages surfaces.

## Glaze UI 2.1 web contract

The current source target follows the 2.1 material hierarchy: Canvas → Surface → Soft Glaze → Glaze → Deep Glaze → Live Glaze. The governing material rule is **Content is solid. Interaction is glazed.** Durable reading, repository, project, timeline, policy, and status content therefore resolves to solid Surface material, while navigation, controls, focal hero interaction, and transient/live surfaces may use appropriate glaze levels.

The web contract supports Clear, Balanced, and Solid clarity; Comfortable, Standard, Compact, and Far View density; a 48px general interaction floor; a 56px Touch Assistance floor; large-text compact-density fallback; keyboard and pointer interaction; responsive navigation; and safe-area-aware compact layouts.

## Accessibility and resilience

Reduced Motion removes nonessential transformation and travel. Reduced Transparency resolves optical material to solid hierarchy. Increased Contrast strengthens borders and non-color cues. Forced Colors preserves operability without authored glass effects. Large Text cannot reduce Compact controls below the normal touch floor. Browsers without backdrop-filter support receive opaque surfaces. Deterministic reduced-material/performance modes can remove blur and depth without changing task or state semantics.

## Privacy boundary

The design-system layer is served same-origin. It adds no analytics, advertising, trackers, remote fonts, runtime UI framework, or cross-domain stylesheet dependency.

## Authority boundary

Glaze UI controls presentation and interaction only. Public presentation cannot upgrade application, Privacy Shield, Wardveil Security, Everkeep, Mesh, or GoreeCloud Identity implementation/evidence state.

## Release boundary

Glaze UI 2.1.0 is the current Stable design-system target. Glaze UI 2.0.0 and 1.x are historical baselines and must not remain active production dependencies after these public surfaces earn 2.1 deployment acceptance. Historical references may remain only when explicitly presented as dated history rather than current guidance.

## Exceptions

No production Glaze UI exception is recorded for these website surfaces. Each independently deployed surface still requires its own rendered/production acceptance for the exact deployed revision.
