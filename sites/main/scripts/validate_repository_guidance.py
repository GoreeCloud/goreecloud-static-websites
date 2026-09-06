#!/usr/bin/env python3
"""Validate repository contribution guidance and public/private safety boundaries."""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ISSUE_CONFIG = ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
BUG_FORM = ROOT / ".github" / "ISSUE_TEMPLATE" / "bug-report.yml"
FEATURE_FORM = ROOT / ".github" / "ISSUE_TEMPLATE" / "feature-request.yml"
PR_TEMPLATE = ROOT / ".github" / "pull_request_template.md"
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"
README = ROOT / "README.md"
VERSION = ROOT / "VERSION"
DOCS_INDEX = ROOT / "docs" / "README.md"
ASSET_INVENTORY = ROOT / "docs" / "public-asset-inventory.md"
RELEASE_CHECKLIST = ROOT / "docs" / "release-readiness-checklist.md"
RELEASE_EVIDENCE_TEMPLATE = ROOT / "docs" / "release-evidence-template.md"
SECURITY_URL = "https://www.goreecloud.com/security.html"

PRIVATE_PATTERNS = (
    re.compile(r"\b10(?:\.\d{1,3}){3}\b"),
    re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b"),
)
SENSITIVE_TERMS = ("goreecloud-vps-01", ".netbird.selfhosted")


def normalize_guidance_text(text: str) -> str:
    """Normalize harmless Markdown emphasis and whitespace for semantic marker checks."""
    without_emphasis = re.sub(r"[*_]", "", text)
    return re.sub(r"\s+", " ", without_emphasis).strip().lower()


def require_markers(path: Path, markers: tuple[str, ...], errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"Required repository guidance file is missing: {path.relative_to(ROOT)}")
        return ""

    text = path.read_text(encoding="utf-8")
    normalized = normalize_guidance_text(text)
    for marker in markers:
        if normalize_guidance_text(marker) not in normalized:
            errors.append(f"{path.relative_to(ROOT)} is missing required guidance: {marker}")
    return text


def current_version(errors: list[str]) -> str:
    if not VERSION.exists():
        errors.append("Canonical VERSION file is missing.")
        return ""

    version = VERSION.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
        errors.append("VERSION must contain one strict SemVer value.")
        return ""
    return version


