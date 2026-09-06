#!/usr/bin/env python3
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Validate a simple GoreeCloud static site package")
parser.add_argument("site")
parser.add_argument("--glaze", default="2.1.0")
args = parser.parse_args()
root = Path(args.site)
required = ("index.html", "404.html", "_headers")
for name in required:
    if not (root / name).is_file():
        raise SystemExit(f"missing required static-site file: {root / name}")
index = (root / "index.html").read_text(encoding="utf-8")
error = (root / "404.html").read_text(encoding="utf-8")
headers = (root / "_headers").read_text(encoding="utf-8")
marker = f'name="goreecloud-glaze-ui" content="{args.glaze}"'
asset = f'data-glaze-ui="{args.glaze}"'
for page_name, page in (("index.html", index), ("404.html", error)):
    if marker not in page or asset not in page or "glaze-canvas" not in page:
        raise SystemExit(f"{page_name} is missing the active Glaze UI {args.glaze} contract")
for required_header in ("Content-Security-Policy:", "X-Content-Type-Options: nosniff", "frame-ancestors 'none'", "Permissions-Policy:"):
    if required_header not in headers:
        raise SystemExit(f"required security header missing: {required_header}")
for prohibited in ("google-analytics", "googletagmanager", "fonts.googleapis.com", "segment.com"):
    if prohibited in index.lower():
        raise SystemExit(f"prohibited runtime dependency: {prohibited}")
print(f"validated simple static site: {root}")
