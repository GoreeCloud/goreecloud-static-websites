#!/usr/bin/env python3
"""Exercise the exact built GoreeCloud Design Center artifact in headless Chrome."""

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
WEB_PORT = 8774
TARGET = f"http://{WEB_HOST}:{WEB_PORT}/"
DRIVER_HOST = "127.0.0.1"
DRIVER_PORT = 9520
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
    for candidate in (
        shutil.which("chromedriver"),
        "/usr/local/share/chromedriver-linux64/chromedriver",
    ):
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
    raise BrowserError(f"local Design Center artifact server did not become ready: {last}")


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
        {
            "cmd": "Emulation.setDeviceMetricsOverride",
            "params": {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1,
                "mobile": False,
            },
        },
    )
    execute(session_id, "window.scrollTo(0,0); return {width:window.innerWidth,height:window.innerHeight};")


def overflow_offenders(session_id: str) -> Any:
    return execute(
        session_id,
        """
        const width=window.innerWidth;
        return [...document.querySelectorAll('body *')]
          .map(el=>{const r=el.getBoundingClientRect(); const s=getComputedStyle(el); return {tag:el.tagName.toLowerCase(),className:el.className||'',id:el.id||'',left:r.left,right:r.right,width:r.width,display:s.display,position:s.position,text:(el.textContent||'').trim().slice(0,100)};})
          .filter(x=>x.display!=='none'&&x.width>0&&(x.left < -1 || x.right > width + 1))
          .slice(0,20);
        """,
    )


def layout_state(session_id: str) -> dict[str, Any]:
    state = execute(
        session_id,
        """
        const q=s=>document.querySelector(s);
        const rect=s=>{const el=q(s);if(!el)return null;const r=el.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height};};
        const visible=el=>{const s=getComputedStyle(el);const r=el.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;};
        const nav=[...document.querySelectorAll('.site-header nav a')].filter(visible);
        const themes=[...document.querySelectorAll('.theme-group button')].filter(visible);
        const images=[...document.images];
        const columns=s=>{const el=q(s);if(!el)return 0;return getComputedStyle(el).gridTemplateColumns.split(/\s+/).filter(Boolean).length;};
        const containers=['.site-header .shell','.hero','.release-band','.principle-grid','.surface-grid','.demo-grid','.adoption','footer .shell']
          .map(selector=>({selector,rect:rect(selector)}));
        return {
          ready:document.readyState,
          title:document.title,
          width:window.innerWidth,
          height:window.innerHeight,
          scrollWidth:document.documentElement.scrollWidth,
          bodyScrollWidth:document.body.scrollWidth,
          glaze:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',
          revision:document.querySelector('meta[name="goreecloud-glaze-source-revision"]')?.content||'',
          consumerState:document.querySelector('meta[name="goreecloud-glaze-consumer-state"]')?.content||'',
          header:rect('.site-header'),
          nav:rect('.site-header nav'),
          theme:rect('.theme-group'),
          minNavHeight:nav.length?Math.min(...nav.map(el=>el.getBoundingClientRect().height)):0,
          minThemeHeight:themes.length?Math.min(...themes.map(el=>el.getBoundingClientRect().height)):0,
          brokenImages:images.filter(img=>!img.complete||img.naturalWidth<=0).map(img=>img.getAttribute('src')),
          principleColumns:columns('.principle-grid'),
          surfaceColumns:columns('.surface-grid'),
          demoColumns:columns('.demo-grid'),
          containers,
        };
        """,
    )
    require(isinstance(state, dict), f"Could not read Design Center responsive state: {state!r}")
    return state


def validate_theme_controls(session_id: str) -> None:
    state = execute(
        session_id,
        """
        const click=choice=>{const b=document.querySelector(`[data-theme-choice="${choice}"]`);if(!b)throw new Error(`missing ${choice} theme button`);b.click();return {choice,theme:document.documentElement.getAttribute('data-theme'),appearance:document.documentElement.getAttribute('data-glaze-appearance'),pressed:b.getAttribute('aria-pressed'),stored:localStorage.getItem('glaze-ui-site-theme')};};
        const light=click('light');
        const dark=click('dark');
        const system=click('system');
        return {light,dark,system};
        """,
    )
    require(isinstance(state, dict), f"Could not exercise Design Center theme controls: {state!r}")
    light = state.get("light") or {}
    dark = state.get("dark") or {}
    system = state.get("system") or {}
    require(light.get("theme") == "light" and light.get("appearance") == "light" and light.get("pressed") == "true", f"Light appearance control failed: {state}")
    require(dark.get("theme") == "dark" and dark.get("appearance") == "dark" and dark.get("pressed") == "true", f"Dark appearance control failed: {state}")
    require(system.get("theme") is None and system.get("appearance") is None and system.get("pressed") == "true", f"System appearance control failed: {state}")
    require(system.get("stored") == "system", f"System appearance choice was not persisted: {state}")


