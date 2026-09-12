#!/usr/bin/env python3
"""Exercise the built GoreeCloud Manager public site at production-relevant viewport widths."""

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
WEB_PORT = 8768
DRIVER_HOST = "127.0.0.1"
DRIVER_PORT = 9521
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
    request = Request(
        f"{DRIVER_BASE}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urlopen(request, timeout=25) as response:
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
    raise BrowserError(f"local Manager public-site server did not become ready: {last}")


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
        driver_request(
            "POST",
            f"/session/{session_id}/window/rect",
            {"width": requested_width, "height": height, "x": 0, "y": 0},
        )
        state = execute(
            session_id,
            r"""
            const q=s=>document.querySelector(s);
            const columns=s=>{
              const el=q(s); if(!el) return 0;
              return getComputedStyle(el).gridTemplateColumns.trim().split(/\s+/).filter(track=>parseFloat(track)>1).length;
            };
            const rects=s=>[...document.querySelectorAll(s)].map(node=>node.getBoundingClientRect()).filter(r=>r.width>0&&r.height>0);
            const actions=rects('.actions .glaze-button');
            const actionContainer=q('.actions')?.getBoundingClientRect();
            const managerVisual=q('.manager-visual')?.getBoundingClientRect();
            const nav=rects('.header-row nav a');
            const theme=rects('.theme-group button');
            const overflowers=[...document.querySelectorAll('body *')].map(node=>{
              const r=node.getBoundingClientRect();
              return {
                tag:node.tagName.toLowerCase(),
                id:node.id||'',
                className:typeof node.className==='string'?node.className.slice(0,120):'',
                left:Math.round(r.left*100)/100,
                right:Math.round(r.right*100)/100,
                width:Math.round(r.width*100)/100,
                text:(node.textContent||'').trim().replace(/\s+/g,' ').slice(0,120),
              };
            }).filter(item=>item.width>0&&(item.left<-1||item.right>window.innerWidth+1)).slice(0,24);
            return {
              ready:document.readyState,
              width:window.innerWidth,
              scrollWidth:document.documentElement.scrollWidth,
              headerPosition:getComputedStyle(q('.site-header')).position,
              capColumns:columns('.cap-grid'),
              principleColumns:columns('.principle-grid'),
              statusColumns:columns('.status-grid'),
              minNavHeight:nav.length?Math.min(...nav.map(r=>r.height)):0,
              minThemeHeight:theme.length?Math.min(...theme.map(r=>r.height)):0,
              minThemeWidth:theme.length?Math.min(...theme.map(r=>r.width)):0,
              managerVisualRight:managerVisual?.right||0,
              managerVisualLeft:managerVisual?.left||0,
              actions:actions.map(r=>({width:r.width})),
              actionContainerWidth:actionContainer?.width||0,
              overflowers,
              images:[...document.images].map(image=>({complete:image.complete,naturalWidth:image.naturalWidth,naturalHeight:image.naturalHeight,src:image.src})),
            };
            """,
        )
        require(isinstance(state, dict), f"Manager public-site layout state unreadable at {requested_width}px: {state!r}")
        width = int(state.get("width", requested_width))
        require(state.get("ready") == "complete", f"Manager public site did not finish loading at {width}px: {state}")
        require(
            int(state.get("scrollWidth", width + 2)) <= width + 1,
            f"Manager public site has horizontal overflow at {width}px: {state}",
        )
        require(float(state.get("minNavHeight", 0)) >= 47.5, f"Manager nav target below 48px at {width}px: {state}")
        require(
            float(state.get("minThemeHeight", 0)) >= 47.5 and float(state.get("minThemeWidth", 0)) >= 47.5,
            f"Manager appearance control below 48px at {width}px: {state}",
        )
        require(
            float(state.get("managerVisualLeft", 0)) >= -1
            and float(state.get("managerVisualRight", width + 1)) <= width + 1,
            f"Manager conceptual visibility panel escapes viewport at {width}px: {state}",
        )

        expected_cap = 2 if width > 720 else 1
        expected_principle = 3 if width > 980 else (2 if width > 720 else 1)
        expected_status = 2 if width > 720 else 1
        require(
            int(state.get("capColumns", 0)) == expected_cap,
            f"Manager capability grid is not {expected_cap} columns at {width}px: {state}",
        )
        require(
            int(state.get("principleColumns", 0)) == expected_principle,
            f"Manager authority grid is not {expected_principle} columns at {width}px: {state}",
        )
        require(
            int(state.get("statusColumns", 0)) == expected_status,
            f"Manager readiness grid is not {expected_status} columns at {width}px: {state}",
        )
        expected_header = "sticky" if width > 720 else "relative"
        require(
            state.get("headerPosition") == expected_header,
            f"Manager header position is not {expected_header} at {width}px: {state}",
        )

        if width <= 480:
            actions = state.get("actions") or []
            container_width = float(state.get("actionContainerWidth", 0))
            require(bool(actions) and container_width > 0, f"Manager hero actions missing at {width}px")
            require(
                all(float(action.get("width", 0)) >= container_width * 0.98 for action in actions),
                f"Manager hero actions are not full-width at {width}px: {state}",
            )

        images = state.get("images") or []
        failed = [
            image.get("src")
            for image in images
            if not image.get("complete")
            or int(image.get("naturalWidth", 0)) <= 0
            or int(image.get("naturalHeight", 0)) <= 0
        ]
        require(not failed, f"Manager public site contains failed image loads at {width}px: {failed}")

    theme_state = execute(
        session_id,
        r"""
        const click=choice=>document.querySelector(`[data-theme-choice="${choice}"]`)?.click();
        click('light'); const light=document.documentElement.dataset.theme||'';
        click('dark'); const dark=document.documentElement.dataset.theme||'';
        click('system'); const system=document.documentElement.getAttribute('data-theme');
        const selected=[...document.querySelectorAll('[data-theme-choice]')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.dataset.themeChoice);
        return {light,dark,system,selected};
        """,
    )
    require(isinstance(theme_state, dict), f"Manager appearance state unreadable: {theme_state!r}")
    require(
        theme_state.get("light") == "light" and theme_state.get("dark") == "dark",
        f"Manager Light/Dark controls failed: {theme_state}",
    )
    require(
        theme_state.get("system") is None and theme_state.get("selected") == ["system"],
        f"Manager System appearance reset failed: {theme_state}",
    )


def main() -> int:
    require(DIST.is_dir() and (DIST / "index.html").is_file(), "Manager dist/ artifact is missing; run build first")
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
        with tempfile.NamedTemporaryFile(prefix="manager-chromedriver-", suffix=".log", delete=False) as log:
            log_path = log.name
            driver = subprocess.Popen(
                [chromedriver(), f"--port={DRIVER_PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        wait_driver()
        session_id = create_session()
        exercise(session_id)
        print(
            "Manager public-site responsive Chrome smoke passed at 1180, 768, 390, and 320px against the built artifact, including System/Light/Dark controls."
        )
        return 0
    except Exception as error:
        print(f"Manager public-site responsive Chrome smoke failed: {error}")
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
