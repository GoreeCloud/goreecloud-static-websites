#!/usr/bin/env python3
"""Exercise the built Suite site at screenshot-relevant viewport widths."""

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

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
WEB_HOST = "127.0.0.1"
WEB_PORT = 8765
DRIVER_HOST = "127.0.0.1"
DRIVER_PORT = 9518
DRIVER_BASE = f"http://{DRIVER_HOST}:{DRIVER_PORT}"
TARGET = f"http://{WEB_HOST}:{WEB_PORT}/"
VIEWPORTS = ((1180, 900), (768, 900), (390, 844), (320, 844))


class BrowserError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BrowserError(message)


def driver_request(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(
        f"{DRIVER_BASE}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urlopen(req, timeout=25) as response:
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
        raise BrowserError(f"WebDriver {value.get('error')}: {value.get('message', '')}")
    return value


def wait_http(url: str, timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    last: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception as error:
            last = error
        time.sleep(0.1)
    raise BrowserError(f"local Suite server did not become ready: {last}")


def wait_driver(timeout: float = 15) -> None:
    deadline = time.monotonic() + timeout
    last: Exception | None = None
    while time.monotonic() < deadline:
        try:
            status = driver_request("GET", "/status")
            if isinstance(status, dict) and status.get("ready"):
                return
        except Exception as error:
            last = error
        time.sleep(0.2)
    raise BrowserError(f"ChromeDriver did not become ready: {last}")


def chromedriver() -> str:
    for candidate in (shutil.which("chromedriver"), "/usr/local/share/chromedriver-linux64/chromedriver"):
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise BrowserError("chromedriver is unavailable on the runner")


def create_session() -> str:
    value = driver_request(
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
                            "--disable-extensions",
                            "--no-first-run",
                            "--window-size=1180,900",
                        ]
                    },
                }
            }
        },
    )
    require(isinstance(value, dict), f"unexpected Chrome session response: {value!r}")
    session_id = value.get("sessionId")
    require(isinstance(session_id, str) and bool(session_id), "Chrome did not return a session id")
    return session_id


def execute(session_id: str, script: str) -> Any:
    return driver_request("POST", f"/session/{session_id}/execute/sync", {"script": script, "args": []})


def exercise(session_id: str) -> None:
    driver_request("POST", f"/session/{session_id}/timeouts", {"implicit": 0, "pageLoad": 15000, "script": 10000})
    driver_request("POST", f"/session/{session_id}/url", {"url": TARGET})

    for requested_width, height in VIEWPORTS:
        driver_request("POST", f"/session/{session_id}/window/rect", {"width": requested_width, "height": height, "x": 0, "y": 0})
        state = execute(
            session_id,
            """
            const q=s=>document.querySelector(s);
            const columns=s=>{
              const el=q(s); if(!el) return 0;
              const tracks=getComputedStyle(el).gridTemplateColumns.trim().split(/\s+/).filter(Boolean);
              return tracks.filter(track=>parseFloat(track)>1).length;
            };
            const header=q('.site-header');
            const headerRect=header?.getBoundingClientRect();
            const hero=q('.hero');
            const heroRect=hero?.getBoundingClientRect();
            const actions=[...document.querySelectorAll('.hero-actions .button')].map(node=>node.getBoundingClientRect());
            const nav=q('.glaze-navigation-capsule');
            const navStyle=nav?getComputedStyle(nav):null;
            const navLinks=[...document.querySelectorAll('.glaze-navigation-capsule a')].map(node=>node.getBoundingClientRect()).filter(r=>r.width>0&&r.height>0);
            return {
              ready:document.readyState,
              width:window.innerWidth,
              scrollWidth:document.documentElement.scrollWidth,
              headerPosition:header?getComputedStyle(header).position:'',
              headerBottom:headerRect?.bottom||0,
              heroTop:heroRect?.top||0,
              cardColumns:columns('.card-grid'),
              principleColumns:columns('.principle-grid'),
              navColumns:navStyle?.display==='grid'?navStyle.gridTemplateColumns.trim().split(/\s+/).filter(track=>parseFloat(track)>1).length:0,
              minNavHeight:navLinks.length?Math.min(...navLinks.map(r=>r.height)):0,
              actions:actions.map(r=>({left:r.left,width:r.width})),
              actionContainerWidth:q('.hero-actions')?.getBoundingClientRect().width||0,
            };
            """,
        )
        require(isinstance(state, dict), f"Suite layout state unreadable at {requested_width}px: {state!r}")
        width = int(state.get("width", requested_width))
        require(state.get("ready") == "complete", f"Suite did not finish loading at {width}px: {state}")
        require(int(state.get("scrollWidth", width + 2)) <= width + 1, f"Suite has horizontal overflow at {width}px: {state}")
        require(state.get("headerPosition") not in {"sticky", "fixed"}, f"Suite header overlays content at {width}px: {state}")
        require(float(state.get("heroTop", 0)) + 1 >= float(state.get("headerBottom", 0)), f"Suite hero overlaps header at {width}px: {state}")
        require(float(state.get("minNavHeight", 0)) >= 47.5, f"Suite nav target below 48px at {width}px: {state}")

        expected_cards = 3 if width > 920 else (2 if width > 680 else 1)
        expected_principles = 3 if width > 920 else (2 if width > 680 else 1)
        require(int(state.get("cardColumns", 0)) == expected_cards, f"Suite card grid is not {expected_cards} columns at {width}px: {state}")
        require(int(state.get("principleColumns", 0)) == expected_principles, f"Suite principle grid is not {expected_principles} columns at {width}px: {state}")

        if width <= 680:
            expected_nav = 1 if width <= 380 else 2
            require(int(state.get("navColumns", 0)) == expected_nav, f"Suite nav is not {expected_nav} columns at {width}px: {state}")
            actions = state.get("actions") or []
            container_width = float(state.get("actionContainerWidth", 0))
            require(bool(actions) and container_width > 0, f"Suite hero actions missing at {width}px")
            require(all(float(action.get("width", 0)) >= container_width * 0.98 for action in actions), f"Suite hero actions are not full-width at {width}px: {state}")


def main() -> int:
    require(DIST.is_dir() and (DIST / "index.html").is_file(), "Suite dist/ artifact is missing; run build first")
    server: subprocess.Popen[bytes] | None = None
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: str | None = None
    try:
        server = subprocess.Popen(
            ["python3", "-m", "http.server", str(WEB_PORT), "--bind", WEB_HOST, "--directory", str(DIST)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        wait_http(TARGET)
        with tempfile.NamedTemporaryFile(prefix="suite-chromedriver-", suffix=".log", delete=False) as log:
            log_path = log.name
            driver = subprocess.Popen([chromedriver(), f"--port={DRIVER_PORT}", "--allowed-ips=127.0.0.1"], stdout=log, stderr=subprocess.STDOUT)
        wait_driver()
        session_id = create_session()
        exercise(session_id)
        print("Suite responsive Chrome smoke passed at 1180, 768, 390, and 320px against the built public artifact.")
        return 0
    except Exception as error:
        print(f"Suite responsive Chrome smoke failed: {error}")
        if log_path:
            try:
                text = Path(log_path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            if text:
                print(text[-8000:])
        return 1
    finally:
        if session_id:
            try:
                driver_request("DELETE", f"/session/{session_id}")
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
                Path(log_path).unlink()
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
