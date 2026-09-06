# GoreeCloud Website Release Evidence Record Template

## Purpose

This repository-only template is used to create a historical validation record for one exact GoreeCloud website release candidate.

It complements `docs/release-readiness-checklist.md`. The checklist defines what must be reviewed; a completed evidence record documents what was actually reviewed, what evidence was observed, what remained unresolved, and whether the candidate was accepted or rejected.

A completed record must describe only the candidate identified by its exact Git commit SHA. Evidence from one candidate must not be silently reused after the candidate changes.

## Record handling

- Create a new record for each materially reviewed release candidate rather than overwriting an older record.
- Use Central Time (`America/Chicago`) and the 12-hour time format for human-recorded timestamps.
- Keep the exact 40-character Git commit SHA in the record.
- Record public-safe identifiers such as GitHub Actions run IDs and approved preview URLs where useful.
- Do not place credentials, tokens, private keys, private IP addresses, private hostnames, internal-only service URLs, private infrastructure diagrams, or other sensitive GoreeCloud information in this record.
- Do not paste raw logs merely to increase detail. Record the relevant result and retain sensitive or high-volume evidence in its appropriate protected system.
- A checksum, Git blob ID, CI result, preview deployment, or successful command is evidence for the specific property it validates; it is not proof of unrelated security, rights, usability, accessibility, or production-readiness claims.
- Preserve rejected and superseded records when they retain useful historical accountability. Mark their final disposition clearly instead of rewriting them to look successful.
- This template and completed repository evidence records are source-repository documentation and must remain outside the website `dist/` artifact.

Recommended record filename after the repository-publication model is approved:

`docs/release-evidence/YYYY-MM-DD-<short-commit>-release-evidence.md`

Before issue #5 is resolved, consider whether a completed record contains information appropriate for future source-repository publication. If not, retain the sensitive supporting evidence in an approved private record and keep only public-safe conclusions here.

---

## 1. Candidate identity

- Review date and time:
- Exact candidate commit (40-character SHA):
- Pull request:
- Base branch:
- Reviewer or reviewer role:
- GitHub Actions run ID:
- Cloudflare preview URL reviewed:
- Stable branch-preview hostname:
- Intended release/package identifier, if applicable:

### Candidate freeze result

- [ ] Exact candidate SHA confirmed.
- [ ] No later unreviewed commit is being treated as covered by this record.
- [ ] Pull request still targets the intended base branch.
- [ ] Candidate has not been merged or promoted unintentionally.

Evidence/notes:


## 2. Automated validation evidence

Record the results from the exact candidate.

- Workflow supply-chain validation:
- Current-tree repository hygiene:
- Reachable-history preflight:
- Security reporting / `security.txt` validation:
- Privacy validation:
- Browser-origin integrity:
- Structural accessibility validation:
- Glaze UI contract validation:
- Application identity validation:
- Public semantics/surface validation:
- Cloudflare deployment-contract validation:
- Performance budget:
- Isolated artifact build:
- Isolated artifact validation:
- Remote-verifier configuration:
- Dependency-free tests:
- Repository-guidance validation:
- Site validation:
- Resilience validation:
- JavaScript syntax validation:

### Artifact identity

- Public file count:
- Public artifact byte size:
- Public artifact KiB size:
- Deployable artwork count:
- Asset-inventory/content-identity validation result:

### Automated gate result

- [ ] All required automated gates passed on the exact candidate.
- [ ] Any failure or exception is documented below instead of being silently ignored.

Evidence/notes:


## 3. Glaze UI visual and interaction acceptance

Review the homepage, Privacy, Security, and custom 404 surfaces using `docs/release-readiness-checklist.md`.

- Desktop browser/OS reviewed:
- Mobile browser/device reviewed:
- System appearance result:
- Light appearance result:
- Dark appearance result:
- Responsive desktop/tablet result:
- Narrow/mobile result:
- Navigation interaction result:
- Theme persistence/first-paint result:
- Glaze surfaces/hierarchy result:
- Third-party mark presentation result:

### Glaze UI acceptance

- [ ] Accepted for this exact candidate.
- [ ] No material visual or interaction defect remains hidden by automated validation.

Evidence/defects/notes:


## 4. Accessibility acceptance

Automated checks are regression controls and do not replace human acceptance.

- Keyboard-only navigation result:
- Skip-link/focus result:
- Mobile-navigation keyboard/Escape result:
- 200% zoom result:
- 400% zoom/reflow result:
- Reduced-motion result:
- Reduced-transparency result:
- Increased-contrast result:
- Forced-colors/high-contrast result:
- Screen reader or semantic review method:
- Screen reader/semantic result:
- Touch-target/mobile accessibility result:

### Accessibility acceptance

