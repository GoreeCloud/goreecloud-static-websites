#!/usr/bin/env python3
"""Validate GoreeCloud's Cloudflare Pages static deployment contract.

The public site intentionally remains a dependency-free static deployment. This check
keeps Cloudflare Pages configuration within platform limits, prevents accidental runtime
surface growth, and avoids custom browser caching for versionless site assets so deploys
can rely on Pages' revalidation behavior instead of serving stale CSS/JS after releases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
HEADERS = ROOT / "_headers"
REQUIRED_STATIC_FILES = (
    ROOT / "404.html",
    ROOT / "robots.txt",
    ROOT / "sitemap.xml",
    ROOT / "site.webmanifest",
    ROOT / ".well-known" / "security.txt",
)
REQUIRED_GLOBAL_HEADERS = {
    "Content-Security-Policy",
    "Permissions-Policy",
    "Referrer-Policy",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "X-Permitted-Cross-Domain-Policies",
    "X-DNS-Prefetch-Control",
    "Cross-Origin-Opener-Policy",
    "Origin-Agent-Cluster",
    "Strict-Transport-Security",
}
MAX_HEADER_RULES = 100
MAX_LINE_LENGTH = 2000


@dataclass
class HeaderRule:
    pattern: str
    headers: dict[str, list[str]] = field(default_factory=dict)


def report(errors: list[str]) -> int:
    if errors:
        print("Deployment contract validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Deployment contract validation passed.")
    return 0


def parse_headers(errors: list[str]) -> list[HeaderRule]:
    if not HEADERS.exists():
        errors.append("Cloudflare Pages _headers file is missing.")
        return []

    lines = HEADERS.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, start=1):
        if len(line) > MAX_LINE_LENGTH:
            errors.append(
                f"_headers line {number} exceeds the Cloudflare Pages {MAX_LINE_LENGTH}-character line limit."
            )

    rules: list[HeaderRule] = []
    current: HeaderRule | None = None
    for number, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if raw_line[:1].isspace():
            if current is None:
                errors.append(f"_headers line {number} defines a header before any URL rule.")
                continue
            if ":" not in stripped:
                errors.append(f"_headers line {number} is not a valid header assignment: {stripped}")
                continue
            name, value = stripped.split(":", 1)
            header_name = name.strip()
            current.headers.setdefault(header_name, []).append(value.strip())
            continue

        current = HeaderRule(pattern=stripped)
        rules.append(current)

    if len(rules) > MAX_HEADER_RULES:
        errors.append(
            f"_headers defines {len(rules)} rules; Cloudflare Pages supports at most {MAX_HEADER_RULES}."
        )
    return rules


def validate_global_security(errors: list[str], rules: list[HeaderRule]) -> None:
    global_rules = [rule for rule in rules if rule.pattern == "/*"]
    if len(global_rules) != 1:
        errors.append(f"_headers must contain exactly one global /* rule, found {len(global_rules)}.")
        return

    global_rule = global_rules[0]
    missing = sorted(REQUIRED_GLOBAL_HEADERS.difference(global_rule.headers))
    for header in missing:
        errors.append(f"Global Cloudflare Pages rule is missing required header: {header}")

    csp_values = global_rule.headers.get("Content-Security-Policy", [])
    csp = " ".join(csp_values)
    for directive in (
        "default-src 'self'",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "form-action 'none'",
        "connect-src 'none'",
        "media-src 'none'",
        "worker-src 'none'",
        "manifest-src 'self'",
    ):
        if directive not in csp:
            errors.append(f"Global CSP must preserve the static-site boundary: {directive}")


def validate_cache_contract(errors: list[str], rules: list[HeaderRule]) -> None:
    security_rule_found = False
    for rule in rules:
        cache_values = rule.headers.get("Cache-Control", [])
        if not cache_values:
            continue
        if rule.pattern != "/.well-known/security.txt":
            errors.append(
                f"Custom Cache-Control is not allowed for versionless public assets: {rule.pattern}"
            )
            continue
        security_rule_found = True
        if cache_values != ["public, max-age=3600"]:
            errors.append(
                "security.txt must keep the deliberate one-hour Cache-Control policy."
            )

    if not security_rule_found:
        errors.append("security.txt must define its explicit one-hour Cache-Control policy.")


def validate_static_boundary(errors: list[str]) -> None:
    forbidden_runtime_paths = (
        ROOT / "functions",
        ROOT / "_worker.js",
        ROOT / "_worker.ts",
    )
    for path in forbidden_runtime_paths:
        if path.exists():
            errors.append(
                f"Unexpected Cloudflare runtime surface detected: {path.relative_to(ROOT)}. "
                "Update the deployment/security contract explicitly before adding server-side execution."
            )

    for path in REQUIRED_STATIC_FILES:
        if not path.exists():
            errors.append(f"Required static deployment resource is missing: {path.relative_to(ROOT)}")


def main() -> int:
    errors: list[str] = []
    rules = parse_headers(errors)
    validate_global_security(errors, rules)
    validate_cache_contract(errors, rules)
    validate_static_boundary(errors)
    return report(errors)


if __name__ == "__main__":
    sys.exit(main())
