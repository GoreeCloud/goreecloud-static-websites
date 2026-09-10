#!/usr/bin/env python3
"""Validate source and built artifact for the six-product GoreeCloud public center."""
from __future__ import annotations
from pathlib import Path
import hashlib
import sys

SITE = Path(__file__).resolve().parent
DIST = SITE / "dist"
sys.path.insert(0, str(SITE / "scripts"))
from glaze_v1 import FILES as GLAZE_FILES, validate_bundle  # noqa: E402

PRODUCTS = (
    "GoreeCloud Home Security",
    "GoreeCloud Home",
    "GoreeCloud AI",
    "GoreeCloud Containers",
    "GoreeCloud Code",
    "GoreeCloud Boot",
)

CANONICAL_ASSETS = {
    "assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "assets/products/ai.svg": "1cbe04748f50cb843eef0cbb7233e2769efa275a",
    "assets/products/code.svg": "579f0416bd2839bf40e87de7751e319d80bd0bf9",
}


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> int:
    errors=[]
    index=(SITE/"index.html").read_text(encoding="utf-8")
    css=(SITE/"labs.css").read_text(encoding="utf-8")
    for product in PRODUCTS:
        if product not in index:
            errors.append(f"missing canonical product name: {product}")
    for marker in ('data-glaze-version="1.1"','content="1.1.0"','data-glaze-ui="1.1.0"','meta name="robots" content="noindex,nofollow"'):
        if marker not in index:
            errors.append(f"index missing source marker: {marker}")
    for forbidden in ("Frigate alternative","Home Assistant alternative","production-ready"):
        if forbidden in index:
            errors.append(f"public product copy contains disallowed maturity/upstream framing: {forbidden}")
    for section in ("Implemented foundation","Still gated","Cloudflare Pages boundary","This website explains the products. It does not host them."):
        if section not in index:
            errors.append(f"index missing truthfulness boundary: {section}")

    # Approved artwork must be actual image content, not CSS-painted or textual surrogate identity.
    for marker in (
        '<img class="product-mark" src="/assets/products/ai.svg"',
        '<img class="product-mark" src="/assets/products/code.svg"',
    ):
        if marker not in index:
            errors.append(f"Labs canonical product artwork missing from markup: {marker}")
    if index.count('class="product-mark"') != 2:
        errors.append("Labs must render exactly the two currently approved product marks (AI and Code)")
    for forbidden in (
        'class="text-mark"',
        '>Home</span>',
        '>Security</span>',
        '>OCI</span>',
        '>Boot</span>',
    ):
        if forbidden in index:
            errors.append(f"Labs surrogate product identity remains in markup: {forbidden}")
    for forbidden in (".text-mark", "background-image: url(\"/assets/products/ai.svg\")", "background-image: url(\"/assets/products/code.svg\")"):
        if forbidden in css:
            errors.append(f"Labs surrogate/CSS-painted identity remains in stylesheet: {forbidden}")
    if ".product-mark" not in css:
        errors.append("Labs canonical product artwork sizing contract is missing")

    for rel, expected in CANONICAL_ASSETS.items():
        path = SITE / rel
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing canonical asset: {rel}")
            continue
        actual = git_blob_sha(path)
        if actual != expected:
            errors.append(f"canonical asset drift: {rel}: expected {expected}, got {actual}")
    if "Disallow: /" not in (SITE/"robots.txt").read_text(encoding="utf-8"):
        errors.append("pre-publication robots.txt must disallow indexing")
    readme=(SITE/"README.md").read_text(encoding="utf-8")
    for marker in ("labs.goreecloud.com","GoreeCloud/goreecloud-static-websites","legacy source", "GoreeCloud Boot"):
        if marker not in readme:
            errors.append(f"README missing central/product boundary marker: {marker}")
    identity=(SITE/"IDENTITY-ASSETS.md").read_text(encoding="utf-8") if (SITE/"IDENTITY-ASSETS.md").is_file() else ""
    for marker in ("GoreeCloud Home", "GoreeCloud Home Security", "GoreeCloud Containers", "GoreeCloud Boot", "branding-assets#16"):
        if marker not in identity:
            errors.append(f"identity authority record missing: {marker}")
    if DIST.exists():
        expected={"index.html","404.html","css/labs.css","_headers","robots.txt","css/site-v1.1.css","js/main.js","js/theme-init.js","assets/goreecloud-logo.svg","assets/products/ai.svg","assets/products/code.svg"}|{f"css/glaze-v1/{n}" for n in GLAZE_FILES}
        actual={str(p.relative_to(DIST)) for p in DIST.rglob("*") if p.is_file()}
        if actual!=expected:
            errors.append(f"artifact file set mismatch; missing={sorted(expected-actual)} unexpected={sorted(actual-expected)}")
        bundle={}
        for name in GLAZE_FILES:
            p=DIST/"css"/"glaze-v1"/name
            if p.is_file():
                bundle[name]=p.read_text(encoding="utf-8")
        try:
            validate_bundle(bundle)
        except ValueError as exc:
            errors.append(str(exc))
        for rel, expected_sha in CANONICAL_ASSETS.items():
            p=DIST/rel
            if p.is_file() and git_blob_sha(p) != expected_sha:
                errors.append(f"built artifact canonical asset drift: {rel}")
        built_index = (DIST / "index.html").read_text(encoding="utf-8") if (DIST / "index.html").is_file() else ""
        if built_index.count('class="product-mark"') != 2 or 'class="text-mark"' in built_index:
            errors.append("built Labs artifact does not preserve the canonical-artwork/no-surrogate boundary")
    if errors:
        print("Labs site validation failed:")
        [print(f"  - {e}") for e in errors]
        return 1
    print("Labs six-product center source validation passed; canonical AI/Code artwork is direct markup and products lacking approved artwork have no surrogate identity.")
    return 0

if __name__=="__main__":
    sys.exit(main())
