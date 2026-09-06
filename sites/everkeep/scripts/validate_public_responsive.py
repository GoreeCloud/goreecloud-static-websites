#!/usr/bin/env python3
"""Fail closed on Continuity Center V1.1 responsive/public-document regressions."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "website" / "site-polish.css"
BASE = ROOT / "website" / "style.css"


def main() -> int:
    errors: list[str] = []
    css = CSS.read_text(encoding="utf-8")
    base = BASE.read_text(encoding="utf-8")

    required = {
        "V1.1 responsive integration label": "GLAZE UI V1.1 / 1.1.0",
        "public header remains in normal document flow": ".site-header{position:relative;inset-block-start:auto}",
        "narrow navigation remains a single horizontal row": ".nav nav{display:flex;width:100%;flex-wrap:nowrap;justify-content:flex-start",
        "narrow navigation scrolls locally instead of widening the page": "overflow-x:auto;overscroll-behavior-inline:contain;scrollbar-width:none;-webkit-overflow-scrolling:touch",
        "narrow navigation preserves a deliberate capsule surface": "border-radius:var(--ek-control-radius);background:color-mix(in srgb,var(--ek-surface) 88%,transparent)",
        "navigation targets do not shrink or wrap": ".nav nav a{flex:0 0 auto;width:auto;padding-inline:14px;white-space:nowrap;scroll-snap-align:start}",
        "webkit navigation scrollbar is hidden without disabling scroll": ".nav nav::-webkit-scrollbar{display:none}",
        "exact-width phone canvas can fit inside the usable viewport": "@media(max-width:380px){body.glaze-canvas{min-inline-size:0}",
        "narrow split/status tracks can shrink below min-content width": ".split,.status-grid{grid-template-columns:minmax(0,1fr)}",
        "split/status children cannot force horizontal overflow": ".split>*,.status-grid>*{min-inline-size:0;max-inline-size:100%}",
        "phone content cards collapse to one column": ".card-grid.six,.card-grid.four,.card-grid.three{grid-template-columns:1fr}",
        "recovery equation collapses to one column": ".equation{grid-template-columns:1fr}",
        "narrow action buttons become full width": ".actions .button{width:100%}",
        "public anchors do not reserve sticky-header space": "html{scroll-padding-top:24px}",
        "reduced transparency has an explicit fallback": "@media(prefers-reduced-transparency:reduce)",
        "forced colors has an explicit fallback": "@media(forced-colors:active)",
    }
    for label, marker in required.items():
        if marker not in css:
            errors.append(f"Missing responsive contract: {label}")

    for marker, label in (
        ("min-width:320px", "320px minimum canvas"),
        ("min-height:48px", "48px interaction floor"),
        ("@media(prefers-reduced-motion:reduce)", "reduced-motion fallback"),
        ("@media(prefers-reduced-transparency:reduce)", "reduced-transparency base fallback"),
        ("@media(forced-colors:active)", "forced-colors base fallback"),
    ):
        if marker not in base:
            errors.append(f"Missing base responsive/accessibility contract: {label}")

    forbidden = {
        "pre-reset Glaze token": "var(--glaze-",
        "multi-row tablet navigation": ".nav nav{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))",
        "multi-row phone navigation": ".nav nav{grid-template-columns:repeat(2,minmax(0,1fr))",
        "single-column navigation matrix": ".nav nav{grid-template-columns:1fr}",
    }
    for label, marker in forbidden.items():
        if marker in css:
            errors.append(f"Responsive layer contains {label}")

    if errors:
        print("Continuity Center responsive validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Continuity Center V1.1 responsive contract passed: normal-flow shell, locally scrollable narrow navigation, shrinkable content tracks, 320px fit, touch targets, and accessibility fallbacks are protected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
