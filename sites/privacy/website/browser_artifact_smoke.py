#!/usr/bin/env python3
"""Exercise the exact built Privacy Center artifact in headless Chrome.

This is an automated browser-artifact smoke gate. It does not substitute for human
visual review, assistive-technology/device qualification, performance acceptance,
deployment verification, Privacy Shield runtime acceptance, or production approval.
"""

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
EXPECTED_REVISION = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
EXPECTED_STATE = "source-migrated-rendered-acceptance-pending"


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
    raise BrowserError(f"local Privacy Center artifact server did not become ready: {last}")


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


def navigate(session_id: str, url: str) -> None:
    request("POST", f"/session/{session_id}/url", {"url": url})


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
          .map(el=>{const r=el.getBoundingClientRect();const s=getComputedStyle(el);return {tag:el.tagName.toLowerCase(),className:el.className||'',id:el.id||'',left:r.left,right:r.right,width:r.width,display:s.display,position:s.position,text:(el.textContent||'').trim().slice(0,100)};})
          .filter(x=>x.display!=='none'&&x.position!=='fixed'&&x.width>0&&(x.left < -1 || x.right > width + 1))
          .slice(0,20);
        """,
    )


def layout_state(session_id: str) -> dict[str, Any]:
    state = execute(
        session_id,
        """
        const q=s=>document.querySelector(s);
        const visible=el=>{const s=getComputedStyle(el);const r=el.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;};
        const columns=s=>{const el=q(s);if(!el)return 0;return getComputedStyle(el).gridTemplateColumns.split(/\s+/).filter(Boolean).length;};
        const nav=[...document.querySelectorAll('.nav-wrap nav a')].filter(visible);
        const controls=[...document.querySelectorAll('.site-header a,.site-header button')].filter(visible);
        const images=[...document.images];
        return {
          ready:document.readyState,
          title:document.title,
          width:window.innerWidth,
          height:window.innerHeight,
          scrollWidth:document.documentElement.scrollWidth,
          bodyScrollWidth:document.body.scrollWidth,
          glaze:q('meta[name="goreecloud-glaze-ui"]')?.content||'',
          revision:q('meta[name="goreecloud-glaze-source-revision"]')?.content||'',
          consumerState:q('meta[name="goreecloud-glaze-consumer-state"]')?.content||'',
          main:!!q('main#main'),
          h1:(q('h1')?.textContent||'').trim(),
          navLabels:nav.map(el=>(el.textContent||'').trim()),
          minControlHeight:controls.length?Math.min(...controls.map(el=>el.getBoundingClientRect().height)):0,
          brokenImages:images.filter(img=>!img.complete||img.naturalWidth<=0).map(img=>img.getAttribute('src')),
          cardColumns:columns('.card-grid'),
          splitColumns:columns('.split'),
          principleColumns:columns('.principle-list'),
          meshNoteCount:document.querySelectorAll('[data-mesh-privacy-note]').length,
          privacyPending:[...document.querySelectorAll('#status .pending')].length,
        };
        """,
    )
    require(isinstance(state, dict), f"Could not read Privacy Center responsive state: {state!r}")
    return state


def validate_skip_link(session_id: str) -> None:
    state = execute(
        session_id,
        """
        const link=document.querySelector('.skip-link');
        if(!link)return {missing:true};
        link.focus();
        const r=link.getBoundingClientRect();
        return {active:document.activeElement===link,left:r.left,top:r.top,width:r.width,height:r.height};
        """,
    )
    require(isinstance(state, dict) and not state.get("missing"), f"Privacy Center skip link is missing: {state}")
    require(state.get("active") is True, f"Privacy Center skip link did not receive focus: {state}")
    require(float(state.get("left", -9999)) >= 0 and float(state.get("width", 0)) > 0, f"Privacy Center skip link did not become visible on focus: {state}")


def validate_theme_cycle(session_id: str) -> None:
    state = execute(
        session_id,
        """
        localStorage.removeItem('goreecloud-privacy-site-appearance');
        const button=document.querySelector('[data-theme-toggle]');
        if(!button)return {missing:true};
        const snap=()=>({text:button.textContent,theme:document.documentElement.getAttribute('data-theme'),appearance:document.documentElement.getAttribute('data-glaze-appearance'),stored:localStorage.getItem('goreecloud-privacy-site-appearance'),label:button.getAttribute('aria-label')});
        const states=[snap()];
        for(let i=0;i<4;i++){button.click();states.push(snap());}
        return {states};
        """,
    )
    require(isinstance(state, dict) and not state.get("missing"), f"Privacy Center appearance control is missing: {state}")
    states = state.get("states") or []
    require(len(states) == 5, f"Privacy Center appearance cycle did not produce five states: {state}")
    expected = (
        ("System", None, None, None),
        ("Light", "light", "light", "light"),
        ("Dark", "dark", "dark", "dark"),
        ("Deep Dark", "dark", "deep-dark", "deep-dark"),
        ("System", None, None, "system"),
    )
    for observed, wanted in zip(states, expected, strict=True):
        text, theme, appearance, stored = wanted
        require(observed.get("text") == text, f"Privacy Center appearance label drift: {state}")
        require(observed.get("theme") == theme and observed.get("appearance") == appearance, f"Privacy Center appearance state drift: {state}")
        require(observed.get("stored") == stored, f"Privacy Center appearance persistence drift: {state}")
        require("Appearance:" in (observed.get("label") or ""), f"Privacy Center appearance control lacks descriptive aria-label: {state}")


def validate_navigation(session_id: str) -> None:
    state = execute(
        session_id,
        """
        const link=document.querySelector('nav a[href="#authorization"]');
        if(!link)return {missing:true};
        link.click();
        return {current:link.getAttribute('aria-current'),hash:location.hash,target:!!document.querySelector('#authorization')};
        """,
    )
    require(isinstance(state, dict) and not state.get("missing"), f"Privacy Center authorization navigation link is missing: {state}")
    require(state.get("target") is True and state.get("current") == "true" and state.get("hash") == "#authorization", f"Privacy Center navigation state did not follow the selected section: {state}")


def validate_404(session_id: str) -> None:
    navigate(session_id, f"{TARGET}404.html")
    state = execute(
        session_id,
        """
        const q=s=>document.querySelector(s);
        return {
          ready:document.readyState,
          title:document.title,
          glaze:q('meta[name="goreecloud-glaze-ui"]')?.content||'',
          revision:q('meta[name="goreecloud-glaze-source-revision"]')?.content||'',
          consumerState:q('meta[name="goreecloud-glaze-consumer-state"]')?.content||'',
          heading:(q('h1')?.textContent||'').trim(),
          backHref:q('a.glaze-button')?.getAttribute('href')||'',
          imageCount:document.images.length,
        };
        """,
    )
    require(isinstance(state, dict), f"Could not read Privacy Center 404 state: {state!r}")
    require(state.get("ready") == "complete", f"Privacy Center 404 did not finish loading: {state}")
    require(state.get("title") == "Not found — GoreeCloud Privacy Center", f"Privacy Center 404 title drift: {state}")
    require(state.get("glaze") == "1.3.0" and state.get("revision") == EXPECTED_REVISION, f"Privacy Center 404 Glaze provenance drift: {state}")
    require(state.get("consumerState") == EXPECTED_STATE, f"Privacy Center 404 consumer-state boundary drift: {state}")
    require(state.get("heading") == "That Privacy Center path does not exist.", f"Privacy Center 404 heading drift: {state}")
    require(state.get("backHref") == "/", f"Privacy Center 404 return target drift: {state}")


def exercise(session_id: str) -> None:
    request("POST", f"/session/{session_id}/timeouts", {"implicit": 0, "pageLoad": 15000, "script": 10000})
    navigate(session_id, TARGET)

    for requested_width, requested_height in VIEWPORTS:
        set_viewport(session_id, requested_width, requested_height)
        state = layout_state(session_id)
        width = int(state.get("width", 0))
        height = int(state.get("height", 0))
        require(abs(width - requested_width) <= 1 and abs(height - requested_height) <= 1, f"Unexpected Privacy Center CSS viewport at {requested_width}px: {state}")
        require(state.get("ready") == "complete", f"Privacy Center did not finish loading at {width}px: {state}")
        require(state.get("title") == "GoreeCloud Privacy Center — Privacy Shield", f"Unexpected Privacy Center title at {width}px: {state}")
        require(state.get("glaze") == "1.3.0", f"Privacy Center Glaze version drift at {width}px: {state}")
        require(state.get("revision") == EXPECTED_REVISION, f"Privacy Center Glaze revision drift at {width}px: {state}")
        require(state.get("consumerState") == EXPECTED_STATE, f"Privacy Center consumer-state boundary drift at {width}px: {state}")
        require(state.get("main") is True and bool(state.get("h1")), f"Privacy Center primary content landmarks are incomplete at {width}px: {state}")
        require(state.get("navLabels") == ["Role", "Authorization", "Boundaries", "Status"], f"Privacy Center navigation drift at {width}px: {state}")
        require(int(state.get("scrollWidth", width + 10)) <= width + 1, f"Privacy Center horizontal overflow at {width}px: {state}; offenders={overflow_offenders(session_id)}")
        require(int(state.get("bodyScrollWidth", width + 10)) <= width + 1, f"Privacy Center body overflow at {width}px: {state}; offenders={overflow_offenders(session_id)}")
        require(not (state.get("brokenImages") or []), f"Privacy Center contains broken images at {width}px: {state}")
        require(float(state.get("minControlHeight", 0)) >= 47.5, f"Privacy Center header target below 48px at {width}px: {state}")
        require(int(state.get("meshNoteCount", 0)) == 1, f"Privacy Center Mesh lifecycle note is missing or duplicated at {width}px: {state}")
        require(int(state.get("privacyPending", 0)) >= 1, f"Privacy Center no longer exposes pending implementation state at {width}px: {state}")

        if width > 850:
            require(int(state.get("cardColumns", 0)) == 3 and int(state.get("splitColumns", 0)) == 3, f"Privacy Center desktop grids drifted at {width}px: {state}")
            require(int(state.get("principleColumns", 0)) == 2, f"Privacy Center desktop principle grid drifted at {width}px: {state}")
        elif width > 620:
            require(int(state.get("cardColumns", 0)) == 2 and int(state.get("splitColumns", 0)) == 2, f"Privacy Center medium grids drifted at {width}px: {state}")
            require(int(state.get("principleColumns", 0)) == 2, f"Privacy Center medium principle grid drifted at {width}px: {state}")
        else:
            for key in ("cardColumns", "splitColumns", "principleColumns"):
                require(int(state.get(key, 0)) == 1, f"Privacy Center {key} did not collapse to one column at {width}px: {state}")

    validate_skip_link(session_id)
    validate_navigation(session_id)
    navigate(session_id, TARGET)
    validate_theme_cycle(session_id)
    validate_404(session_id)


def main() -> int:
    require(DIST.is_dir() and (DIST / "index.html").is_file(), "Privacy Center dist/ is missing; run build.py first")
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
        with tempfile.NamedTemporaryFile(prefix="goreecloud-privacy-chromedriver-", suffix=".log", delete=False) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen(
                [chromedriver(), f"--port={DRIVER_PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        wait_for_driver()
        session_id = create_session()
        exercise(session_id)
        print("Privacy Center automated Chrome artifact smoke passed at 1180×900, 768×900, 390×844, and 320×844; human/device/production acceptance remains separate.")
        return 0
    except Exception as error:
        print(f"Privacy Center automated Chrome artifact smoke failed: {error}")
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
