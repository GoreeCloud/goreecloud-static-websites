# GoreeCloud Public Websites — Feature Roadmap

**Status:** Active roadmap control  
**As of:** 2026-09-15  
**Authoritative project record:** Project Record — Public Websites  
**Canonical repository:** GoreeCloud/goreecloud-static-websites  
**Drive control:** `GoreeCloud/Feature Roadmap/GoreeCloud Public Websites/FEATURE-ROADMAP.md`

## Purpose

This file is the repository-side feature roadmap control for GoreeCloud Public Websites. It records current planned and recommended feature work without replacing the authoritative project record, implementation evidence, release gates, or GoreeCloud Tasks Management.

## Roadmap

| ID | Feature / obligation | Priority | Current state |
| --- | --- | --- | --- |
| PW-001 | Reconcile all fourteen static website packages on authoritative `main` to the current GLAZE UI 1.4.1 Stable contract, with per-site evidence and acceptance. | High | In progress / evidence-gated |
| PW-002 | Complete the provider-side Labs deployment cutover from the accepted central source and exact production acceptance. | High | Unified `/labs/` path live; per-site exact production acceptance and legacy retirement pending |
| PW-003 | Complete the Manager public informational website deployment cutover while preserving the separate `manager.goreecloud.com` authenticated application boundary. | High | Unified `/manager/` path live; `manage.goreecloud.com` redirect verified and `manager.goreecloud.com` application boundary preserved; per-site exact production acceptance and legacy retirement pending |
| PW-004 | Require reviewed source/build, rendered-accessibility, deployment, and exact deployed-revision evidence before recording new production acceptance. | High | Ongoing release gate |
| PW-005 | Migrate public informational/static websites to `https://www.goreecloud.com/<website-slug>`, including `/glaze-ui`, `/wardveil`, `/suite`, `/labs`, and `/identity`; reserve `https://<application>.goreecloud.com/` for the actual web application. Preserve required compatibility and require per-site production verification before acceptance. | High | In progress / unified www production cutover and 13 legacy informational-host redirects verified; per-site metadata, GLAZE UI 1.4.1, rendered/accessibility, exact-revision acceptance, and legacy retirement pending |
| PW-006 | Add reusable commerce capabilities for applicable GoreeCloud websites, including product and service catalogs, product/service detail pages, customer reviews, testimonials, product/service Q&A, shopping cart, checkout, order confirmation, and account-linked order history where applicable. The commerce architecture should remain reusable across GoreeCloud websites rather than duplicating independent cart/order implementations per site. | Unprioritized | Planned / not implemented or production-verified |
| PW-007 | Use **Stripe and PayPal as the preferred external payment-processing integrations** for GoreeCloud website commerce instead of building a GoreeCloud payment processor. GoreeCloud should own the storefront, cart, order, customer, tax/shipping/discount orchestration, payment-status model, and branded checkout experience while delegating sensitive payment processing to the selected providers. The implementation must avoid storing raw card numbers or CVVs, verify provider webhooks/events before changing paid/refunded state, keep provider identifiers and payment metadata separated from sensitive credentials, and use a provider-neutral internal payment abstraction so Stripe, PayPal, or future approved providers can be integrated without rebuilding the commerce core. Provider-supported methods such as cards, eligible digital wallets, PayPal checkout, subscriptions, invoices, and refunds may be enabled only when supported, deliberately configured, and verified for the applicable GoreeCloud site. | Unprioritized | Planned requirement / no implementation or payment-provider production acceptance verified |

## Current evidence baseline

Authoritative `main` registers fourteen centralized static website packages, and the Glaze UI lifecycle registry identifies 1.4.1 as current Official Stable. Source-side URL namespace preparation was implemented through PR #96 at merge revision `6a5c70292857ea3ccbc922585f7a905195cd92bb`. The existing `goreecloud-website` Cloudflare Pages project now builds the unified repository-root www namespace with `python3 scripts/build_www_namespace.py` and output directory `dist`, and public readback confirms all fourteen governed `www.goreecloud.com` path destinations are reachable.

The account-level Bulk Redirect Rule `goreecloud-website-url-migration` is enabled against `goreecloud_website_url_migration` with 13 permanent legacy informational-host redirects. The original 12 legacy hosts are verified, and `manage.goreecloud.com` now redirects to `https://www.goreecloud.com/manager/` with query strings preserved. PR #98 merged as main revision `6029da3313b570cc730ebf24c475eda905f5064e` to distinguish the legacy Manager informational hostname from `manager.goreecloud.com`, which remains reserved for the actual Manager application, and Cloudflare Pages successfully deployed that exact revision to `goreecloud-website`.

Final migration acceptance remains open because some mounted sites still expose stale canonical/design-system metadata, current GLAZE UI 1.4.1 per-site conformance is not yet established, and per-site rendered/accessibility/indexing/exact deployed-revision acceptance, old Pages-project/reference cleanup, nested legacy-path compatibility where applicable, and legacy-source retirement remain pending.

PW-006 and PW-007 record planned commerce and payment-processing requirements only. Their presence in this roadmap is not evidence that commerce, checkout, Stripe, PayPal, subscriptions, refunds, webhooks, wallets, order processing, or related production controls have been implemented, configured, certified, or accepted.

## Commerce and payment architecture requirements

The planned commerce layer should separate GoreeCloud-owned commerce state from provider-owned payment processing. Product/service catalog data, carts, orders, customer-facing status, shipping/tax/discount logic, reviews, testimonials, Q&A, and account relationships should remain under GoreeCloud control. Stripe and PayPal integrations should be adapters around a provider-neutral payment contract rather than becoming the primary domain model for orders or customer accounts.

Payment credentials and reusable secrets must remain in approved secret-management/runtime configuration and must not be stored in ordinary documentation, source files, public website assets, logs, or client-side configuration beyond provider-issued publishable identifiers specifically designed for that use. Payment state changes must be idempotent and evidence-backed, with signed/verified provider events used to reconcile authorization, capture, failure, refund, dispute, subscription, and cancellation state where applicable.

The design must minimize PCI-sensitive scope by relying on provider-hosted or provider-tokenized payment collection where practical. GoreeCloud must not collect or persist raw PAN/card-number or CVV data as part of this planned website-commerce architecture.

## Maintenance and synchronization

This roadmap and the corresponding Drive `FEATURE-ROADMAP.md` must remain materially synchronized with one another and with the authoritative project or service record. Update both copies whenever feature scope, priority, dependency, implementation status, cancellation, supersession, recommendation, or verification state materially changes.

No feature may be represented as complete or Stable solely because it appears in this roadmap. Completion and lifecycle claims require the applicable authoritative implementation, validation, review, release, provider configuration, security/privacy review, and production evidence.

## Reconciliation rule

At each material feature change, reconcile this roadmap against the current authoritative project record, repository implementation state, applicable platform-system requirements, payment-provider integration state where relevant, and GoreeCloud Tasks Management. Missing obligations, stale status, duplicated work, roadmap drift, or undocumented disposition changes are defects to correct.
