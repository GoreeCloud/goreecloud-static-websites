# GoreeCloud Website Release Readiness Checklist

## Purpose

This repository-only checklist defines the minimum evidence required before the GoreeCloud public website is treated as ready for an authorized production release.

It complements automated CI. It does **not** replace the remaining creative-rights/source-publication decision in issue #5, the external Cloudflare `dist/` cutover in issue #6, or human Glaze UI/accessibility acceptance.

Passing every automated check is necessary production evidence, but **passing CI does not itself authorize a merge, repository visibility change, DNS change, Cloudflare configuration change, or production release**.

## Recording convention

This checklist is the reusable procedure, not the historical evidence record. Do not turn the canonical checklist into a running release log or overwrite it with candidate-specific results.

Before formal manual acceptance begins, create a fail-closed working record for the exact candidate SHA:

```bash
python scripts/create_release_evidence.py --commit <40-character-lowercase-git-sha>
```

The generator creates a non-overwriting record under `docs/release-evidence/` using the Central-Time date and the approved technical filename pattern. It binds the record to the supplied full SHA but does **not** fetch evidence, run validation, check acceptance boxes, or authorize any action.

After editing a working evidence record, validate its structural and privacy boundaries with:

```bash
python scripts/validate_release_evidence.py
```

Record manual evidence in that candidate-specific file using Central Time (`America/Chicago`) and the 12-hour time format. Keep the exact Git commit SHA being reviewed so evidence cannot be silently carried forward to a different release candidate.

If the candidate SHA changes after manual acceptance begins, create a new candidate record or explicitly mark the older record Superseded. Do not rename, overwrite, or rewrite an older record to make it appear to cover the new candidate.

## 1. Candidate freeze

Before final acceptance:

- [ ] Identify the exact intended release-candidate commit SHA.
- [ ] Create or identify the candidate-specific working evidence record for that exact SHA.
- [ ] Confirm PR #3 (or its successor release PR) targets `main` and is not merged accidentally.
- [ ] Confirm there are no unintended unreviewed commits after the selected candidate.
- [ ] Confirm the public artifact still comes only from `PUBLIC_FILES` in `scripts/build_public_site.py`.
- [ ] Confirm repository-only `docs/`, `tests/`, `scripts/`, `.github/`, `README.md`, `SECURITY.md`, `LICENSE`, `NOTICE`, and local/development material remain outside `dist/`.

If the candidate SHA changes after manual acceptance begins, rerun the checks affected by the change and record them against the new exact SHA.

## 2. Automated production gates

Run from the repository root on the exact candidate:

```bash
python scripts/validate_workflow_security.py
python scripts/validate_repository_hygiene.py
python scripts/validate_repository_history.py
python scripts/validate_license.py
python scripts/validate_governance_readiness.py
python scripts/validate_security_policy.py
python scripts/validate_privacy_policy.py
python scripts/validate_browser_origin_integrity.py
python scripts/validate_accessibility.py
python scripts/validate_glaze_ui.py
python scripts/validate_app_identity.py
python scripts/validate_public_semantics.py
python scripts/validate_public_surface.py
python scripts/validate_deployment_contract.py
python scripts/validate_performance_budget.py
python scripts/build_public_site.py
python scripts/validate_build_artifact.py
python scripts/verify_remote_deployment.py --check-config
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_repository_guidance.py
python scripts/validate_release_evidence.py
python scripts/validate_site.py
python scripts/validate_resilience.py
node --check js/theme-init.js
node --check js/main.js
```

Required evidence:

- [ ] GitHub Actions is green on the exact candidate SHA.
- [ ] Current-tree repository hygiene passes.
- [ ] Full reachable-history automated preflight passes from a non-shallow checkout.
- [ ] Apache-2.0 source-license, NOTICE boundary, and README licensing guidance remain synchronized and pass `scripts/validate_license.py`.
- [ ] GoreeCloud governance applicability remains valid and passes `scripts/validate_governance_readiness.py`: multi-user is Not Applicable only to the current anonymous static site, while security and Glaze UI remain fully applicable.
- [ ] Every deployable public asset path is present in the rights/provenance inventory.
- [ ] Every deployable public asset byte sequence matches its reviewed Git blob ID in the inventory.
- [ ] The isolated `dist/` artifact contains exactly the expected allowlisted files.
- [ ] Performance budgets pass without waiver.
- [ ] Remote-verifier configuration and dependency-free regression tests pass.
- [ ] Release-evidence records, if present, pass structural/privacy validation without implying substantive acceptance.

Automated history, license-integrity, governance, and rights-inventory checks are prevention/evidence controls, not substitutes for the human publication review required by issue #5.

## 3. Glaze UI visual and interaction acceptance

Review the homepage, Privacy page, Security page, and custom 404 experience. Glaze UI must remain recognizably GoreeCloud while preserving readability, accessibility, privacy, and performance.

