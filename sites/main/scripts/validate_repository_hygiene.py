#!/usr/bin/env python3
"""Validate GoreeCloud website repository hygiene and sensitive-file boundaries."""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
GITIGNORE = ROOT / ".gitignore"
MAX_TEXT_BYTES = 1_048_576
EXCLUDED_DIRS = {".git", "dist", "__pycache__"}
PRIVATE_FILE_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}
PRIVATE_KEY_FILENAMES = {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}
TEMPORARY_SUFFIXES = {".swp", ".swo", ".orig", ".rej"}

# High-confidence reusable credential signatures. The validator itself is excluded
# from content scanning because it intentionally contains these detection patterns.
SECRET_PATTERNS = (
    ("private key material", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    (
        "hard-coded credential assignment",
        re.compile(
            r"(?i)\b(?:password|passwd|api[_-]?key|access[_-]?token|client[_-]?secret)\b"
            r"\s*[:=]\s*['\"]([^'\"\s]{12,})['\"]"
        ),
    ),
)

REQUIRED_GITIGNORE_MARKERS = (
    "/dist/",
    "__pycache__/",
    "*.py[cod]",
    ".env",
    ".env.*",
    "!.env.example",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
)


def iter_repository_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.is_file() or path.is_symlink():
            files.append(path)
    return sorted(files)


def validate_path(path: Path, errors: list[str]) -> None:
    relative = path.relative_to(ROOT)
    name = path.name
    lower_name = name.lower()

    if path.is_symlink():
        errors.append(f"Repository source must not use symlinks: {relative}")
    if lower_name == ".env" or (lower_name.startswith(".env.") and lower_name not in {".env.example", ".env.sample"}):
        errors.append(f"Tracked environment/secrets file is prohibited: {relative}")
    if path.suffix.lower() in PRIVATE_FILE_SUFFIXES:
        errors.append(f"Tracked private-key/certificate-container file is prohibited: {relative}")
    if lower_name in PRIVATE_KEY_FILENAMES or any(lower_name.startswith(f"{base}.") for base in PRIVATE_KEY_FILENAMES):
        errors.append(f"Tracked SSH private-key material is prohibited: {relative}")
    if path.suffix.lower() in TEMPORARY_SUFFIXES or lower_name.endswith("~"):
        errors.append(f"Temporary/editor artifact must not be tracked: {relative}")
    if lower_name in {".ds_store", "thumbs.db"}:
        errors.append(f"Operating-system metadata must not be tracked: {relative}")


def validate_content(path: Path, errors: list[str]) -> None:
    if path.resolve() == SELF:
        return
    try:
        raw = path.read_bytes()
    except OSError as exc:
        errors.append(f"Could not inspect repository file {path.relative_to(ROOT)}: {exc}")
        return
    if len(raw) > MAX_TEXT_BYTES or b"\x00" in raw:
        return
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return

    for label, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append(f"Possible {label} found in tracked text file: {path.relative_to(ROOT)}")


def validate_gitignore(errors: list[str]) -> None:
    if not GITIGNORE.exists():
        errors.append(".gitignore is required for repository hygiene.")
        return
    text = GITIGNORE.read_text(encoding="utf-8")
    for marker in REQUIRED_GITIGNORE_MARKERS:
        if marker not in text:
            errors.append(f".gitignore is missing sensitive/generated-file protection: {marker}")


def main() -> int:
    errors: list[str] = []
    files = iter_repository_files()

    for path in files:
        validate_path(path, errors)
        validate_content(path, errors)
    validate_gitignore(errors)

    if errors:
        print("Repository hygiene validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Repository hygiene validation passed across {len(files)} tracked/source files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
