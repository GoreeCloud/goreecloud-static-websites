#!/usr/bin/env python3
"""Exercise the exact built GoreeCloud Main artifact in headless Chrome."""

from __future__ import annotations

from pathlib import Path
import subprocess
import time
from urllib.error import URLError
from urllib.request import urlopen

import browser_responsive_smoke as smoke
from build_public_site import DIST

WEB_HOST = "127.0.0.1"
WEB_PORT = 8770
TARGET = f"http://{WEB_HOST}:{WEB_PORT}/"
EXPECTED_PUBLIC_PROFILES = {
    "https://instagram.com/goreecloud",
    "https://www.threads.com/@goreecloud",
    "https://www.tiktok.com/@goreecloud",
    "https://x.com/GoreeCloud",
    "https://www.reddit.com/user/goreecloud/",
    "https://www.pinterest.com/goreecloud/",
    "https://www.youtube.com/@GoreeCloud",
    "https://github.com/GoreeCloud",
}


def wait_http(timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    last: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urlopen(TARGET, timeout=1) as response:
                if response.status == 200:
                    return
        except (URLError, TimeoutError, OSError) as error:
            last = error
        time.sleep(0.1)
    raise smoke.BrowserError(f"local Main artifact server did not become ready: {last}")


def overflow_diagnostics(session_id: str) -> object:
    return smoke.execute(
        session_id,
        r"""
        return [...document.querySelectorAll('body *')].map(node=>{
          const r=node.getBoundingClientRect();
          const style=getComputedStyle(node);
          return {
            tag:node.tagName.toLowerCase(),
            id:node.id||'',
            className:typeof node.className==='string'?node.className.slice(0,140):'',
            left:Math.round(r.left*100)/100,
            right:Math.round(r.right*100)/100,
            width:Math.round(r.width*100)/100,
            display:style.display,
            position:style.position,
            transform:style.transform,
            text:(node.textContent||'').trim().replace(/\s+/g,' ').slice(0,140),
          };
        }).filter(item=>item.width>0&&(item.left<-1||item.right>window.innerWidth+1)).slice(0,32);
        """,
    )


def validate_public_profiles(session_id: str) -> None:
    state = smoke.execute(
        session_id,
        r"""
        const follow=[...document.querySelectorAll('#follow .social-card')];
        const footer=[...document.querySelectorAll('.site-footer .footer-social-link')];
        const height=links=>links.length?Math.min(...links.map(link=>link.getBoundingClientRect().height)):0;
        return {
          followCount:follow.length,
          followUrls:follow.map(link=>link.getAttribute('href')),
          footerCount:footer.length,
          footerUrls:footer.map(link=>link.getAttribute('href')),
          footerMinHeight:height(footer),
          scopeNote:(document.querySelector('#follow .social-scope-note')?.textContent||'').trim(),
          footerLabel:(document.querySelector('.site-footer .footer-social-label')?.textContent||'').trim(),
          socialColumns:getComputedStyle(document.querySelector('#follow .social-grid')).gridTemplateColumns.split(/\s+/).filter(Boolean).length,
          width:window.innerWidth,
          scrollWidth:document.documentElement.scrollWidth,
        };
        """,
    )
    smoke.require(isinstance(state, dict), f"Could not read Main public-profile state: {state!r}")
    follow_urls = set(state.get("followUrls") or [])
    footer_urls = set(state.get("footerUrls") or [])
    smoke.require(int(state.get("followCount", 0)) == 8, f"Main Follow section must render eight public profiles: {state}")
    smoke.require(int(state.get("footerCount", 0)) == 8, f"Main footer must expose eight direct public-profile links: {state}")
    smoke.require(follow_urls == EXPECTED_PUBLIC_PROFILES, f"Main Follow profile inventory drifted: {state}")
    smoke.require(footer_urls == EXPECTED_PUBLIC_PROFILES, f"Main footer profile inventory drifted: {state}")
    smoke.require("Six active GoreeCloud social-media accounts" in str(state.get("scopeNote", "")), f"Main social scope boundary missing: {state}")
    smoke.require(state.get("footerLabel") == "Follow GoreeCloud", f"Main footer social label missing: {state}")
    smoke.require(float(state.get("footerMinHeight", 0)) >= 47.5, f"Main footer public-profile target below 48px: {state}")
    width = int(state.get("width", 0))
    smoke.require(int(state.get("scrollWidth", width + 10)) <= width + 1, f"Main public-profile UI causes horizontal overflow: {state}")
    if width <= 720:
        smoke.require(int(state.get("socialColumns", 0)) == 1, f"Main social grid must collapse to one column at mobile width: {state}")


def main() -> int:
    smoke.require(DIST.is_dir() and (DIST / "index.html").is_file(), "Main dist/ artifact is missing; run build first")
    server: subprocess.Popen[bytes] | None = None
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: Path | None = None
    try:
        server = subprocess.Popen(
            ["python3", "-m", "http.server", str(WEB_PORT), "--bind", WEB_HOST, "--directory", str(DIST)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        wait_http()

        import tempfile

        with tempfile.NamedTemporaryFile(prefix="goreecloud-main-artifact-chromedriver-", suffix=".log", delete=False) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen(
                [smoke.chromedriver(), f"--port={smoke.PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        smoke.wait_for_driver()
        session_id = smoke.create_session()
        smoke.exercise(session_id, TARGET)
        validate_public_profiles(session_id)
        print(
            "Main built-artifact responsive Chrome smoke passed at 1180×900, 768×900, 390×844, and 320×844, including bounded mobile navigation and complete public-profile discoverability."
        )
        return 0
    except Exception as error:
        print(f"Main built-artifact responsive Chrome smoke failed: {error}")
        if session_id:
            try:
                offenders = overflow_diagnostics(session_id)
            except Exception as diagnostic_error:
                print(f"Viewport overflow diagnostics unavailable: {diagnostic_error}")
            else:
                print(f"Viewport overflow offenders: {offenders}")
        if log_path:
            try:
                text = log_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            if text:
                print(text[-8000:])
        return 1
    finally:
        if session_id:
            try:
                smoke.request("DELETE", f"/session/{session_id}")
            except Exception:
                pass
        for process in (driver, server):
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
        if log_path:
            try:
                log_path.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