### Appearance modes

- [ ] System mode follows the operating-system light/dark preference.
- [ ] Light mode is visually complete and has no dark-only surfaces or unreadable tokens.
- [ ] Dark mode is visually complete and has no light-only surfaces or unreadable tokens.
- [ ] Explicit Light/Dark preference persists locally between reloads.
- [ ] Returning to System removes the explicit override and restores system-controlled behavior.
- [ ] Early theme initialization does not produce an obvious incorrect-theme flash.

### Glaze surfaces and hierarchy

- [ ] Layered surfaces, translucency, borders, shadows, radii, gradients, and spacing follow the shared Glaze UI language.
- [ ] Translucency is selective rather than applied indiscriminately.
- [ ] Primary headings, body text, metadata, cards, actions, and navigation retain clear hierarchy.
- [ ] GoreeCloud branding is consistent across all human-facing pages.
- [ ] Third-party platform/service marks remain supporting content and are not visually presented as GoreeCloud-owned brands.

### Responsive behavior

- [ ] Desktop layout is stable at common wide viewport sizes.
- [ ] Tablet/narrow desktop layouts retain clear hierarchy without horizontal scrolling.
- [ ] Mobile layout remains usable at approximately 320 CSS pixels wide.
- [ ] Navigation opens/closes correctly and does not trap content behind an overlay.
- [ ] Interactive controls have practical touch targets and spacing.
- [ ] Images retain correct proportions and do not cause layout shifts from missing intrinsic dimensions.

## 4. Accessibility acceptance

Automated structural checks are not a formal WCAG conformance claim. Perform human acceptance on the exact candidate.

### Keyboard

- [ ] All meaningful interactive elements are reachable using only the keyboard.
- [ ] The skip link appears when focused and moves focus to the main content.
- [ ] Focus indication remains clearly visible on links, buttons, navigation controls, and theme controls.
- [ ] Focus order follows the visual/logical reading order.
- [ ] Mobile navigation can be opened, used, and closed with the keyboard.
- [ ] Escape closes the mobile navigation where expected and restores useful focus.
- [ ] No keyboard trap is present.

### Zoom and reflow

- [ ] Content remains usable at 200% browser zoom.
- [ ] Critical content and controls remain usable at 400% zoom/reflow where the browser supports it.
- [ ] Text is not clipped or hidden by fixed-height containers.
- [ ] Horizontal scrolling is not required for ordinary page content at narrow/reflowed widths.

### User preferences

- [ ] `prefers-reduced-motion` removes or substantially reduces nonessential motion.
- [ ] Reduced-transparency behavior preserves legibility without relying on glass effects.
- [ ] Increased-contrast mode remains readable.
- [ ] Forced-colors/high-contrast mode preserves meaningful controls, boundaries, and focus.

### Screen reader / semantic review

- [ ] Page title and primary heading accurately identify each page.
- [ ] Main, navigation, and footer landmarks are understandable.
- [ ] Heading levels form a useful document outline.
- [ ] Links and controls have meaningful accessible names out of context.
- [ ] Decorative images do not create noise; informative images have appropriate alternatives.
- [ ] Theme and navigation controls announce useful state/name changes.
- [ ] Custom 404 content clearly communicates that the requested page was not found.

## 5. Progressive enhancement and resilience

- [ ] With JavaScript disabled, primary navigation remains available.
- [ ] With JavaScript disabled, the footer remains useful and the copyright year has a sensible fallback.
- [ ] Theme controls are not shown in a misleading nonfunctional state when JavaScript is unavailable.
- [ ] A nested unknown path shows the custom GoreeCloud 404 experience and returns HTTP 404 after the Cloudflare deployment boundary is verified.
- [ ] Print preview produces a readable document without decorative Glaze effects obscuring content.

## 6. Privacy and browser-origin review

- [ ] No analytics, advertising, fingerprinting, or third-party telemetry has been introduced.
- [ ] Browser-loaded render resources remain first-party/origin-local.
- [ ] Public JavaScript remains non-networked unless the architecture, privacy statement, threat boundary, and validators have been intentionally revised.
- [ ] Theme persistence remains local browser storage only.
- [ ] External links are user-selected destinations rather than hidden render/runtime dependencies.
- [ ] The privacy statement still accurately describes repository-controlled behavior and distinguishes Cloudflare's hosting/network layer.

## 7. Source publication and creative-rights gate — issue #5

The source-code license is established as Apache-2.0 and protected by `scripts/validate_license.py`. That source-license decision does **not** itself authorize repository publication or grant unrestricted rights to GoreeCloud branding or third-party marks.

Do not make the repository public until the remaining issue #5 publication and creative-rights requirements are explicitly resolved.

Required before any repository visibility change:

