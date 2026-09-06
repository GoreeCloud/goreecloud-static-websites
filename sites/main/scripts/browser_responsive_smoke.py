#!/usr/bin/env python3
"""Exercise the public GoreeCloud homepage at screenshot-relevant CSS viewports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import verify_remote_deployment

HOST = "127.0.0.1"
PORT = 9517
BASE = f"http://{HOST}:{PORT}"
HTTP_TIMEOUT = 25
STARTUP_TIMEOUT = 15
VIEWPORTS = ((1180, 900), (768, 900), (390, 844), (320, 844))


class BrowserError(RuntimeError):
    pass


def request(method: str, path: str, payload: dict[str, Any] | None = None, timeout: int = HTTP_TIMEOUT) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(
        f"{BASE}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urlopen(req, timeout=timeout) as response:
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BrowserError(message)


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


def set_css_viewport(session_id: str, width: int, height: int) -> None:
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
    # Keep each viewport independent: a navigation expansion at 390px must not
    # affect the initial page geometry checked at 320px.
    execute(
        session_id,
        """
        const toggle=document.querySelector('.nav-toggle');
        if(toggle?.getAttribute('aria-expanded')==='true') toggle.click();
        window.scrollTo(0,0);
        return {width:window.innerWidth,height:window.innerHeight};
        """,
    )


def single_column(layout: Any) -> bool:
    if not isinstance(layout, dict) or int(layout.get("count", 0)) < 1:
        return False
    content_width = float(layout.get("contentWidth", 0))
    content_left = float(layout.get("contentLeft", 0))
    children = layout.get("children") or []
    if content_width <= 0 or not children:
        return False
    return all(
        abs(float(child.get("left", 0)) - content_left) <= 2
        and float(child.get("width", 0)) >= content_width * 0.94
        for child in children
    )


def read_state(session_id: str) -> dict[str, Any]:
    state = execute(
        session_id,
        """
        const q=s=>document.querySelector(s);
        const layout=s=>{
          const el=q(s);
          if(!el) return null;
          const rect=el.getBoundingClientRect();
          const style=getComputedStyle(el);
          const paddingLeft=parseFloat(style.paddingLeft)||0;
          const paddingRight=parseFloat(style.paddingRight)||0;
          const children=[...el.children]
            .filter(child=>{
              const childStyle=getComputedStyle(child);
              const r=child.getBoundingClientRect();
              return childStyle.display!=='none' && childStyle.visibility!=='hidden' && r.width>0 && r.height>0;
            })
            .map(child=>{
              const r=child.getBoundingClientRect();
              return {left:r.left,right:r.right,top:r.top,width:r.width,height:r.height};
            });
          return {
            left:rect.left,
            right:rect.right,
            width:rect.width,
            contentLeft:rect.left+paddingLeft,
            contentWidth:Math.max(0,rect.width-paddingLeft-paddingRight),
            count:children.length,
            children,
          };
        };
        const header=q('.site-header');
        const hero=q('#top');
        const headerRect=header?.getBoundingClientRect();
        const heroRect=hero?.getBoundingClientRect();
        return {
          ready:document.readyState,
          width:window.innerWidth,
          height:window.innerHeight,
          scrollWidth:document.documentElement.scrollWidth,
          headerPosition:header?getComputedStyle(header).position:'',
          headerBottom:headerRect?.bottom||0,
          heroTop:heroRect?.top||0,
          heroFont:parseFloat(getComputedStyle(q('.hero h1')).fontSize),
          websiteLayout:layout('.website-grid'),
          howLayout:layout('.how-flow'),
          roadmapLayout:layout('.roadmap-grid'),
          socialLayout:layout('.social-grid'),
          statLayout:layout('.repository-teaser-stats'),
        };
        """,
    )
    require(isinstance(state, dict), f"Could not read homepage responsive state: {state!r}")
    return state


def validate_navigation(session_id: str, width: int, height: int) -> None:
    nav_state = execute(
        session_id,
        """
        const toggle=document.querySelector('.nav-toggle');
        if(toggle && toggle.getAttribute('aria-expanded')!=='true') toggle.click();
        const nav=document.querySelector('.site-nav');
        const style=nav?getComputedStyle(nav):null;
        const rect=nav?.getBoundingClientRect();
        const linkRects=[...document.querySelectorAll('.site-nav a')]
          .map(a=>a.getBoundingClientRect()).filter(r=>r.width>0&&r.height>0);
        const columns=(style?.gridTemplateColumns||'').split(/\s+/).filter(Boolean);
        return {
          position:style?.position||'',
          left:rect?.left||0,
          right:rect?.right||0,
          top:rect?.top||0,
          bottom:rect?.bottom||0,
          width:rect?.width||0,
          height:rect?.height||0,
          columnCount:columns.length,
          minLinkHeight:linkRects.length?Math.min(...linkRects.map(r=>r.height)):0,
          expanded:toggle?.getAttribute('aria-expanded')||'',
          overflowY:style?.overflowY||'',
        };
        """,
    )
    require(isinstance(nav_state, dict), f"Could not read mobile navigation at {width}px")
    require(nav_state.get("position") == "absolute", f"Mobile navigation is not a bounded popover at {width}px: {nav_state}")
    require(nav_state.get("expanded") == "true", f"Mobile navigation did not expand at {width}px: {nav_state}")
    require(int(nav_state.get("columnCount", 0)) == 2, f"Mobile navigation did not retain the compact two-column layout at {width}px: {nav_state}")
    require(float(nav_state.get("minLinkHeight", 0)) >= 47.5, f"Mobile navigation target below 48px at {width}px: {nav_state}")
    require(float(nav_state.get("left", -1)) >= -1 and float(nav_state.get("right", width + 2)) <= width + 1, f"Mobile navigation overflows viewport horizontally at {width}px: {nav_state}")
    require(float(nav_state.get("top", -1)) >= -1 and float(nav_state.get("bottom", height + 2)) <= height + 1, f"Mobile navigation exceeds the visible viewport at {width}px: {nav_state}")
    require(float(nav_state.get("width", width + 10)) <= min(321.0, width - 18.0), f"Mobile navigation is not compactly width-bounded at {width}px: {nav_state}")
    require(nav_state.get("overflowY") in {"auto", "scroll"}, f"Mobile navigation does not contain vertical overflow at {width}px: {nav_state}")


def exercise(session_id: str, url: str) -> None:
    request("POST", f"/session/{session_id}/timeouts", {"implicit": 0, "pageLoad": 15000, "script": 10000})
    request("POST", f"/session/{session_id}/url", {"url": url})

    for requested_width, requested_height in VIEWPORTS:
        set_css_viewport(session_id, requested_width, requested_height)
        state = read_state(session_id)
        width = int(state.get("width", 0))
        height = int(state.get("height", 0))
        require(abs(width - requested_width) <= 1, f"Chrome CSS viewport is {width}px; expected {requested_width}px: {state}")
        require(abs(height - requested_height) <= 1, f"Chrome CSS viewport height is {height}px; expected {requested_height}px: {state}")
        require(state.get("ready") == "complete", f"Homepage did not finish loading at {width}px: {state}")
        require(int(state.get("scrollWidth", width + 10)) <= width + 1, f"Horizontal overflow at {width}px: {state}")
        require(state.get("headerPosition") not in {"fixed", "sticky"}, f"Public header overlays content at {width}px: {state}")
        require(float(state.get("heroTop", 0)) + 1 >= float(state.get("headerBottom", 0)), f"Hero begins beneath an overlapping header at {width}px: {state}")
        require(float(state.get("heroFont", 0)) >= 40, f"Hero type became too small at {width}px: {state}")

        if width <= 820:
            require(single_column(state.get("websiteLayout")), f"Website directory did not render as one full-width content column at {width}px: {state}")
        if width <= 600:
            for key in ("howLayout", "roadmapLayout", "socialLayout", "statLayout"):
                require(single_column(state.get(key)), f"{key} did not render as one full-width content column at {width}px: {state}")
        if width <= 390:
            validate_navigation(session_id, width, height)


def run(target: str) -> int:
    url = verify_remote_deployment.target_url(target)
    process: subprocess.Popen[bytes] | None = None
    log_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="goreecloud-main-chromedriver-", suffix=".log", delete=False) as log_file:
            log_path = log_file.name
            process = subprocess.Popen(
                [chromedriver(), f"--port={PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        wait_for_driver()
        last_error: Exception | None = None
        for attempt in range(2):
            session_id: str | None = None
            try:
                session_id = create_session()
                exercise(session_id, url)
                print(f"Main responsive Chrome smoke passed for {target}: {url}")
                return 0
            except Exception as error:
                last_error = error
                if attempt == 0:
                    print(f"Chrome session failed before responsive acceptance; retrying with a fresh session: {error}")
            finally:
                if session_id:
                    try:
                        request("DELETE", f"/session/{session_id}")
                    except Exception:
                        pass
        raise BrowserError(str(last_error))
    except Exception as error:
        print(f"Main responsive Chrome smoke failed for {target}: {url}")
        print(f"- {error}")
        if log_path:
            try:
                text = Path(log_path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            if text:
                print(text[-8000:])
        return 1
    finally:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("branch-preview", "production"), required=True)
    args = parser.parse_args()
    return run(args.target)


if __name__ == "__main__":
    raise SystemExit(main())
