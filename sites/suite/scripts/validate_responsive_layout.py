#!/usr/bin/env python3
"""Protect the Suite responsive composition found during public visual review."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")

REQUIRED = {
    "document-flow header": ".glaze-canvas .site-header{position:relative!important",
    "tablet two-column cards": "@media(max-width:920px){.principle-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.card-grid{grid-template-columns:repeat(2,minmax(0,1fr))}",
    "phone two-column navigation": ".glaze-canvas .site-header .glaze-navigation-capsule{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));width:100%",
    "phone single-column cards": ".principle-grid,.card-grid{grid-template-columns:1fr}",
    "phone full-width hero actions": ".hero-actions{display:grid;grid-template-columns:1fr}.hero-actions .button{width:100%}",
    "narrow-phone single-column navigation": "@media(max-width:380px){.glaze-canvas .site-header .glaze-navigation-capsule{grid-template-columns:1fr}",
}

missing = [label for label, marker in REQUIRED.items() if marker not in CSS]
if missing:
    print("Suite responsive layout validation failed:")
    for label in missing:
        print(f"- {label}")
    raise SystemExit(1)

print("Suite responsive layout contract passed: 3→2→1 cards, in-flow navigation, full-width phone actions, and narrow-phone navigation are protected.")
