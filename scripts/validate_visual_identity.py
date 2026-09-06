#!/usr/bin/env python3
"""Fail closed on known GoreeCloud visual-identity drift in centralized static websites."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CANONICAL = {
    "sites/projects/assets/goreecloud-mesh-mark.svg": "5362a52bd9fb38379f083a4d894934ed1acf9b67",
    "sites/manager/assets/manager-mark.svg": "024d82d5b5911e426216dfbd6a19d95cd6d71fc3",
    "sites/labs/assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "sites/labs/assets/products/ai.svg": "1cbe04748f50cb843eef0cbb7233e2769efa275a",
    "sites/labs/assets/products/code.svg": "579f0416bd2839bf40e87de7751e319d80bd0bf9",
}

FORBIDDEN_ACTIVE_ASSET_NAMES = {
    "goreecloud-artwork-pending.svg",
}


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"visual identity validation failed: {message}")


def main() -> None:
    errors: list[str] = []

    for rel, expected in CANONICAL.items():
        path = ROOT / rel
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing canonical asset: {rel}")
            continue
        actual = git_blob_sha(path)
        if actual != expected:
            errors.append(f"canonical asset drift: {rel}: expected {expected}, got {actual}")

    for path in (ROOT / "sites").rglob("*"):
        if path.is_file() and path.name in FORBIDDEN_ACTIVE_ASSET_NAMES:
            errors.append(f"forbidden placeholder artwork remains in active source: {path.relative_to(ROOT)}")

    labs_css = (ROOT / "sites/labs/labs.css").read_text(encoding="utf-8")
    required_labs_markers = (
        '#intelligence .text-mark { background-image: url("/assets/products/ai.svg"); }',
        '#build .product-card:nth-child(2) .text-mark { background-image: url("/assets/products/code.svg"); }',
        "#home .text-mark,",
        "#build .product-card:first-child .text-mark,",
        "#boot .text-mark { display: none; }",
    )
    for marker in required_labs_markers:
        if marker not in labs_css:
            errors.append(f"Labs identity rendering boundary missing: {marker}")

    identity_record = ROOT / "sites/labs/IDENTITY-ASSETS.md"
    if not identity_record.is_file():
        errors.append("Labs identity authority record is missing")
    else:
        text = identity_record.read_text(encoding="utf-8")
        for marker in (
            "GoreeCloud/goreecloud-branding-assets",
            "GoreeCloud Home",
            "GoreeCloud Home Security",
            "GoreeCloud Containers",
            "GoreeCloud Boot",
            "branding-assets#16",
        ):
            if marker not in text:
                errors.append(f"Labs identity authority record missing marker: {marker}")

    if errors:
        for error in errors:
            print(f"  - {error}")
        fail(f"{len(errors)} defect(s)")

    print(f"Visual identity validation passed: {len(CANONICAL)} canonical asset pins verified; no forbidden placeholder artwork present.")


if __name__ == "__main__":
    main()