- [ ] Human acceptance completed for this exact candidate.
- [ ] No formal WCAG conformance claim is being inferred solely from this record or CI.

Evidence/defects/notes:


## 5. Progressive enhancement, resilience, privacy, and origin boundary

- JavaScript-disabled navigation result:
- JavaScript-disabled fallback-content result:
- Nonfunctional-control suppression result:
- Print-preview result:
- Custom nested 404 result:
- Analytics/advertising/telemetry review result:
- First-party/origin-local resource review result:
- Browser JavaScript network-boundary result:
- Theme local-storage behavior result:
- Privacy-statement synchronization result:

### Boundary acceptance

- [ ] Progressive enhancement and resilience accepted.
- [ ] Privacy/origin behavior accepted.

Evidence/notes:


## 6. Source publication and creative-rights gate — issue #5

- Issue #5 state at review time:
- Source-code license decision:
- Top-level `LICENSE` validation:
- GoreeCloud content/branding reuse boundary:
- Copyright holder/notice treatment:
- Third-party artwork provenance/terms review:
- Public asset inventory state:
- Final human repository-history/contextual disclosure review:
- Repository visibility decision:

### Issue #5 gate

- [ ] Issue #5 is resolved for the actions being authorized.
- [ ] No source-publication or third-party-rights claim exceeds the evidence actually reviewed.

If not complete, record the blocker rather than marking the candidate fully accepted.

Evidence/blockers/notes:


## 7. Cloudflare isolated-artifact gate — issue #6

Record only post-cutover evidence for the isolated `dist/` configuration.

- Issue #6 state at review time:
- Production branch setting:
- Framework preset:
- Build command:
- Build output directory:
- Root directory:
- Fresh post-cutover preview URL:
- Branch-preview verifier result:
- Preview `X-Robots-Tag: noindex` result:
- Deployed security/privacy-header result:
- Repository-only path isolation result:
- Deployed `security.txt` result:
- Nested custom 404 result:

### Issue #6 gate

- [ ] Cloudflare is verified to build and publish the exact isolated `dist/` artifact.
- [ ] Fresh post-cutover remote verification passed.

A successful preview generated before the `dist/` configuration change does not satisfy this gate.

Evidence/blockers/notes:


## 8. Exceptions and accepted limitations

Do not use this section to normalize an avoidable failed gate. A material exception must identify the requirement, reason, risk, compensating control, approver, review/expiration condition, and corrective plan.

- Exception identifier:
- Requirement affected:
- Reason:
- Risk:
- Compensating control:
- Approver:
- Approval date/time:
- Review or expiration condition:
- Corrective plan:
- Accepted limitation:

If no exception exists, record: `None`.


## 9. Release authorization

Passing CI or completing this record does not itself authorize a merge, repository visibility change, DNS change, Cloudflare configuration change, or production deployment.

- Final exact SHA re-confirmed:
- Final CI run re-confirmed:
- Final preview corresponds to exact SHA:
- Issue #5 disposition:
- Issue #6 disposition:
- Manual Glaze UI acceptance disposition:
- Manual accessibility acceptance disposition:
- Merge authorization:
- Production-release authorization:
- Repository-visibility authorization, if separately applicable:
- DNS/routing authorization, if separately applicable:
- Authorizing person/role:
- Authorization date/time:

### Pre-release decision

Select exactly one final candidate disposition:

- [ ] ACCEPTED — candidate may proceed only within the explicitly authorized actions above.
- [ ] BLOCKED — candidate must not proceed until listed blockers are resolved.
- [ ] REJECTED — candidate is not suitable for release.
- [ ] SUPERSEDED — a newer candidate replaced this evidence record.

Decision rationale/blockers:


## 10. Post-release production verification

Complete only after an explicitly authorized production release.

- Production verification date/time:
- Production verifier result:
- Canonical `www` content result:
- Apex-to-`www` routing result:
- Production indexing-header result:
- Public-resource status/MIME/identity result:
- Repository-only path isolation result:
- Security/privacy-header result:
- `security.txt` freshness/result:
- Nested custom 404 result:
- System/Light/Dark production appearance result:
- Production-only discrepancy found:

### Post-release result

- [ ] Production verification passed without a material discrepancy.
- [ ] Any production-only discrepancy is recorded as a release defect rather than rewritten as intended behavior.

Evidence/defects/follow-up:


## Final record boundary

This record documents evidence and decisions for one exact candidate. It does not create policy, change GoreeCloud standards, grant third-party rights, authorize actions not explicitly recorded above, or prove properties that were not actually tested.

Historical evidence must remain distinguishable from current state. If the candidate, deployment configuration, license state, public artifact, or production environment changes materially, create or update the appropriate new validation record rather than silently carrying forward this acceptance.