def exercise(session_id: str) -> None:
    request("POST", f"/session/{session_id}/timeouts", {"implicit": 0, "pageLoad": 15000, "script": 10000})
    request("POST", f"/session/{session_id}/url", {"url": TARGET})

    for requested_width, requested_height in VIEWPORTS:
        set_viewport(session_id, requested_width, requested_height)
        state = layout_state(session_id)
        width = int(state.get("width", 0))
        height = int(state.get("height", 0))
        require(abs(width - requested_width) <= 1 and abs(height - requested_height) <= 1, f"Unexpected Design Center CSS viewport at {requested_width}px: {state}")
        require(state.get("ready") == "complete", f"Design Center did not finish loading at {width}px: {state}")
        require(state.get("title") == "GoreeCloud Design Center — GLAZE UI V1.3", f"Unexpected Design Center title at {width}px: {state}")
        require(state.get("glaze") == "1.3.0", f"Design Center Glaze version drift at {width}px: {state}")
        require(state.get("revision") == "8354308445da9ac35ced2b37a7f503a08a0aaf72", f"Design Center Glaze revision drift at {width}px: {state}")
        require(state.get("consumerState") == "source-migrated-rendered-acceptance-pending", f"Design Center consumer-state boundary drift at {width}px: {state}")
        require(int(state.get("scrollWidth", width + 10)) <= width + 1, f"Design Center horizontal overflow at {width}px: {state}; offenders={overflow_offenders(session_id)}")
        require(int(state.get("bodyScrollWidth", width + 10)) <= width + 1, f"Design Center body overflow at {width}px: {state}; offenders={overflow_offenders(session_id)}")
        require(not (state.get("brokenImages") or []), f"Design Center contains broken images at {width}px: {state}")
        require(float(state.get("minNavHeight", 0)) >= 47.5, f"Design Center nav target below 48px at {width}px: {state}")
        require(float(state.get("minThemeHeight", 0)) >= 47.5, f"Design Center appearance target below 48px at {width}px: {state}")
        for item in state.get("containers") or []:
            r = item.get("rect") or {}
            require(float(r.get("left", -999)) >= -1 and float(r.get("right", 99999)) <= width + 1, f"Design Center container {item.get('selector')} escapes viewport at {width}px: {state}")
        if width <= 620:
            for key in ("principleColumns", "surfaceColumns", "demoColumns"):
                require(int(state.get(key, 0)) == 1, f"Design Center {key} did not collapse to one column at {width}px: {state}")
        elif width <= 900:
            for key in ("principleColumns", "surfaceColumns", "demoColumns"):
                require(int(state.get(key, 0)) == 2, f"Design Center {key} did not use the medium two-column layout at {width}px: {state}")

    validate_theme_controls(session_id)


def main() -> int:
    require(DIST.is_dir() and (DIST / "index.html").is_file(), "Design Center dist/ is missing; run validate.py first")
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
        with tempfile.NamedTemporaryFile(prefix="goreecloud-design-chromedriver-", suffix=".log", delete=False) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen(
                [chromedriver(), f"--port={DRIVER_PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        wait_for_driver()
        session_id = create_session()
        exercise(session_id)
        print("Design Center built-artifact Chrome acceptance passed at 1180×900, 768×900, 390×844, and 320×844 with V1.3 appearance controls.")
        return 0
    except Exception as error:
        print(f"Design Center built-artifact Chrome acceptance failed: {error}")
        if log_path:
            try:
                text = log_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            if text:
                print(text[-8_000:])
        return 1
    finally:
        if session_id:
            try:
                request("DELETE", f"/session/{session_id}")
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
