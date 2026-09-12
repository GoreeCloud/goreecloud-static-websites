#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
INDEX = (ROOT / "index.html").read_text()
HEADERS = (ROOT / "_headers").read_text()

required = [
    "https://firefox.goreecloud.com/",
    "GoreeCloud Firefox Extensions",
    "GoreeCloud Bookmarks",
    "GoreeCloud Download Manager Extension",
    "GoreeCloud Privacy Shield",
    "GoreeCloud Redirector",
    "GoreeCloud Source Resync",
    "0.2.12",
    "0.2.0",
    "1.1.2",
    'data-glaze-version="1.3.0"',
]
for marker in required:
    if marker not in INDEX:
        raise SystemExit(f"missing required Firefox-site marker: {marker}")
for forbidden in ("Stable 0.1.1", "Stable 1.1.2", "Mozilla Add-ons listing"):
    if forbidden in INDEX:
        raise SystemExit(f"unsupported release claim: {forbidden}")
for header in ("Content-Security-Policy", "Strict-Transport-Security: max-age=31536000", "X-Content-Type-Options: nosniff"):
    if header not in HEADERS:
        raise SystemExit(f"missing required security header: {header}")

inventory_path = REPO.parent / "goreecloud-firefox-extensions" / "docs" / "extension-inventory.json"
if inventory_path.exists():
    inventory = json.loads(inventory_path.read_text())
    names = {item["name"] for item in inventory["extensions"]}
    for name in names:
        if name not in INDEX:
            raise SystemExit(f"homepage missing extension from canonical inventory: {name}")

subprocess.run(["python3", str(ROOT / "build.py")], check=True)
for name in ("index.html", "404.html", "site.css", "site.js", "_headers", "robots.txt", "sitemap.xml"):
    if not (ROOT / "dist" / name).is_file():
        raise SystemExit(f"build missing artifact: {name}")
print("Firefox Extensions site validation passed")