- [ ] Confirm the reviewed top-level `LICENSE` remains Apache-2.0 and the license-integrity gate passes on the exact candidate.
- [ ] Confirm `NOTICE` still documents the GoreeCloud branding, editorial-content, and third-party-mark boundary.
- [ ] Confirm the copyright holder and notice treatment remain accurate.
- [ ] Complete third-party artwork provenance, applicable logo/trademark terms, and required attribution/notices review for every remaining deployable third-party mark.
- [ ] Confirm family-service cards remain Glaze UI monograms and no third-party family-service logo artwork has silently re-entered `PUBLIC_ASSET_FILES` without review.
- [ ] Confirm `docs/public-asset-inventory.md` reflects the exact deployable artwork paths and reviewed bytes.
- [ ] Complete the final human repository-history and contextual disclosure review.
- [ ] Explicitly record the repository visibility/publication decision.

An upstream software license, an intermediary icon-library license, or a successful automated scan must not be treated as a blanket rights grant for third-party logos.

## 8. Cloudflare isolated-artifact gate — issue #6

The repository-side build is not enough. Cloudflare must actually publish the isolated `dist/` artifact.

Required Pages settings:

- Production branch: `main`
- Framework preset: `None`
- Build command: `python scripts/build_public_site.py`
- Build output directory: `dist`
- Root directory: blank

After those settings are deliberately applied and a new branch preview is built, run from the **exact checked-out candidate** whose preview is being reviewed:

```bash
python scripts/build_public_site.py
python scripts/validate_build_artifact.py
python scripts/verify_remote_deployment.py --target branch-preview
```

The remote verifier now performs two distinct checks against that fixed branch-preview target:

1. deployment semantics/security behavior (status, MIME types, headers, indexing behavior, `security.txt`, custom 404, and repository-only path isolation); and
2. **candidate content integrity** for every fetchable path in the authoritative `PUBLIC_FILES` allowlist.

Candidate integrity compares the deployed response bytes with the local candidate source bytes. The Cloudflare `_headers` file is the only allowlisted source excluded because Cloudflare consumes it as deployment configuration rather than exposing it as a public resource. Redirect destinations are validated against the fixed GoreeCloud host allowlist before they are followed.

Acceptance:

- [ ] Fresh post-cutover branch preview deploys successfully.
- [ ] Branch-preview verifier exits successfully when run from the exact candidate checkout.
- [ ] Every fetchable allowlisted public resource is byte-identical to that candidate.
- [ ] No verifier redirect leaves the reviewed GoreeCloud host allowlist.
- [ ] Preview publishes `X-Robots-Tag: noindex`.
- [ ] Required security/privacy headers reach the deployed HTTP surface.
- [ ] Repository-only paths return 404.
- [ ] `security.txt` identity, cache policy, and expiry checks pass.
- [ ] Nested custom 404 behavior passes.

A preview produced before the `dist/` configuration change, or a preview whose public bytes do not match the exact reviewed candidate, does not satisfy issue #6.

## 9. Release authorization

Only after sections 1–8 are satisfied or an explicitly documented exception has been approved:

- [ ] Confirm the final exact SHA again.
- [ ] Confirm final CI is green.
- [ ] Confirm final preview evidence corresponds to that exact SHA and its fetchable public bytes.
- [ ] Confirm issue #5 is resolved before any repository-publication action.
- [ ] Confirm issue #6 is resolved before treating `dist/` isolation as externally enforced.
- [ ] Obtain explicit authorization for merge/production release.
- [ ] Treat repository visibility, DNS, and production routing as separate explicit changes rather than implied consequences of a merge.

## 10. Post-release verification

After an authorized production release, run from the **exact released source candidate**:

```bash
python scripts/verify_remote_deployment.py --target production
```

Confirm:

- [ ] Canonical production content is reachable at `https://www.goreecloud.com/`.
- [ ] Apex routing resolves permanently to the canonical `www` host as intended.
- [ ] Production does **not** publish `X-Robots-Tag: noindex`.
- [ ] Every fetchable allowlisted public resource is byte-identical to the released candidate.
- [ ] Required public resources return expected status, MIME type, and identifying content.
- [ ] Repository-only paths remain unavailable.
- [ ] Security/privacy headers match the reviewed contract.
- [ ] `security.txt` remains valid and has more than the required freshness window remaining.
- [ ] Custom nested-path 404 behavior remains correct.
- [ ] Light, Dark, and System appearance modes still behave correctly on the production origin.

Record any production-only discrepancy as a release defect rather than normalizing it into the repository documentation.

## Release boundary

This checklist is intentionally fail-closed. An unchecked creative-rights/publication requirement, an unverified Cloudflare `dist/` boundary, a red automated production gate, a deployed-byte mismatch, or a material manual Glaze UI/accessibility defect means the release candidate is not yet fully accepted.

The checklist itself is repository-only documentation and must never be copied into the public `dist/` artifact.
