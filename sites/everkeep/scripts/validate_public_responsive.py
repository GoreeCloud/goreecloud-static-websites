#!/usr/bin/env python3
"""Fail closed on Continuity Center GLAZE UI V1.3 responsive/public layout regressions."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
POLISH = ROOT / "website" / "site-polish.css"
V13 = ROOT / "website" / "v1.3-site.css"
INDEX = ROOT / "website" / "index.html"


def main() -> int:
    errors: list[str] = []
    css = POLISH.read_text(encoding="utf-8")
    v13 = V13.read_text(encoding="utf-8")
    html = INDEX.read_text(encoding="utf-8")

    required = {
        "public header remains in normal document flow": ".site-header{position:relative;inset-block-start:auto}",
        "narrow navigation remains a single horizontal row": ".nav nav{display:flex;width:100%;flex-wrap:nowrap;justify-content:flex-start",
        "narrow navigation scrolls locally instead of widening the page": "overflow-x:auto;overscroll-behavior-inline:contain;scrollbar-width:none;-webkit-overflow-scrolling:touch",
        "narrow navigation uses a bounded Glaze surface": "border:1px solid var(--glaze-line,#d7e1ee);border-radius:var(--glaze-radius-control,999px);background:color-mix(in srgb,var(--glaze-surface-strong,#fff) 88%,transparent)",
        "navigation targets do not shrink or wrap": ".nav nav a{flex:0 0 auto;width:auto;padding-inline:14px;white-space:nowrap;scroll-snap-align:start}",
        "webkit navigation scrollbar is hidden without disabling scroll": ".nav nav::-webkit-scrollbar{display:none}",
        "exact-width phone canvas can fit inside the usable viewport": "@media(max-width:380px){body.glaze-canvas{min-inline-size:0}",
        "narrow split/status tracks can shrink below min-content width": ".split,.status-grid{grid-template-columns:minmax(0,1fr)}",
        "split/status children cannot force horizontal overflow": ".split>*,.status-grid>*{min-inline-size:0;max-inline-size:100%}",
        "phone content cards collapse to one column": ".card-grid.six,.card-grid.four,.card-grid.three{grid-template-columns:1fr}",
        "recovery equation collapses to one column": ".equation{grid-template-columns:1fr}",
        "narrow action buttons become full width": ".actions .button{width:100%}",
        "public anchors do not reserve sticky-header space": "html{scroll-padding-top:24px}",
    }
    for label, marker in required.items():
        if marker not in css:
            errors.append(f"Missing responsive contract: {label}")

    for label, marker in {
        "48px interaction floor": "--everkeep-v13-control:48px",
        "56px assisted/coarse interaction floor": "--everkeep-v13-control-assisted:56px",
        "visible keyboard focus": "focus-visible",
        "coarse-pointer adaptation": "@media(pointer:coarse)",
        "reduced motion": "prefers-reduced-motion:reduce",
        "reduced transparency": "prefers-reduced-transparency:reduce",
        "increased contrast": "prefers-contrast:more",
        "forced colors": "forced-colors:active",
        "print fallback": "@media print",
    }.items():
        if marker not in v13:
            errors.append(f"Missing GLAZE UI V1.3 adaptation: {label}")

    for marker in (
        'data-glaze-version="1.3.0"',
        'name="goreecloud-glaze-ui" content="1.3.0"',
        'name="goreecloud-glaze-source-revision" content="8354308445da9ac35ced2b37a7f503a08a0aaf72"',
        'name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"',
        '/assets/glaze-v1.3.0.css',
        '/assets/v1.3-site.css',
    ):
        if marker not in html:
            errors.append(f"Missing Continuity Center V1.3 source marker: {marker}")

    for stale in ('glaze-ui-2.1.0.css', 'data-glaze-ui="2.1.0"', 'content="2.1.0"'):
        if stale in html:
            errors.append(f"Continuity Center still activates superseded Glaze source: {stale}")

    forbidden = {
        "multi-row tablet navigation": ".nav nav{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))",
        "multi-row phone navigation": ".nav nav{grid-template-columns:repeat(2,minmax(0,1fr))",
        "single-column navigation matrix": ".nav nav{grid-template-columns:1fr}",
    }
    for label, marker in forbidden.items():
        if marker in css:
            errors.append(f"Responsive navigation regressed to {label}")

    sticky = css.rfind(".site-header{position:sticky")
    normal_flow = css.rfind(".site-header{position:relative;inset-block-start:auto}")
    if sticky >= 0 and normal_flow <= sticky:
        errors.append("Final Continuity Center cascade does not keep public navigation in normal document flow")

    if errors:
        print("Continuity Center GLAZE UI V1.3 responsive validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Continuity Center GLAZE UI V1.3 responsive source contract passed; rendered, deployment, recovery-effect, and production acceptance remain separate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
