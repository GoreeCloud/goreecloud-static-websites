#!/usr/bin/env python3
"""Verify the wide Design Center header keeps its canonical identity fully visible."""

from __future__ import annotations

import subprocess

import browser_artifact_smoke as smoke

WIDTH = 1440
HEIGHT = 900


def header_state(session_id: str):
    return smoke.execute(
        session_id,
        """
        const longLabel=document.querySelector('.brand-label-long');
        const shortLabel=document.querySelector('.brand-label-short');
        const brand=document.querySelector('.site-header .brand');
        const nav=document.querySelector('.site-header nav');
        const theme=document.querySelector('.theme-group');
        const rect=el=>{const r=el.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width};};
        const style=el=>getComputedStyle(el);
        return {
          width:innerWidth,
          scrollWidth:document.documentElement.scrollWidth,
          longText:(longLabel?.textContent||'').trim(),
          longDisplay:longLabel?style(longLabel).display:'missing',
          shortDisplay:shortLabel?style(shortLabel).display:'missing',
          longClient:longLabel?.clientWidth||0,
          longScroll:longLabel?.scrollWidth||0,
          longRect:longLabel?rect(longLabel):null,
          brand:brand?rect(brand):null,
          nav:nav?rect(nav):null,
          theme:theme?rect(theme):null,
        };
        """,
    )


def exercise(session_id: str) -> None:
    smoke.request("POST", f"/session/{session_id}/timeouts", {"implicit": 0, "pageLoad": 15000, "script": 10000})
    smoke.request("POST", f"/session/{session_id}/url", {"url": smoke.TARGET})
    smoke.set_viewport(session_id, WIDTH, HEIGHT)

    base = smoke.layout_state(session_id)
    smoke.require(int(base.get("width", 0)) == WIDTH, f"Unexpected Design Center wide viewport: {base}")
    smoke.require(int(base.get("scrollWidth", WIDTH + 10)) <= WIDTH + 1, f"Design Center wide header caused document overflow: {base}")
    smoke.require(int(base.get("bodyScrollWidth", WIDTH + 10)) <= WIDTH + 1, f"Design Center wide header caused body overflow: {base}")

    state = header_state(session_id)
    smoke.require(state.get("longText") == "GoreeCloud · Design Center · GLAZE UI", f"Design Center canonical brand text drift: {state}")
    smoke.require(state.get("longDisplay") != "none", f"Design Center long brand label is hidden at {WIDTH}px: {state}")
    smoke.require(state.get("shortDisplay") == "none", f"Design Center compact brand label remained visible at {WIDTH}px: {state}")
    smoke.require(int(state.get("longScroll", 1)) <= int(state.get("longClient", 0)) + 1, f"Design Center brand label is clipped or ellipsized at {WIDTH}px: {state}")

    brand = state.get("brand") or {}
    nav = state.get("nav") or {}
    theme = state.get("theme") or {}
    smoke.require(float(brand.get("right", WIDTH)) + 8 <= float(nav.get("left", -1)), f"Design Center brand overlaps primary navigation: {state}")
    smoke.require(float(nav.get("right", WIDTH)) + 8 <= float(theme.get("left", -1)), f"Design Center navigation overlaps appearance controls: {state}")


def main() -> int:
    smoke.require(smoke.DIST.is_dir() and (smoke.DIST / "index.html").is_file(), "Design Center dist/ is missing; run validate.py first")
    server = subprocess.Popen(
        ["python3", "-m", "http.server", str(smoke.WEB_PORT), "--bind", smoke.WEB_HOST, "--directory", str(smoke.DIST)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    driver = subprocess.Popen(
        [smoke.chromedriver(), f"--port={smoke.DRIVER_PORT}", "--allowed-ips=127.0.0.1"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    session_id = None
    try:
        smoke.wait_http()
        smoke.wait_for_driver()
        session_id = smoke.create_session()
        exercise(session_id)
        print("Design Center wide-header Chrome acceptance passed at 1440×900 with full canonical branding.")
        return 0
    finally:
        if session_id:
            try:
                smoke.request("DELETE", f"/session/{session_id}")
            except Exception:
                pass
        for process in (driver, server):
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
