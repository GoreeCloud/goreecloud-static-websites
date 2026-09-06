#!/usr/bin/env python3
"""Preflight reachable Git history for publication-sensitive material.

The current-tree hygiene validator protects what is checked out today. This companion gate
reviews every reachable historical blob so a credential or private-infrastructure detail does
not become "safe" merely because it was deleted in a later commit. Findings identify only the
kind of concern, object ID, and historical path; matched values are never printed.

This is a conservative automated preflight, not a claim that arbitrary secret scanning can prove
a repository contains no sensitive information. A deliberate human history review remains part
of the repository-publication decision tracked in issue #5.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import PurePosixPath
import re
import subprocess
import sys

from validate_repository_hygiene import (
    MAX_TEXT_BYTES,
    PRIVATE_FILE_SUFFIXES,
    PRIVATE_KEY_FILENAMES,
    SECRET_PATTERNS,
)

# These validator/test sources intentionally embed the private-network patterns or selected
# private-infrastructure identifiers that they reject from ordinary repository content. They
# remain subject to reusable-credential scanning; only literal infrastructure checks are skipped
# for these exact reviewed paths so detector definitions and synthetic fixtures do not match
# themselves. New paths must not be added here merely to silence a real finding.
DETECTION_SOURCE_PATHS = {
    "scripts/validate_repository_history.py",
    "scripts/validate_repository_guidance.py",
    "scripts/validate_release_evidence.py",
    "scripts/validate_site.py",
    "scripts/validate_resilience.py",
    "scripts/validate_privacy_policy.py",
    "scripts/validate_security_policy.py",
    "tests/test_validate_release_evidence.py",
}

PRIVATE_NETWORK_PATTERNS = (
    ("RFC1918 10/8 address", re.compile(r"\b10(?:\.\d{1,3}){3}\b")),
    ("RFC1918 192.168/16 address", re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b")),
    ("RFC1918 172.16/12 address", re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b")),
    ("CGNAT/private-overlay 100.64/10 address", re.compile(r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b")),
)
SENSITIVE_INFRASTRUCTURE_IDENTIFIERS = (
    "goreecloud-vps-01",
    ".netbird.selfhosted",
)
ALLOWED_ENV_FILENAMES = {".env.example", ".env.sample"}
MAX_GIT_OUTPUT_BYTES = 64 * 1024 * 1024


class GitError(RuntimeError):
    """Raised when the local Git object database cannot be inspected safely."""


def run_git(*args: str, input_text: str | None = None) -> bytes:
    try:
        result = subprocess.run(
            ("git", *args),
            input=input_text.encode("utf-8") if input_text is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise GitError(f"could not execute git: {exc}") from exc

    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise GitError(f"git {' '.join(args)} failed: {message or 'unknown error'}")
    if len(result.stdout) > MAX_GIT_OUTPUT_BYTES:
        raise GitError(f"git {' '.join(args)} produced unexpectedly large output")
    return result.stdout


def is_prohibited_historical_path(path_text: str) -> str | None:
    path = PurePosixPath(path_text)
    name = path.name.lower()

    if name == ".env" or (name.startswith(".env.") and name not in ALLOWED_ENV_FILENAMES):
        return "environment/secrets filename"
    if path.suffix.lower() in PRIVATE_FILE_SUFFIXES:
        return "private-key/certificate-container filename"
    if name in PRIVATE_KEY_FILENAMES or any(name.startswith(f"{base}.") for base in PRIVATE_KEY_FILENAMES):
        return "SSH private-key filename"
    return None


def reachable_objects() -> dict[str, set[str]]:
    raw = run_git("rev-list", "--objects", "--all").decode("utf-8", errors="strict")
    objects: dict[str, set[str]] = defaultdict(set)
    for line in raw.splitlines():
        object_id, separator, path = line.partition(" ")
        if not re.fullmatch(r"[0-9a-f]{40,64}", object_id):
            raise GitError("git rev-list returned an unexpected object identifier")
        if separator and path:
            objects[object_id].add(path)
        else:
            objects.setdefault(object_id, set())
    return objects


def object_metadata(object_ids: list[str]) -> dict[str, tuple[str, int]]:
    if not object_ids:
        return {}
    output = run_git(
        "cat-file",
        "--batch-check=%(objectname) %(objecttype) %(objectsize)",
        input_text="\n".join(object_ids) + "\n",
    ).decode("utf-8", errors="strict")

    metadata: dict[str, tuple[str, int]] = {}
    for line in output.splitlines():
        parts = line.split()
        if len(parts) != 3:
            raise GitError("git cat-file returned unexpected metadata")
        object_id, object_type, size_text = parts
        try:
            size = int(size_text)
        except ValueError as exc:
            raise GitError("git cat-file returned an invalid object size") from exc
        metadata[object_id] = (object_type, size)
    return metadata


def inspect_text_blob(object_id: str, paths: set[str], errors: list[str]) -> None:
    raw = run_git("cat-file", "blob", object_id)
    if len(raw) > MAX_TEXT_BYTES or b"\x00" in raw:
        return
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return

    display_paths = sorted(paths) or ["(historical blob with no retained path)"]
    path_summary = ", ".join(display_paths[:3])
    if len(display_paths) > 3:
        path_summary += f", +{len(display_paths) - 3} more"
    short_id = object_id[:12]

    for label, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append(f"Possible historical {label} in object {short_id} at {path_summary}")

    if any(path in DETECTION_SOURCE_PATHS for path in paths):
        return

    for label, pattern in PRIVATE_NETWORK_PATTERNS:
        if pattern.search(text):
            errors.append(f"Possible historical {label} in object {short_id} at {path_summary}")

    lower = text.lower()
    for identifier in SENSITIVE_INFRASTRUCTURE_IDENTIFIERS:
        if identifier.lower() in lower:
            errors.append(
                f"Possible historical private infrastructure identifier in object {short_id} at {path_summary}"
            )


def main() -> int:
    errors: list[str] = []
    try:
        shallow = run_git("rev-parse", "--is-shallow-repository").decode("ascii", errors="strict").strip()
        if shallow != "false":
            print("Repository history validation failed:")
            print("  - Full Git history is required; checkout is shallow.")
            return 1

        objects = reachable_objects()
        metadata = object_metadata(list(objects))

        historical_blobs = 0
        inspected_text_blobs = 0
        for object_id, paths in objects.items():
            object_type, size = metadata.get(object_id, ("", -1))
            if object_type != "blob":
                continue
            historical_blobs += 1

            for path in sorted(paths):
                reason = is_prohibited_historical_path(path)
                if reason:
                    errors.append(
                        f"Historical {reason} found in object {object_id[:12]} at {path}"
                    )

            if 0 <= size <= MAX_TEXT_BYTES:
                inspected_text_blobs += 1
                inspect_text_blob(object_id, paths, errors)

    except (GitError, UnicodeError) as exc:
        print("Repository history validation failed:")
        print(f"  - Could not complete full-history inspection: {exc}")
        return 1

    if errors:
        print("Repository history validation failed:")
        for error in sorted(set(errors)):
            print(f"  - {error}")
        print("Matched values are intentionally redacted. Treat any credential finding as potentially compromised.")
        return 1

    print(
        "Repository history validation passed: "
        f"reviewed {historical_blobs} reachable blobs; "
        f"inspected {inspected_text_blobs} text-sized blobs without exposing matched values."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
