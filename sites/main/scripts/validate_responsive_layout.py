#!/usr/bin/env python3
"""Fail closed if the public-site responsive composition regresses.

This is intentionally a source contract, not a claim of rendered visual acceptance.
Real-browser preview checks remain separate where configured. The purpose of this
gate is to prevent the exact desktop-density and content-obscuring patterns found
during full-page review from silently returning.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(source: str, marker: str, label: str, errors: list[str]) -> None:
    if marker not in source:
        errors.append(f"Missing responsive contract: {label}")


def validate() -> list[str]:
    errors: list[str] = []

    homepage = text("css/homepage-v6.css")
    main_styles = text("css/style.css")
    for marker, label in (
        ("body.glaze-canvas .site-header", "Main header stays in document flow"),
        ("@media (max-width: 820px)", "Main tablet breakpoint exists"),
        ("@media (max-width: 600px)", "Main phone breakpoint exists"),
        (".timeline,\n  .how-flow,\n  #platform .service-grid,\n  .roadmap-grid,\n  .social-grid {\n    grid-template-columns: 1fr;", "Main dense content grids collapse to one column on phones"),
        (".repository-teaser-stats { grid-template-columns: 1fr; }", "Main repository stats collapse at narrow phone width"),
        (".hero-actions .button,\n  .repository-teaser-actions .button {\n    width: 100%;", "Main phone actions become full-width"),
        ("background: color-mix(in srgb, var(--glaze-surface-elevated) 94%, transparent);", "Main open mobile navigation has an explicit Glaze interaction surface"),
    ):
        require(homepage, marker, label, errors)

    for marker, label in (
        ("width: min(20rem, calc(100vw - 1.4rem));", "Main mobile navigation is width-bounded"),
        ("max-height: calc(100dvh - 96px - env(safe-area-inset-bottom));", "Main mobile navigation is viewport-height bounded"),
        (".site-nav:not(.open) { display: none; }", "Main closed mobile navigation cannot cover content"),
        ("grid-template-columns: repeat(2, minmax(0, 1fr));", "Main open mobile navigation uses compact touch columns"),
        ("overscroll-behavior: contain;", "Main mobile navigation contains local scrolling"),
        (".site-nav.open .nav-cta { grid-column: 1 / -1; }", "Main mobile call-to-action spans the popover"),
    ):
        require(main_styles, marker, label, errors)

    websites = text("css/websites.css")
    for marker, label in (
        ("@media (max-width: 820px)", "Website directory single-column breakpoint exists"),
        (".websites-section .website-grid > .website-card:nth-child(n)", "Website directory overrides high-specificity desktop spans on narrow screens"),
        ("grid-column: 1 / -1;", "Website cards reset to the complete narrow grid row"),
        ("inline-size: 100%;", "Website cards fill the complete narrow row"),
        ("max-inline-size: none;", "Website cards have no narrow max-size cap"),
    ):
        require(websites, marker, label, errors)

    repositories = text("css/repositories.css")
    for marker, label in (
        (".glaze-canvas .site-header { position: relative; inset-block-start: auto; }", "Repository directory header stays in document flow"),
        ("@media (max-width: 900px)", "Repository directory collapses to one card column before phone width"),
        (".repo-grid { grid-template-columns: 1fr; }", "Repository cards become one readable column"),
        ("@media (max-width: 720px)", "Repository mobile navigation breakpoint exists"),
        (".site-header .site-nav { position: static;", "Repository mobile navigation stays in document flow"),
        ("grid-template-columns: repeat(2, minmax(0, 1fr));", "Repository phone navigation uses deliberate touch columns"),
        (".site-header .site-nav a { min-height: 48px;", "Repository navigation preserves the 48px target floor"),
        ("@media (max-width: 420px) { .site-header .site-nav.open { grid-template-columns: 1fr; }", "Repository navigation becomes one column at narrow width"),
        (".repo-visibility-buttons { grid-template-columns: 1fr; }", "Repository visibility filters stack on phones"),
    ):
        require(repositories, marker, label, errors)

    projects = text("sites/projects/assets/mobile-refresh.css")
    for marker, label in (
        ("body.glaze-canvas .topbar{position:relative", "Projects header stays in document flow"),
        ("@media(max-width:820px)", "Projects tablet breakpoint exists"),
        ("@media(max-width:580px)", "Projects phone breakpoint exists"),
        (".foundation-strip,.grid{grid-template-columns:1fr}", "Projects foundation and directory grids collapse on phones"),
        ("@media(max-width:390px){.topbar nav{grid-template-columns:1fr}", "Projects navigation becomes one column on narrow phones"),
    ):
        require(projects, marker, label, errors)

    blog = text("sites/blog/style.css")
    for marker, label in (
        ("body.glaze-canvas .top{position:relative", "Blog header stays in document flow"),
        ("@media(max-width:1060px){.card{grid-column:span 6}", "Blog uses an intermediate two-column layout"),
        ("@media(max-width:760px)", "Blog phone breakpoint exists"),
        (".card,.featured{grid-column:1/-1", "Blog cards become single-column on phones"),
        ("@media(max-width:420px){.top nav{grid-template-columns:1fr}", "Blog navigation becomes one column on narrow phones"),
    ):
        require(blog, marker, label, errors)

    roadmap = text("sites/roadmap/site.css")
    for marker, label in (
        ("body.glaze-canvas .site-header{position:relative", "Roadmap header stays in document flow"),
        ("@media(max-width:700px)", "Roadmap phone breakpoint exists"),
        (".cards{grid-template-columns:1fr}", "Roadmap cards become single-column on phones"),
        ("@media(max-width:420px){.nav nav{grid-template-columns:1fr}", "Roadmap navigation becomes one column on narrow phones"),
    ):
        require(roadmap, marker, label, errors)

    archive = text("sites/archive/style.css")
    for marker, label in (
        ("body.glaze-canvas .top{position:relative", "Archive header stays in document flow"),
        ("@media(max-width:760px)", "Archive phone breakpoint exists"),
        ("@media(max-width:430px){.top nav{grid-template-columns:1fr}", "Archive navigation becomes one column on narrow phones"),
        (".timeline{margin-left:0;padding-left:0;border-left:0}", "Archive timeline simplifies on narrow phones"),
    ):
        require(archive, marker, label, errors)

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Responsive layout validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Responsive layout source contract passed for Main, Repositories, Projects, Blog, Roadmap, and Archive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
