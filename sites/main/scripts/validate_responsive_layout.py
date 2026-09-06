#!/usr/bin/env python3
"""Fail closed on Main V1.1 responsive and accessibility-fallback regressions."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "css" / "site-v1.1.css"


def main() -> int:
    errors: list[str] = []
    css = CSS.read_text(encoding="utf-8") if CSS.is_file() else ""
    checks = (
        ("min-width: 320px", "minimum supported layout width"),
        ("min-height: 48px", "48px interaction target floor"),
        ("@media (max-width: 980px)", "tablet/intermediate breakpoint"),
        (".primary-nav { grid-column: 1 / -1; justify-self: stretch; display: none;", "closed intermediate navigation"),
        (".primary-nav.is-open { display: flex; }", "explicit open navigation state"),
        (".nav-toggle { display: inline-flex;", "navigation trigger at narrow widths"),
        (".hero-grid, .split-section, .architecture-grid { grid-template-columns: 1fr; }", "major layout collapse"),
        ("@media (max-width: 700px)", "phone breakpoint"),
        (".principle-grid, .destination-grid, .repo-grid { grid-template-columns: 1fr; }", "phone content grids"),
        ("@media (max-width: 440px)", "narrow-phone breakpoint"),
        (".actions { flex-direction: column; }", "narrow-phone actions"),
        ("@media (prefers-reduced-motion: reduce)", "reduced-motion fallback"),
        ("@media (prefers-reduced-transparency: reduce)", "reduced-transparency fallback"),
        ("@media (forced-colors: active)", "forced-colors fallback"),
    )
    for marker, label in checks:
        if marker not in css:
            errors.append(f"missing responsive contract: {label}")

    for page_name in ("index.html", "repositories.html", "privacy.html", "security.html", "404.html"):
        page = (ROOT / page_name).read_text(encoding="utf-8")
        for marker in ('class="nav-toggle', 'aria-expanded="false"', 'aria-controls="primary-nav"', 'class="appearance-toggle'):
            if marker not in page:
                errors.append(f"{page_name} missing responsive/interaction marker: {marker}")

    if errors:
        print("Main responsive layout validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Main V1.1 responsive source contract passed for desktop, tablet, phone, and accessibility fallbacks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
