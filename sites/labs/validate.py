#!/usr/bin/env python3
"""Validate source and built artifact for the six-product GoreeCloud public center."""
from __future__ import annotations
from pathlib import Path
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


def main() -> int:
    errors=[]
    index=(SITE/"index.html").read_text(encoding="utf-8")
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
    if "Disallow: /" not in (SITE/"robots.txt").read_text(encoding="utf-8"):
        errors.append("pre-publication robots.txt must disallow indexing")
    readme=(SITE/"README.md").read_text(encoding="utf-8")
    for marker in ("labs.goreecloud.com","GoreeCloud/goreecloud-static-websites","legacy source", "GoreeCloud Boot"):
        if marker not in readme:
            errors.append(f"README missing central/product boundary marker: {marker}")
    if DIST.exists():
        expected={"index.html","404.html","css/labs.css","_headers","robots.txt","css/site-v1.1.css","js/main.js","js/theme-init.js","assets/goreecloud-logo.svg"}|{f"css/glaze-v1/{n}" for n in GLAZE_FILES}
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
    if errors:
        print("Labs site validation failed:")
        [print(f"  - {e}") for e in errors]
        return 1
    print("Labs six-product center source validation passed; publication remains intentionally noindex and production-gated.")
    return 0

if __name__=="__main__":
    sys.exit(main())
