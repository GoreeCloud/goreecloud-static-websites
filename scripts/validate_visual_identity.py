#!/usr/bin/env python3
"""Fail closed on GoreeCloud visual-identity drift in centralized static websites."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Byte-identity pins for every currently audited first-party site mark. These are
# exact Git blob IDs from GoreeCloud/goreecloud-branding-assets. A website copy is
# a deployable derivative, never an independent branding authority.
CANONICAL = {
    "sites/archive/assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "sites/blog/assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "sites/main/assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "sites/projects/assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "sites/projects/assets/glaze-ui-mark.svg": "7756ca8f04a588286e05e37e9a141dbea7f1965d",
    "sites/projects/assets/privacy-shield-icon.svg": "62b10029d4104d0235afe634c21f55d0a826a63d",
    "sites/projects/assets/wardveil-security-icon.svg": "fb3d643cca5477c3f8d4e03ce10a3458fd12f407",
    "sites/projects/assets/everkeep.svg": "5f70a483e06147193944c816291d42774a8648b2",
    "sites/projects/assets/goreecloud-mesh-mark.svg": "5362a52bd9fb38379f083a4d894934ed1acf9b67",
    "sites/projects/assets/identity.svg": "dc8287e385f86767f0105c48a8f234d8440d7623",
    "sites/roadmap/assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "sites/suite/assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "sites/design/assets/identity/official/facet/glaze-ui-mark.svg": "7756ca8f04a588286e05e37e9a141dbea7f1965d",
    "sites/privacy/branding/privacy-shield/privacy-shield-icon.svg": "62b10029d4104d0235afe634c21f55d0a826a63d",
    "sites/security/branding/wardveil-security-icon.svg": "fb3d643cca5477c3f8d4e03ce10a3458fd12f407",
    "sites/everkeep/assets/everkeep.svg": "5f70a483e06147193944c816291d42774a8648b2",
    "sites/identity/assets/identity.svg": "dc8287e385f86767f0105c48a8f234d8440d7623",
    "sites/manager/assets/manager-mark.svg": "024d82d5b5911e426216dfbd6a19d95cd6d71fc3",
    "sites/mesh/website/assets/goreecloud-mesh-mark.svg": "5362a52bd9fb38379f083a4d894934ed1acf9b67",
    "sites/labs/assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "sites/labs/assets/products/ai.svg": "1cbe04748f50cb843eef0cbb7233e2769efa275a",
    "sites/labs/assets/products/code.svg": "579f0416bd2839bf40e87de7751e319d80bd0bf9",
}

FORBIDDEN_ACTIVE_ASSET_NAMES = {
    "goreecloud-artwork-pending.svg",
}

# Primary public pages must expose the correct browser identity and a visible
# first-party header identity. This prevents a site from keeping the right SVG in
# the repository while silently regressing to a text-only or unrelated mark.
# Glaze-version migration is deliberately not checked here; that remains the
# separately governed controlled migration tracked by static-websites#14.
PAGE_IDENTITY = {
    "sites/archive/index.html": (
        '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
        '<img src="/assets/goreecloud-logo.svg" width="32" height="32" alt="">',
    ),
    "sites/blog/index.html": (
        '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
        '<img src="/assets/goreecloud-logo.svg" width="32" height="32" alt="">',
    ),
    "sites/main/index.html": (
        '<link rel="icon" href="assets/goreecloud-logo.svg" type="image/svg+xml">',
        '<img class="brand-logo" src="assets/goreecloud-logo.svg" alt="" width="36" height="36">',
    ),
    "sites/projects/index.html": (
        '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
        '<img src="/assets/goreecloud-logo.svg" alt="" width="38" height="38">',
        '<img src="/assets/glaze-ui-mark.svg" alt="" width="42" height="42">',
        '<img src="/assets/privacy-shield-icon.svg" alt="" width="42" height="42">',
        '<img src="/assets/wardveil-security-icon.svg" alt="" width="42" height="42">',
        '<img src="/assets/everkeep.svg" alt="" width="42" height="42">',
        '<img src="/assets/goreecloud-mesh-mark.svg" alt="" width="42" height="42">',
        '<img src="/assets/identity.svg" alt="" width="42" height="42">',
    ),
    "sites/roadmap/index.html": (
        '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
        '<img src="/assets/goreecloud-logo.svg" width="32" height="32" alt="">',
    ),
    "sites/suite/index.html": (
        '<link rel="icon" href="assets/goreecloud-logo.svg" type="image/svg+xml">',
        '<img src="assets/goreecloud-logo.svg" alt="" width="38" height="38">',
    ),
    "sites/design/website/index.html": (
        '<link rel="icon" href="/assets/glaze-ui-mark.svg" type="image/svg+xml">',
        '<img class="brand-mark" src="/assets/glaze-ui-mark.svg" alt="" width="34" height="34">',
    ),
    "sites/privacy/website/index.html": (
        '<link rel="icon" href="/assets/privacy-shield-icon.svg" type="image/svg+xml">',
        '<img src="/assets/privacy-shield-icon.svg" alt="" width="34" height="34">',
    ),
    "sites/security/website/index.html": (
        '<link rel="icon" href="/assets/wardveil-security-icon.svg" type="image/svg+xml">',
        '<img src="/assets/wardveil-security-icon.svg" alt="" width="34" height="34">',
    ),
    "sites/everkeep/website/index.html": (
        '<link rel="icon" href="assets/everkeep.svg" type="image/svg+xml">',
        '<img src="assets/everkeep.svg" alt="" width="38" height="38">',
    ),
    "sites/identity/index.html": (
        '<link rel="icon" href="/assets/identity.svg" type="image/svg+xml">',
        '<img src="/assets/identity.svg" width="42" height="42" alt="">',
    ),
    "sites/manager/index.html": (
        '<link rel="icon" href="/assets/manager-mark.svg" type="image/svg+xml">',
        '<img src="/assets/manager-mark.svg" width="40" height="40" alt="">',
    ),
    "sites/mesh/website/index.html": (
        '<link rel="icon" href="/assets/goreecloud-mesh-mark.svg" type="image/svg+xml">',
        '<img src="/assets/goreecloud-mesh-mark.svg" width="40" height="40" alt="">',
    ),
    "sites/labs/index.html": (
        '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
        '<img src="/assets/goreecloud-logo.svg" width="34" height="34" alt="">',
    ),
}

# Every existing first-party 404 surface that has an approved identity must retain
# the corresponding browser icon. Packages without a 404 source are intentionally
# absent; the validator does not manufacture files merely to satisfy itself.
ERROR_PAGE_IDENTITY = {
    "sites/archive/404.html": '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
    "sites/blog/404.html": '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
    "sites/main/404.html": '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
    "sites/projects/404.html": '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
    "sites/roadmap/404.html": '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
    "sites/design/website/404.html": '<link rel="icon" href="/assets/glaze-ui-mark.svg" type="image/svg+xml">',
    "sites/privacy/website/404.html": '<link rel="icon" href="/assets/privacy-shield-icon.svg" type="image/svg+xml">',
    "sites/security/website/404.html": '<link rel="icon" href="/assets/wardveil-security-icon.svg" type="image/svg+xml">',
    "sites/manager/404.html": '<link rel="icon" href="/assets/manager-mark.svg" type="image/svg+xml">',
    "sites/mesh/website/404.html": '<link rel="icon" href="/assets/goreecloud-mesh-mark.svg" type="image/svg+xml">',
    "sites/labs/404.html": '<link rel="icon" href="/assets/goreecloud-logo.svg" type="image/svg+xml">',
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
        f"{len(CANONICAL)} canonical asset pins verified across {len(PAGE_IDENTITY)} primary sites; "
        f"{len(ERROR_PAGE_IDENTITY)} existing error surfaces retain canonical browser identity; "
        "no forbidden placeholder or Labs surrogate identity remains."
    )


if __name__ == "__main__":
    main()
