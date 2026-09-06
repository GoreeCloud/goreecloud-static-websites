#!/usr/bin/env python3
"""Validate candidate-specific GoreeCloud website release-evidence records.

This validator enforces structural, privacy, and candidate-binding invariants only. It does
not determine whether a human review was substantively correct, grant rights, or authorize
merge, publication, Cloudflare, DNS, or production actions.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "docs" / "release-evidence"

FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([0-9a-f]{12})-release-evidence\.md$")
TITLE_RE = re.compile(r"^# GoreeCloud Website Release Evidence — (\d{4}-\d{2}-\d{2}) — ([0-9a-f]{12})$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CREATED_RE = re.compile(
    r"^[A-Z][a-z]+ \d{1,2}, \d{4} at (?:1[0-2]|[1-9]):[0-5]\d (?:AM|PM) (?:CST|CDT)$"
)

PRIVATE_PATTERNS = (
    re.compile(r"\b10(?:\.\d{1,3}){3}\b"),
    re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b"),
)
SENSITIVE_TERMS = ("goreecloud-vps-01", ".netbird.selfhosted")
SECRET_PATTERNS = (
    ("private key material", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
)

DISPOSITIONS = {
    "ACCEPTED": "Accepted",
    "BLOCKED": "Blocked",
    "REJECTED": "Rejected",
    "SUPERSEDED": "Superseded",
}
WORKING_STATE = "Working — not accepted"

REQUIRED_ACCEPTED_CHECKBOXES = (
    "Exact candidate SHA confirmed.",
    "No later unreviewed commit is being treated as covered by this record.",
    "Pull request still targets the intended base branch.",
    "Candidate has not been merged or promoted unintentionally.",
    "All required automated gates passed on the exact candidate.",
    "Any failure or exception is documented below instead of being silently ignored.",
    "Accepted for this exact candidate.",
    "No material visual or interaction defect remains hidden by automated validation.",
    "Human acceptance completed for this exact candidate.",
    "No formal WCAG conformance claim is being inferred solely from this record or CI.",
    "Progressive enhancement and resilience accepted.",
    "Privacy/origin behavior accepted.",
    "Issue #5 is resolved for the actions being authorized.",
    "No source-publication or third-party-rights claim exceeds the evidence actually reviewed.",
    "Cloudflare is verified to build and publish the exact isolated `dist/` artifact.",
    "Fresh post-cutover remote verification passed.",
)


def display_path(path: Path) -> str:
    """Return a stable repository-relative path when possible, otherwise a safe test path."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def field_value(text: str, label: str) -> str | None:
    # Keep blank fields line-bounded. ``\s`` would also consume a newline and could
    # incorrectly borrow the following metadata field as this field's value.
    pattern = re.compile(rf"(?m)^- {re.escape(label)}:[ \t]*(.*)$")
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def checkbox_checked(text: str, label: str) -> bool:
    target = f"- [x] {label}".casefold()
    return any(line.strip().casefold() == target for line in text.splitlines())


def disposition_states(text: str) -> list[str]:
    checked: list[str] = []
    for disposition in DISPOSITIONS:
        if re.search(rf"(?mi)^- \[x\] {disposition}\b", text):
            checked.append(disposition)
    return checked


def record_state(text: str) -> str | None:
    match = re.search(r"(?m)^- Record state: \*\*(.+?)\*\*\s*$", text)
    return match.group(1).strip() if match else None


def nonblank(value: str | None) -> bool:
    return value is not None and bool(value.strip())