def main() -> int:
    errors: list[str] = []
    version = current_version(errors)

    config = require_markers(
        ISSUE_CONFIG,
        (
            "blank_issues_enabled: false",
            SECURITY_URL,
            "do not publish vulnerability details",
        ),
        errors,
    )
    bug = require_markers(
        BUG_FORM,
        (
            "name: Bug report",
            SECURITY_URL,
            "do not include security vulnerability details",
            "credentials",
            "private infrastructure",
            "private ip addresses",
            "this is not a security vulnerability report",
        ),
        errors,
    )
    feature = require_markers(
        FEATURE_FORM,
        (
            "name: Feature request",
            SECURITY_URL,
            "private infrastructure",
            "passing ci does not by itself authorize",
        ),
        errors,
    )
    pr_template = require_markers(
        PR_TEMPLATE,
        (
            "## Validation",
            "## Privacy and security boundary",
            SECURITY_URL,
            "private hostnames",
            "private ip addresses",
            "passing CI does not by itself authorize",
            "issue #5",
        ),
        errors,
    )
    workflow = require_markers(
        WORKFLOW,
        (
            "Validate repository guidance",
            "Validate release evidence records",
            "Validate public creative-asset boundary",
            "python scripts/validate_repository_guidance.py",
            "python scripts/validate_release_evidence.py",
            "python scripts/validate_repository_hygiene.py",
            "python scripts/validate_repository_history.py",
            "python scripts/validate_license.py",
            "python scripts/validate_public_assets.py",
            "python scripts/validate_accessibility.py",
            "python scripts/validate_glaze_ui.py",
            'python -m unittest discover -s tests -p "test_*.py"',
            "fetch-depth: 0",
        ),
        errors,
    )

    readme_markers = (
        f"Current accepted website package: **v{version}" if version else "Current accepted website package:",
        "`VERSION` is the canonical machine-readable version source",
        "## Source license and creative-rights boundary",
        "Apache License 2.0",
        "Apache-2.0",
        "python scripts/build_public_site.py",
        "python scripts/validate_repository_hygiene.py",
        "python scripts/validate_repository_history.py",
        "python scripts/validate_license.py",
        "python scripts/validate_public_assets.py",
        "python scripts/validate_accessibility.py",
        "python scripts/validate_glaze_ui.py",
        'python -m unittest discover -s tests -p "test_*.py"',
        "Build output directory: `dist`",
        "exact, per-file allowlisted",
        "Adding a file to `assets/`, `css/`, `js/`",
        "Glaze UI is treated as a design contract",
        "automated checks are regression controls, not a claim of complete WCAG conformance",
        "screen-reader testing",
        "repository-history preflight",
        "non-shallow checkout",
        "matched value",
        "docs/public-asset-inventory.md",
        "not a license grant",
        "final human reachable-history/contextual-disclosure review",
        "issue #5",
        "Issue #6 is closed",
        "isolated `dist/` Cloudflare Pages cutover is complete",
        "Passing CI does not itself authorize",
        "GoreeCloud Monitor",
        "Uptime Kuma remains the current production availability monitor",
    )
    readme = require_markers(README, readme_markers, errors)

    docs_index = require_markers(
        DOCS_INDEX,
        (
            "GoreeCloud Website Repository Documentation",
            "public-asset-inventory.md",
            "release-readiness-checklist.md",
            "release-evidence-template.md",
            "inventory = publication/rights",
            "canonical reusable release-readiness procedure",
            "one-candidate historical validation evidence",
            "python scripts/create_release_evidence.py --commit",
            "python scripts/validate_release_evidence.py",
            "non-overwriting creation",
            "Record state",
            "Working — not accepted",
            "Accepted`, `Blocked`, `Rejected`, or `Superseded",
            "does not decide whether the underlying human review was substantively correct",
            "must remain outside the generated `dist/` artifact",
            "Explicit human authorization remains required",
            "Do not record",
            "credentials, tokens, or private keys",
            "private IP addresses or private hostnames",
        ),
        errors,
    )
    asset_inventory = require_markers(
        ASSET_INVENTORY,
        (
            "not a license grant",
            "Official artwork is required when it exists",
            "Source authority",
            "Source revision/path",
            "Reviewed Git blob",
            "Historical repository presence does not authorize artwork use",
            "repository presence does not make a file deployable",
            "does not automatically license GoreeCloud branding or third-party marks",
            "third-party trademarks and artwork remain the property of their respective owners",
            "final human reachable-history/contextual-disclosure review",
            "explicit repository visibility/publication decision",
            "text-only presentation rather than an invented icon",
            "issue #5 remains open",
        ),
        errors,
    )
    release_checklist = require_markers(
        RELEASE_CHECKLIST,
        (
            "GoreeCloud Website Release Readiness Checklist",
            "America/Chicago",
            "exact intended release-candidate commit SHA",
            "python scripts/create_release_evidence.py --commit",
            "create a new candidate record or explicitly mark the older record Superseded",
            "python scripts/validate_repository_history.py",
            "python scripts/validate_license.py",
            "Apache-2.0",
            'python -m unittest discover -s tests -p "test_*.py"',
            "Glaze UI visual and interaction acceptance",
            "Accessibility acceptance",
            "Source publication and creative-rights gate — issue #5",
            "Cloudflare isolated-artifact gate — issue #6",
            "passing CI does not itself authorize",
            "production does **not** publish `X-Robots-Tag: noindex`",
            "must never be copied into the public `dist/` artifact",
        ),
        errors,
    )
    release_evidence_template = require_markers(
        RELEASE_EVIDENCE_TEMPLATE,
        (
            "GoreeCloud Website Release Evidence Record Template",
            "one exact GoreeCloud website release candidate",
            "exact 40-character Git commit SHA",
            "America/Chicago",
            "12-hour time format",
            "Do not place credentials",
            "Glaze UI visual and interaction acceptance",
            "Accessibility acceptance",
            "Source publication and creative-rights gate — issue #5",
            "Cloudflare isolated-artifact gate — issue #6",
            "Exceptions and accepted limitations",
            "Release authorization",
            "Post-release production verification",
            "does not itself authorize a merge",
            "must remain outside the website `dist/` artifact",
            "Historical evidence must remain distinguishable from current state",
        ),
        errors,
    )

    for path, text in (
        (ISSUE_CONFIG, config),
        (BUG_FORM, bug),
        (FEATURE_FORM, feature),
        (PR_TEMPLATE, pr_template),
        (README, readme),
        (DOCS_INDEX, docs_index),
        (ASSET_INVENTORY, asset_inventory),
        (RELEASE_CHECKLIST, release_checklist),
        (RELEASE_EVIDENCE_TEMPLATE, release_evidence_template),
    ):
        if not text:
            continue
        for pattern in PRIVATE_PATTERNS:
            match = pattern.search(text)
            if match:
                errors.append(f"Private-range IP address found in {path.relative_to(ROOT)}: {match.group(0)}")
        lower = text.lower()
        for term in SENSITIVE_TERMS:
            if term.lower() in lower:
                errors.append(f"Private infrastructure identifier found in {path.relative_to(ROOT)}: {term}")

    if config.count("url: https://") != 1:
        errors.append("Issue-template config must expose exactly one HTTPS contact link: the security-reporting policy.")
    if "blank_issues_enabled: true" in config:
        errors.append("Blank issues must remain disabled so reporters receive the public/private safety guidance.")

    if bug.count("required: true") < 6:
        errors.append("Bug report form must keep its required reproduction and safety confirmations.")
    if feature.count("required: true") < 4:
        errors.append("Feature request form must keep its required need, proposal, impact, and boundary confirmations.")

    return report(errors)


def report(errors: list[str]) -> int:
    if errors:
        print("Repository guidance validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Repository guidance validation passed: official-artwork provenance, publication boundaries, and public/private contribution guidance are synchronized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
