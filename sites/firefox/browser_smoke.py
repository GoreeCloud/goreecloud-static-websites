#!/usr/bin/env python3
"""Exercise the exact built GoreeCloud Firefox Extensions artifact in headless Chrome."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SITE = Path(__file__).resolve().parent
DIST = SITE / "dist"
WEB_HOST = "127.0.0.1"
WEB_PORT = 8776
TARGET = f"http://{WEB_HOST}:{WEB_PORT}/"
DRIVER_HOST = "127.0.0.1"
DRIVER_PORT = 9522
DRIVER_BASE = f"http://{DRIVER_HOST}:{DRIVER_PORT}"
HTTP_TIMEOUT = 20
STARTUP_TIMEOUT = 15
VIEWPORTS = ((1180, 900), (768, 900), (390, 844), (320, 844))


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
        with urlopen(req, timeout=HTTP_TIMEOUT) as response:
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
    deadline = time.monotonic() + STARTUP_TIMEOUT
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


def wait_http() -> None:
    deadline = time.monotonic() + 10
    last: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urlopen(TARGET, timeout=1) as response:
                if response.status == 200:
                    return
        except (URLError, TimeoutError, OSError) as error:
            last = error
        time.sleep(0.1)
    raise BrowserError(f"local Firefox site artifact server did not become ready: {last}")


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
    require(isinstance(session_id, str) and bool(session_id), "Chrome did not return a session id")
    return session_id


def execute(session_id: str, script: str) -> Any:
    return request("POST", f"/session/{session_id}/execute/sync", {"script": script, "args": []})


def set_viewport(session_id: str, width: int, height: int) -> None:
    request(
        "POST",
        f"/session/{session_id}/goog/cdp/execute",
        {"cmd": "Emulation.setDeviceMetricsOverride", "params": {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False}},
    )
    execute(session_id, "window.scrollTo(0,0); return {width:innerWidth,height:innerHeight};")


def state(session_id: str) -> dict[str, Any]:
    value = execute(
        session_id,
        r"""
        const visible=el=>{const s=getComputedStyle(el),r=el.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;};
        const cards=[...document.querySelectorAll('#extensions .card')].filter(visible);
        const nav=[...document.querySelectorAll('.site-header nav a,.site-header nav button')].filter(visible);
        const buttons=[...document.querySelectorAll('.button')].filter(visible);
        const images=[...document.images];
        const geometry=[...document.querySelectorAll('.wrap,.hero-grid,.summary,#extensions .grid,.principles,.callout,.footer')]
          .filter(visible).map(el=>{const r=el.getBoundingClientRect();return {className:el.className,left:r.left,right:r.right,width:r.width};});
        const columns=el=>getComputedStyle(el).gridTemplateColumns.split(/\s+/).filter(Boolean).length;
        return {
          ready:document.readyState,
          title:document.title,
          width:innerWidth,
          height:innerHeight,
          scrollWidth:document.documentElement.scrollWidth,
          glaze:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',
          schema:document.querySelector('meta[name="goreecloud-extension-inventory-schema"]')?.content||'',
          cards:cards.length,
          stableCards:cards.filter(card=>card.querySelector('.status.stable')).length,
          cardColumns:cards.length?columns(document.querySelector('#extensions .grid')):0,
          principleColumns:columns(document.querySelector('.principles')),
          minNavHeight:nav.length?Math.min(...nav.map(el=>el.getBoundingClientRect().height)):0,
          minButtonHeight:buttons.length?Math.min(...buttons.map(el=>el.getBoundingClientRect().height)):0,
          brokenImages:images.filter(img=>!img.complete||img.naturalWidth<=0).map(img=>img.getAttribute('src')),
          geometry,
        };
        """,
    )
    require(isinstance(value, dict), f"Could not read Firefox site browser state: {value!r}")
    return value


def validate_theme(session_id: str) -> None:
    value = execute(
        session_id,
        """
        const b=document.querySelector('#theme-toggle');
        if(!b) return null;
        const before=document.documentElement.getAttribute('data-theme');
        b.click();
        const after=document.documentElement.getAttribute('data-theme');
        const stored=localStorage.getItem('goreecloud-firefox-theme');
        b.click();
        return {before,after,stored,final:document.documentElement.getAttribute('data-theme')};
        """,
    )
    require(isinstance(value, dict), f"Firefox appearance control missing or unreadable: {value!r}")
    require(value.get("after") in {"light", "dark"}, f"Firefox appearance control did not set an explicit theme: {value}")
    require(value.get("stored") == value.get("after"), f"Firefox appearance choice did not persist: {value}")


def exercise(session_id: str) -> None:
    request("POST", f"/session/{session_id}/timeouts", {"implicit": 0, "pageLoad": 15000, "script": 10000})
    request("POST", f"/session/{session_id}/url", {"url": TARGET})
    for requested_width, requested_height in VIEWPORTS:
        set_viewport(session_id, requested_width, requested_height)
        current = state(session_id)
        width = int(current.get("width", 0))
        height = int(current.get("height", 0))
        require(abs(width-requested_width)<=1 and abs(height-requested_height)<=1, f"Unexpected Firefox CSS viewport at {requested_width}px: {current}")
        require(current.get("ready") == "complete", f"Firefox site did not finish loading at {width}px: {current}")
        require(current.get("title") == "GoreeCloud Firefox Extensions", f"Firefox page title drift at {width}px: {current}")
        require(current.get("glaze") == "1.3.0" and current.get("schema") == "2", f"Firefox authority metadata drift at {width}px: {current}")
        require(int(current.get("scrollWidth", width+10)) <= width+1, f"Firefox site horizontal overflow at {width}px: {current}")
        require(int(current.get("cards", 0)) == 5, f"Firefox inventory did not render five extension cards at {width}px: {current}")
        require(int(current.get("stableCards", 0)) == 2, f"Firefox UI Stable source-state count drift at {width}px: {current}")
        require(not (current.get("brokenImages") or []), f"Firefox site contains broken images at {width}px: {current}")
        require(float(current.get("minButtonHeight", 0)) >= 47.5, f"Firefox primary action target below 48px at {width}px: {current}")
        for item in current.get("geometry") or []:
            require(float(item.get("left", -999)) >= -1 and float(item.get("right", 99999)) <= width+1, f"Firefox layout region escapes viewport at {width}px: {item}")
        if width <= 640:
            require(int(current.get("cardColumns", 0)) == 1 and int(current.get("principleColumns", 0)) == 1, f"Firefox mobile content did not collapse to one column at {width}px: {current}")
            require(float(current.get("minNavHeight", 0)) >= 47.5, f"Firefox mobile nav target below 48px at {width}px: {current}")
        elif width <= 900:
            require(int(current.get("cardColumns", 0)) == 2 and int(current.get("principleColumns", 0)) == 2, f"Firefox medium layout should use two columns at {width}px: {current}")
    validate_theme(session_id)


def main() -> int:
    require(DIST.is_dir() and (DIST / "index.html").is_file(), "Firefox dist/ is missing; run validate.py first")
    server: subprocess.Popen[bytes] | None = None
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: Path | None = None
    try:
        server = subprocess.Popen(["python3", "-m", "http.server", str(WEB_PORT), "--bind", WEB_HOST, "--directory", str(DIST)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wait_http()
        with tempfile.NamedTemporaryFile(prefix="goreecloud-firefox-chromedriver-", suffix=".log", delete=False) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen([chromedriver(), f"--port={DRIVER_PORT}", "--allowed-ips=127.0.0.1"], stdout=log_file, stderr=subprocess.STDOUT)
        wait_for_driver()
        session_id = create_session()
        exercise(session_id)
        print("Firefox Extensions built-artifact Chrome acceptance passed at 1180×900, 768×900, 390×844, and 320×844.")
        return 0
    except Exception as error:
        print(f"Firefox Extensions built-artifact Chrome acceptance failed: {error}")
        if log_path:
            try:
                text=log_path.read_text(encoding="utf-8",errors="replace")
            except OSError:
                text=""
            if text:
                print(text[-8000:])
        return 1
    finally:
        if session_id:
            try: request("DELETE", f"/session/{session_id}")
            except Exception: pass
        for process in (driver,server):
            if process:
                process.terminate()
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=5)
        if log_path:
            try: log_path.unlink()
            except OSError: pass


if __name__ == "__main__":
    raise SystemExit(main())
