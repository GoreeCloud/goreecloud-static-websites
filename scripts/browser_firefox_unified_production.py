#!/usr/bin/env python3
"""Exercise the selected unified Firefox Extensions publication in headless Chrome."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CANONICAL = "https://www.goreecloud.com/firefox-extensions/"
VERIFY_ORIGIN = os.environ.get("FIREFOX_VERIFY_ORIGIN", "https://www.goreecloud.com").rstrip("/")
TARGET = VERIFY_ORIGIN + "/firefox-extensions/"
VIEWPORTS = ((1180, 900), (768, 900), (390, 844), (320, 844))
DRIVER_PORT = 9540
DRIVER_BASE = f"http://127.0.0.1:{DRIVER_PORT}"
TIMEOUT = 20
GLAZE_VERSION = "1.4.1"
GLAZE_REVISION = "4fab9da0fad2e5c974e0e66ec88632c61745751c"


class BrowserError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BrowserError(message)


def request(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(
        f"{DRIVER_BASE}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            raw = response.read()
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise BrowserError(f"WebDriver HTTP {error.code} for {path}: {detail}") from error
    except (URLError, TimeoutError) as error:
        raise BrowserError(f"WebDriver request failed for {path}: {error}") from error
    if not raw:
        return None
    value = json.loads(raw.decode("utf-8")).get("value")
    if isinstance(value, dict) and value.get("error"):
        raise BrowserError(f"WebDriver {value.get('error')} for {path}: {value.get('message', '')}")
    return value


def chromedriver() -> str:
    for candidate in (shutil.which("chromedriver"), "/usr/local/share/chromedriver-linux64/chromedriver"):
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise BrowserError("chromedriver is unavailable on the runner")


def wait_for_driver() -> None:
    deadline = time.monotonic() + 15
    last: Exception | None = None
    while time.monotonic() < deadline:
        try:
            status = request("GET", "/status")
            if isinstance(status, dict) and status.get("ready"):
                return
        except Exception as error:
            last = error
        time.sleep(0.2)
    raise BrowserError(f"chromedriver did not become ready: {last}")


def create_session() -> str:
    value = request(
        "POST",
        "/session",
        {
            "capabilities": {
                "alwaysMatch": {
                    "browserName": "chrome",
                    "goog:chromeOptions": {
                        "args": [
                            "--headless=new",
                            "--no-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-background-networking",
                            "--disable-component-update",
                            "--disable-default-apps",
                            "--disable-extensions",
                            "--disable-sync",
                            "--metrics-recording-only",
                            "--no-first-run",
                            "--window-size=1180,900",
                        ]
                    },
                }
            }
        },
    )
    require(isinstance(value, dict), f"Unexpected Chrome session response: {value!r}")
    session_id = value.get("sessionId")
    require(isinstance(session_id, str) and session_id, "Chrome did not return a session id")
    return session_id


def execute(session_id: str, script: str) -> Any:
    return request("POST", f"/session/{session_id}/execute/sync", {"script": script, "args": []})


def execute_async(session_id: str, script: str) -> Any:
    return request("POST", f"/session/{session_id}/execute/async", {"script": script, "args": []})


def cdp(session_id: str, command: str, params: dict[str, Any] | None = None) -> Any:
    return request(
        "POST",
        f"/session/{session_id}/goog/cdp/execute",
        {"cmd": command, "params": params or {}},
    )


def set_viewport(session_id: str, width: int, height: int) -> None:
    cdp(
        session_id,
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False},
    )
    execute(session_id, "window.scrollTo(0,0); return true;")


def verify_image_decode(session_id: str) -> None:
    value = execute_async(
        session_id,
        r"""
        const done = arguments[arguments.length - 1];
        const images = [...document.images];
        Promise.all(images.map(async img => {
          try {
            await img.decode();
            const r = img.getBoundingClientRect();
            const s = getComputedStyle(img);
            return {
              src: img.getAttribute('src'), currentSrc: img.currentSrc,
              complete: img.complete, decoded: true,
              width: r.width, height: r.height,
              display: s.display, visibility: s.visibility,
              naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight,
            };
          } catch (error) {
            const r = img.getBoundingClientRect();
            return {
              src: img.getAttribute('src'), currentSrc: img.currentSrc,
              complete: img.complete, decoded: false,
              width: r.width, height: r.height,
              error: String(error), naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight,
            };
          }
        })).then(done).catch(error => done({fatal: String(error)}));
        """,
    )
    require(isinstance(value, list) and value, f"Could not decode Firefox publication images: {value!r}")
    failures = [
        item
        for item in value
        if not item.get("decoded")
        or not item.get("complete")
        or float(item.get("width", 0)) <= 0
        or float(item.get("height", 0)) <= 0
        or item.get("display") == "none"
        or item.get("visibility") == "hidden"
    ]
    require(not failures, f"Firefox publication image decode/render failure at {VERIFY_ORIGIN}: {failures}")


def state(session_id: str) -> dict[str, Any]:
    value = execute(
        session_id,
        r"""
        const visible=el=>{const s=getComputedStyle(el),r=el.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;};
        const cards=[...document.querySelectorAll('#extensions .card')].filter(visible);
        const nav=[...document.querySelectorAll('.site-header nav a,.site-header nav button')].filter(visible);
        const buttons=[...document.querySelectorAll('.button')].filter(visible);
        const images=[...document.images];
        const interactive=[...document.querySelectorAll('a,button,input,select,textarea')].filter(visible);
        const unnamed=interactive.filter(el=>!(el.getAttribute('aria-label')||el.getAttribute('aria-labelledby')||el.textContent||'').trim());
        const geometry=[...document.querySelectorAll('.wrap,.hero-grid,.summary,#extensions .grid,.principles,.callout,.footer')]
          .filter(visible).map(el=>{const r=el.getBoundingClientRect();return {className:el.className,left:r.left,right:r.right,width:r.width};});
        const imageBoxes=images.map(img=>{const r=img.getBoundingClientRect(),s=getComputedStyle(img);return {src:img.getAttribute('src'),currentSrc:img.currentSrc,complete:img.complete,left:r.left,right:r.right,width:r.width,height:r.height,display:s.display,visibility:s.visibility};});
        const columns=el=>getComputedStyle(el).gridTemplateColumns.split(/\s+/).filter(Boolean).length;
        return {
          ready:document.readyState,title:document.title,url:location.href,width:innerWidth,height:innerHeight,
          scrollWidth:document.documentElement.scrollWidth,bodyScrollWidth:document.body.scrollWidth,
          glaze:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',
          revision:document.querySelector('meta[name="goreecloud-glaze-source-revision"]')?.content||'',
          schema:document.querySelector('meta[name="goreecloud-extension-inventory-schema"]')?.content||'',
          canonical:document.querySelector('link[rel="canonical"]')?.href||'',cards:cards.length,
          stableCards:cards.filter(card=>card.querySelector('.status.stable')).length,
          cardColumns:cards.length?columns(document.querySelector('#extensions .grid')):0,
          principleColumns:columns(document.querySelector('.principles')),
          minNavHeight:nav.length?Math.min(...nav.map(el=>el.getBoundingClientRect().height)):0,
          minButtonHeight:buttons.length?Math.min(...buttons.map(el=>el.getBoundingClientRect().height)):0,
          imageBoxes,
          unnamedInteractive:unnamed.map(el=>el.outerHTML.slice(0,180)),
          mainCount:document.querySelectorAll('main').length,
          primaryNavCount:document.querySelectorAll('nav[aria-label="Primary"]').length,
          h1Count:document.querySelectorAll('h1').length,
          skipLinkExists:Boolean(document.querySelector('.skip-link[href="#main"]')),
          geometry,
        };
        """,
    )
    require(isinstance(value, dict), f"Could not read Firefox publication browser state: {value!r}")
    return value


def verify_skip_link(session_id: str, width: int, height: int) -> None:
    value = execute(
        session_id,
        """
        const link=document.querySelector('.skip-link'); if(!link)return null;
        link.focus(); const b=link.getBoundingClientRect();
        return {active:document.activeElement===link,rect:{left:b.left,right:b.right,top:b.top,bottom:b.bottom}};
        """,
    )
    require(isinstance(value, dict) and value.get("active") is True, f"Firefox skip link is not keyboard focusable at {width}px: {value}")
    rect = value.get("rect") or {}
    require(
        float(rect.get("left", -999)) >= -1
        and float(rect.get("right", 99999)) <= width + 1
        and float(rect.get("top", -999)) >= -1
        and float(rect.get("bottom", 99999)) <= height + 1,
        f"Firefox skip link is outside the viewport when focused at {width}px: {value}",
    )


def verify_accessibility_tree(session_id: str) -> None:
    cdp(session_id, "Accessibility.enable")
    tree = cdp(session_id, "Accessibility.getFullAXTree")
    require(isinstance(tree, dict) and isinstance(tree.get("nodes"), list), f"Could not read Chrome accessibility tree: {tree!r}")
    nodes = [node for node in tree["nodes"] if not node.get("ignored")]
    roles = [str((node.get("role") or {}).get("value") or "") for node in nodes]
    for role in ("main", "navigation", "heading"):
        require(role in roles, f"Firefox accessibility tree has no {role} role")
    interactive = [node for node in nodes if str((node.get("role") or {}).get("value") or "") in {"button", "link"}]
    unnamed = [node for node in interactive if not str((node.get("name") or {}).get("value") or "").strip()]
    require(not unnamed, f"Firefox accessibility tree contains unnamed interactive controls: {unnamed[:5]}")


def verify_theme(session_id: str) -> None:
    value = execute(
        session_id,
        """
        const b=document.querySelector('#theme-toggle'); if(!b)return null;
        const before=document.documentElement.getAttribute('data-theme'); b.click();
        const after=document.documentElement.getAttribute('data-theme'); const stored=localStorage.getItem('goreecloud-theme');
        b.click(); return {before,after,stored,final:document.documentElement.getAttribute('data-theme')};
        """,
    )
    require(isinstance(value, dict), f"Firefox appearance control is missing: {value!r}")
    require(value.get("after") in {"light", "dark"}, f"Firefox appearance control did not set an explicit theme: {value}")
    require(value.get("stored") == value.get("after"), f"Firefox appearance choice did not persist: {value}")


def exercise(session_id: str) -> None:
    request("POST", f"/session/{session_id}/timeouts", {"implicit": 0, "pageLoad": 20000, "script": 15000})
    request("POST", f"/session/{session_id}/url", {"url": TARGET})
    verify_image_decode(session_id)
    for requested_width, requested_height in VIEWPORTS:
        set_viewport(session_id, requested_width, requested_height)
        time.sleep(0.15)
        current = state(session_id)
        width = int(current.get("width", 0))
        height = int(current.get("height", 0))
        require(abs(width-requested_width)<=1 and abs(height-requested_height)<=1, f"Unexpected Firefox viewport at {requested_width}px: {current}")
        require(current.get("ready") == "complete" and current.get("url") == TARGET, f"Firefox publication navigation/load drift at {width}px: {current}")
        require(current.get("title") == "GoreeCloud Firefox Extensions" and current.get("canonical") == CANONICAL, f"Firefox identity/canonical drift at {width}px: {current}")
        require(current.get("glaze") == GLAZE_VERSION and current.get("revision") == GLAZE_REVISION, f"Firefox Glaze publication drift at {width}px: {current}")
        require(current.get("schema") == "2", f"Firefox extension inventory schema drift at {width}px: {current}")
        require(int(current.get("scrollWidth", width+10)) <= width+1 and int(current.get("bodyScrollWidth", width+10)) <= width+1, f"Firefox publication overflows horizontally at {width}px: {current}")
        require(int(current.get("cards", 0)) == 5 and int(current.get("stableCards", 0)) == 2, f"Firefox inventory/state count drift at {width}px: {current}")
        image_failures = [
            item for item in current.get("imageBoxes") or []
            if not item.get("complete")
            or float(item.get("width", 0)) <= 0
            or float(item.get("height", 0)) <= 0
            or item.get("display") == "none"
            or item.get("visibility") == "hidden"
        ]
        require(not image_failures, f"Firefox publication contains non-rendered image elements at {width}px: {image_failures}")
        require(not (current.get("unnamedInteractive") or []), f"Firefox publication contains unnamed interactive controls at {width}px: {current}")
        require(int(current.get("mainCount", 0)) == 1 and int(current.get("primaryNavCount", 0)) == 1 and int(current.get("h1Count", 0)) == 1, f"Firefox semantic structure drift at {width}px: {current}")
        require(current.get("skipLinkExists") is True, f"Firefox skip link is missing at {width}px: {current}")
        require(float(current.get("minButtonHeight", 0)) >= 47.5, f"Firefox primary action target below 48px at {width}px: {current}")
        for item in current.get("geometry") or []:
            require(float(item.get("left", -999)) >= -1 and float(item.get("right", 99999)) <= width+1, f"Firefox layout region escapes viewport at {width}px: {item}")
        if width <= 640:
            require(float(current.get("minNavHeight", 0)) >= 47.5, f"Firefox mobile navigation target below 48px at {width}px: {current}")
            require(int(current.get("cardColumns", 0)) == 1 and int(current.get("principleColumns", 0)) == 1, f"Firefox mobile layout did not collapse to one column at {width}px: {current}")
        elif width <= 900:
            require(int(current.get("cardColumns", 0)) == 2 and int(current.get("principleColumns", 0)) == 2, f"Firefox medium layout should use two columns at {width}px: {current}")
        verify_skip_link(session_id, width, height)
    verify_accessibility_tree(session_id)
    verify_theme(session_id)


def main() -> int:
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="goreecloud-firefox-unified-chromedriver-", suffix=".log", delete=False) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen(
                [chromedriver(), f"--port={DRIVER_PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        wait_for_driver()
        session_id = create_session()
        exercise(session_id)
        print(
            f"Unified Firefox Chrome acceptance passed for {TARGET} at 1180×900, 768×900, 390×844, "
            "and 320×844 with decoded-image, semantic, and accessibility checks."
        )
        return 0
    except Exception as error:
        print(f"Unified Firefox Chrome acceptance failed for {TARGET}: {error}")
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
                request("DELETE", f"/session/{session_id}")
            except Exception:
                pass
        if driver:
            driver.terminate()
            try:
                driver.wait(timeout=5)
            except subprocess.TimeoutExpired:
                driver.kill()
                driver.wait(timeout=5)
        if log_path:
            try:
                log_path.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
