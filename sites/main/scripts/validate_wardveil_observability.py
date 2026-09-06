#!/usr/bin/env python3
"""Validate Wardveil Security presentation and static-site observability boundaries."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SECURITY_PAGE = ROOT / "security.html"
SECURITY_MD = ROOT / "SECURITY.md"
SECURITY_TXT = ROOT / ".well-known" / "security.txt"
OBSERVABILITY = ROOT / "docs" / "wardveil-security-and-observability.md"
MAIN_JS = ROOT / "js" / "main.js"
THEME_JS = ROOT / "js" / "theme-init.js"
VALIDATION_WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"

WARDVEIL_IDENTITY = "Wardveil Security by GoreeCloud"
SECURITY_CONTACT = "security@goreecloud.com"
PROTECTED_PHRASE = "Protected by Wardveil"
WORKFLOW_COMMAND = "python scripts/validate_wardveil_observability.py"

REQUIRED_SECURITY_PAGE_COPY = (
    WARDVEIL_IDENTITY,
    SECURITY_CONTACT,
    "platform-wide first-party security system and shared security plane",
    "Foundation 0.9",
    "Sentinel Fold",
    "current authoritative evidence",
    "production ClamAV scanner runtime is deployed and accepted at the scanner-evidence layer",
    "does not establish end-to-end Wardveil Scan application acceptance",
)
REQUIRED_SECURITY_POLICY_COPY = (
    WARDVEIL_IDENTITY,
    SECURITY_CONTACT,
    "platform-wide first-party security system and shared security plane",
    "Foundation 0.9",
    "Sentinel Fold",
    "production ClamAV scanner runtime is deployed and accepted at the scanner-evidence layer",
    "does not establish end-to-end Wardveil Scan application acceptance",
)
REQUIRED_OBSERVABILITY_COPY = (
    WARDVEIL_IDENTITY,
    "anonymous static site",
    "not applicable to the current website runtime",
    "source- and deployment-bound evidence",
    "must not add client-side logging, analytics, session replay, fingerprinting",
    "Cloudflare Pages and other infrastructure providers may generate platform-level logs",
    "does not assume that a provider logging product is enabled",
    "progressive enhancement",
    "Unknown, skipped, unavailable, stale, or unverified required evidence does not count as passing",
    "exact branch-preview verification passes before merge",
    "exact production verification passes after merge",
)

PROHIBITED_BROWSER_MARKERS = (
    "google-analytics.com",
    "googletagmanager.com",
    "plausible.io",
    "cloudflareinsights.com",
    "sentry.io",
    "posthog",
    "segment.com",
    "mixpanel",
)


def require(errors: list[str], text: str, marker: str, location: str) -> None:
    if marker.casefold() not in text.casefold():
        errors.append(f"{location} is missing required Wardveil/observability text: {marker}")


def main() -> int:
    errors: list[str] = []

    for path in (
        SECURITY_PAGE,
        SECURITY_MD,
        SECURITY_TXT,
        OBSERVABILITY,
        MAIN_JS,
        THEME_JS,
        VALIDATION_WORKFLOW,
    ):
        if not path.exists():
            errors.append(f"Required Wardveil/observability file is missing: {path.relative_to(ROOT)}")
    if errors:
        return report(errors)

    security_page = SECURITY_PAGE.read_text(encoding="utf-8")
    security_md = SECURITY_MD.read_text(encoding="utf-8")
    security_txt = SECURITY_TXT.read_text(encoding="utf-8")
    observability = OBSERVABILITY.read_text(encoding="utf-8")
    validation_workflow = VALIDATION_WORKFLOW.read_text(encoding="utf-8")
    browser_source = "\n".join(
        (
            MAIN_JS.read_text(encoding="utf-8"),
            THEME_JS.read_text(encoding="utf-8"),
        )
    )

    for marker in REQUIRED_SECURITY_PAGE_COPY:
        require(errors, security_page, marker, "security.html")
    for marker in REQUIRED_SECURITY_POLICY_COPY:
        require(errors, security_md, marker, "SECURITY.md")
    require(errors, security_txt, f"Contact: mailto:{SECURITY_CONTACT}", ".well-known/security.txt")
    require(errors, validation_workflow, WORKFLOW_COMMAND, ".github/workflows/validate.yml")

    for marker in REQUIRED_OBSERVABILITY_COPY:
        require(errors, observability, marker, "docs/wardveil-security-and-observability.md")

    if PROTECTED_PHRASE.casefold() in security_page.casefold():
        errors.append(
            "security.html must not use the blanket 'Protected by Wardveil' phrase; public Wardveil presentation must remain evidence-scoped."
        )

    for stale in (
        "security identity and presentation layer",
        "Foundation 0.7",
        "production ClamAV runtime remains unaccepted",
    ):
        if stale.casefold() in security_page.casefold() or stale.casefold() in security_md.casefold():
            errors.append(f"Superseded Wardveil public model remains published: {stale}")

    for marker in PROHIBITED_BROWSER_MARKERS:
        if marker.casefold() in browser_source.casefold():
            errors.append(f"Browser source contains a prohibited analytics/telemetry marker: {marker}")

    for browser_api in ("fetch(", "XMLHttpRequest", "sendBeacon(", "WebSocket("):
        if browser_api in browser_source:
            errors.append(
                f"Browser source introduces a runtime network client ({browser_api}); the current static observability boundary requires no browser exporter."
            )

    return report(errors)


def report(errors: list[str]) -> int:
    if errors:
        print("Wardveil Security and observability validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Wardveil Security and observability validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