def validate_record(path: Path) -> list[str]:
    errors: list[str] = []
    relative = display_path(path)

    if path.is_symlink():
        return [f"Release evidence record must not be a symlink: {relative}"]
    if not path.is_file():
        return [f"Release evidence entry is not a regular file: {relative}"]

    name_match = FILENAME_RE.fullmatch(path.name)
    if not name_match:
        errors.append(
            f"Release evidence filename must use YYYY-MM-DD-<12-lowercase-hex>-release-evidence.md: {relative}"
        )
        filename_date = None
        filename_short_sha = None
    else:
        filename_date, filename_short_sha = name_match.groups()
        try:
            datetime.strptime(filename_date, "%Y-%m-%d")
        except ValueError:
            errors.append(f"Release evidence filename contains an invalid calendar date: {relative}")

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"Could not read release evidence record {relative}: {exc}"]

    lines = text.splitlines()
    title_match = TITLE_RE.fullmatch(lines[0]) if lines else None
    if not title_match:
        errors.append(f"Release evidence record has an invalid or missing candidate-bound title: {relative}")
    elif filename_date and filename_short_sha:
        title_date, title_short_sha = title_match.groups()
        if title_date != filename_date or title_short_sha != filename_short_sha:
            errors.append(f"Release evidence title does not match its filename identity: {relative}")

    exact_sha = field_value(text, "Exact candidate commit (40-character SHA)")
    bound_sha = field_value(text, "Bound candidate commit")
    if exact_sha is None or not SHA_RE.fullmatch(exact_sha):
        errors.append(f"Release evidence record must contain one canonical lowercase 40-character candidate SHA: {relative}")
    if bound_sha is None:
        errors.append(f"Release evidence record is missing its bound candidate commit metadata: {relative}")
    else:
        unquoted_bound = bound_sha.strip("`")
        if not SHA_RE.fullmatch(unquoted_bound):
            errors.append(f"Bound candidate commit metadata is not a canonical lowercase 40-character SHA: {relative}")
        elif exact_sha and unquoted_bound != exact_sha:
            errors.append(f"Bound candidate commit does not match the candidate identity field: {relative}")

    if exact_sha and SHA_RE.fullmatch(exact_sha) and filename_short_sha and exact_sha[:12] != filename_short_sha:
        errors.append(f"Release evidence filename short SHA does not match the exact candidate SHA: {relative}")

    created = field_value(text, "Record created")
    if created is None or not CREATED_RE.fullmatch(created):
        errors.append(
            f"Record-created timestamp must use GoreeCloud Central Time and 12-hour format with CST/CDT: {relative}"
        )

    state = record_state(text)
    allowed_states = {WORKING_STATE, *DISPOSITIONS.values()}
    if state not in allowed_states:
        errors.append(f"Release evidence record has an invalid or missing Record state: {relative}")

    dispositions = disposition_states(text)
    if len(dispositions) > 1:
        errors.append(f"Release evidence record selects more than one final candidate disposition: {relative}")
    elif not dispositions:
        if state and state != WORKING_STATE:
            errors.append(f"Final Record state requires exactly one matching disposition checkbox: {relative}")
    else:
        disposition = dispositions[0]
        expected_state = DISPOSITIONS[disposition]
        if state != expected_state:
            errors.append(
                f"Record state must match the selected {disposition} disposition ({expected_state}): {relative}"
            )

        if disposition == "ACCEPTED":
            for label in REQUIRED_ACCEPTED_CHECKBOXES:
                if not checkbox_checked(text, label):
                    errors.append(f"Accepted release evidence is missing required acceptance checkbox: {label} ({relative})")

            merge_auth = field_value(text, "Merge authorization")
            production_auth = field_value(text, "Production-release authorization")
            if not nonblank(merge_auth) and not nonblank(production_auth):
                errors.append(
                    f"Accepted release evidence must record at least one explicit authorized action: {relative}"
                )
            if not nonblank(field_value(text, "Authorizing person/role")):
                errors.append(f"Accepted release evidence must identify the authorizing person or role: {relative}")
            if not nonblank(field_value(text, "Authorization date/time")):
                errors.append(f"Accepted release evidence must record the authorization date/time: {relative}")

    if checkbox_checked(text, "Production verification passed without a material discrepancy."):
        if not nonblank(field_value(text, "Production verifier result")):
            errors.append(f"Post-release success cannot be checked without a production verifier result: {relative}")
        if not nonblank(field_value(text, "Production verification date/time")):
            errors.append(f"Post-release success cannot be checked without a production verification timestamp: {relative}")

    for pattern in PRIVATE_PATTERNS:
        match = pattern.search(text)
        if match:
            errors.append(f"Private-range IP address found in release evidence record {relative}: {match.group(0)}")
    lower = text.lower()
    for term in SENSITIVE_TERMS:
        if term.lower() in lower:
            errors.append(f"Private infrastructure identifier found in release evidence record {relative}: {term}")
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append(f"Possible {label} found in release evidence record: {relative}")

    return errors


def validate_records(evidence_dir: Path = EVIDENCE_DIR) -> tuple[list[str], int]:
    if not evidence_dir.exists():
        return [], 0
    if evidence_dir.is_symlink():
        return ["Release evidence directory must not be a symlink."], 0
    if not evidence_dir.is_dir():
        return ["Release evidence path must be a directory."], 0

    errors: list[str] = []
    entries = sorted(evidence_dir.iterdir())
    records = [entry for entry in entries if entry.is_file() or entry.is_symlink()]
    unexpected_dirs = [entry for entry in entries if entry.is_dir() and not entry.is_symlink()]
    for directory in unexpected_dirs:
        errors.append(f"Nested directories are not allowed under docs/release-evidence: {display_path(directory)}")
    for record in records:
        errors.extend(validate_record(record))
    return errors, len(records)


def main() -> int:
    errors, count = validate_records()
    if errors:
        print("Release evidence validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    if count == 0:
        print("Release evidence validation passed: no candidate records are present.")
    else:
        print(f"Release evidence validation passed across {count} candidate record(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
