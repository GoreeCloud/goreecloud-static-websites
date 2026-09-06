#!/usr/bin/env python3
"""Fail closed on GoreeCloud visual-identity drift in centralized static websites."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CANONICAL = {
    "sites/archive/assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "sites/blog/assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "sites/projects/assets/goreecloud-mesh-mark.svg": "5362a52bd9fb38379f083a4d894934ed1acf9b67",
    "sites/roadmap/assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "sites/privacy/branding/privacy-shield/privacy-shield-icon.svg": "62b10029d4104d0235afe634c21f55d0a826a63d",
    "sites/manager/assets/manager-mark.svg": "024d82d5b5911e426216dfbd6a19d95cd6d71fc3",
    "sites/labs/assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "sites/labs/assets/products/ai.svg": "1cbe04748f50cb843eef0cbb7233e2769efa275a",
    "sites/labs/assets/products/code.svg": "579f0416bd2839bf40e87de7751e319d80bd0bf9",
}

FORBIDDEN_ACTIVE_ASSET_NAMES = {
    "goreecloud-artwork-pending.svg",
}

# Source pages whose main browser identity and visible header identity are now
# required to resolve to the approved canonical asset rather than text-only or
# improvised artwork. More site mappings are added as their audited contracts are
# pinned; passing this validator never substitutes for the separate Glaze migration.
PAGE_IDENTITY = {
    "sites/archive/index.html": (
        '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
        '<img src="/assets/goreecloud-logo.svg" width="32" height="32" alt="">',
    ),
    "sites/blog/index.html": (
        '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
        '<img src="/assets/goreecloud-logo.svg" width="32" height="32" alt="">',
    ),
    "sites/roadmap/index.html": (
        '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
        '<img src="/assets/goreecloud-logo.svg" width="32" height="32" alt="">',
    ),
    "sites/privacy/website/index.html": (
        '<link rel="icon" href="/assets/privacy-shield-icon.svg" type="image/svg+xml">',
        '<img src="/assets/privacy-shield-icon.svg" alt="" width="34" height="34">',
    ),
}

ERROR_PAGE_IDENTITY = {
    "sites/archive/404.html": '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
    "sites/blog/404.html": '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
    "sites/roadmap/404.html": '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
    "sites/privacy/website/404.html": '<link rel="icon" href="/assets/privacy-shield-icon.svg" type="image/svg+xml">',
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

    for rel, markers in PAGE_IDENTITY.items():
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"website identity page missing: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"website identity marker missing from {rel}: {marker}")

    for rel, marker in ERROR_PAGE_IDENTITY.items():
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"website error page missing: {rel}")
            continue
        if marker not in path.read_text(encoding="utf-8"):
            errors.append(f"canonical favicon missing from {rel}")

    # Labs must render approved AI/Code marks as actual images and must not manufacture
    # textual/CSS surrogate identities for products whose canonical artwork is pending.
    labs_index = (ROOT / "sites/labs/index.html").read_text(encoding="utf-8")
    labs_css = (ROOT / "sites/labs/labs.css").read_text(encoding="utf-8")
    for marker in (
        '<img class="product-mark" src="/assets/products/ai.svg"',
        '<img class="product-mark" src="/assets/products/code.svg"',
    ):
        if marker not in labs_index:
            errors.append(f"Labs canonical product artwork missing from markup: {marker}")
    if labs_index.count('class="product-mark"') != 2:
        errors.append("Labs must render exactly the two currently approved product marks")
    for forbidden in (
        'class="text-mark"',
        '>Home</span>',
        '>Security</span>',
        '>OCI</span>',
        '>Boot</span>',
    ):
        if forbidden in labs_index:
            errors.append(f"Labs surrogate product identity remains in markup: {forbidden}")
    for forbidden in (".text-mark", "background-image: url(\"/assets/products/ai.svg\")", "background-image: url(\"/assets/products/code.svg\")"):
        if forbidden in labs_css:
            errors.append(f"Labs surrogate/CSS-painted identity remains in stylesheet: {forbidden}")
    if ".product-mark" not in labs_css:
        errors.append("Labs canonical product artwork sizing contract is missing")

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

    print(
        "Visual identity validation passed: "
        f"{len(CANONICAL)} canonical asset pins verified; audited favicon/header wiring is present; "
        "no forbidden placeholder or Labs surrogate identity remains."
    )


if __name__ == "__main__":
    main()
