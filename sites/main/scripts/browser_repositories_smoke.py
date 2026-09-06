#!/usr/bin/env python3
"""Exercise repositories.html on the exact deployed preview at review viewports."""

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
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import verify_remote_deployment

HOST = "127.0.0.1"
PORT = 9519
BASE = f"http://{HOST}:{PORT}"
VIEWPORTS = ((1180, 900), (768, 900), (390, 844), (320, 844))


class BrowserError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BrowserError(message)


def request(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(f"{BASE}{path}", data=body, method=method, headers={"Content-Type": "application/json; charset=utf-8"})
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


def chromedriver() -> str:
    for candidate in (shutil.which("chromedriver"), "/usr/local/share/chromedriver-linux64/chromedriver"):
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise BrowserError("chromedriver is unavailable on the runner")


def wait_driver() -> None:
    deadline = time.monotonic() + 15
    last: Exception | None = None
    while time.monotonic() < deadline:
        try:
            status = request("GET", "/status")
            if isinstance(status, dict) and status.get("ready"):
                return
        except Exception as error:
            last = error
        time.sleep(.2)
    raise BrowserError(f"chromedriver did not become ready: {last}")


def create_session() -> str:
    value = request(
        "POST",
        "/session",
        {"capabilities": {"alwaysMatch": {
            "browserName": "chrome",
            "goog:chromeOptions": {"args": [
                "--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                "--disable-background-networking", "--disable-component-update",
                "--disable-default-apps", "--disable-extensions", "--disable-sync",
                "--metrics-recording-only", "--no-first-run", "--window-size=1180,900",
            ]},
        }}},
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
        {"cmd": "Emulation.setDeviceMetricsOverride", "params": {
            "width": width, "height": height, "deviceScaleFactor": 1, "mobile": False,
        }},
    )
    execute(
        session_id,
        """
        const toggle=document.querySelector('.nav-toggle');
        if(toggle?.getAttribute('aria-expanded')==='true') toggle.click();
        window.scrollTo(0,0); return window.innerWidth;
        """,
    )


def active_tracks(value: str) -> int:
    tracks = []
    for raw in value.split():
        try:
            size = float(raw.removesuffix("px"))
        except ValueError:
            continue
        if size > 1:
            tracks.append(size)
    return len(tracks)


def read_state(session_id: str) -> dict[str, Any]:
    state = execute(
        session_id,
        """
        const q=s=>document.querySelector(s);
        const header=q('.site-header');
        const hero=q('.repo-hero');
        const headerRect=header?.getBoundingClientRect();
        const heroRect=hero?.getBoundingClientRect();
        const grids=[...document.querySelectorAll('.repo-grid')].filter(el=>getComputedStyle(el).display!=='none');
        const gridTracks=grids.map(el=>getComputedStyle(el).gridTemplateColumns);
        const cards=[...document.querySelectorAll('.repo-card')].filter(el=>getComputedStyle(el).display!=='none');
        const heroActions=[...document.querySelectorAll('.repo-hero .hero-actions .button')].map(el=>el.getBoundingClientRect());
        const actionsBox=q('.repo-hero .hero-actions')?.getBoundingClientRect();
        return {
          ready:document.readyState,
          title:document.title,
          width:window.innerWidth,
          scrollWidth:document.documentElement.scrollWidth,
          headerPosition:header?getComputedStyle(header).position:'',
          headerBottom:headerRect?.bottom||0,
          heroTop:heroRect?.top||0,
          heroTracks:getComputedStyle(q('.repo-hero-grid')).gridTemplateColumns,
          gridTracks,
          cards:cards.length,
          filterTracks:getComputedStyle(q('.repo-filter-grid')).gridTemplateColumns,
          visibilityTracks:getComputedStyle(q('.repo-visibility-buttons')).gridTemplateColumns,
          heroActions:heroActions.map(r=>({width:r.width,left:r.left})),
          actionWidth:actionsBox?.width||0,
        };
        """,
    )
    require(isinstance(state, dict), f"Repository page state was not readable: {state!r}")
    return state


def validate_nav(session_id: str, width: int) -> None:
    nav = execute(
        session_id,
        """
        const toggle=document.querySelector('.nav-toggle');
        if(toggle && toggle.getAttribute('aria-expanded')!=='true') toggle.click();
        const el=document.querySelector('.site-nav');
        const style=getComputedStyle(el);
        const rect=el.getBoundingClientRect();
        const links=[...el.querySelectorAll('a')].map(a=>a.getBoundingClientRect()).filter(r=>r.width>0&&r.height>0);
        return {
          expanded:toggle?.getAttribute('aria-expanded')||'',
          position:style.position,
          tracks:style.gridTemplateColumns,
          left:rect.left,
          right:rect.right,
          minHeight:links.length?Math.min(...links.map(r=>r.height)):0,
        };
        """,
    )
    require(isinstance(nav, dict), f"Repository mobile navigation state unreadable at {width}px")
    require(nav.get("expanded") == "true", f"Repository navigation did not expand at {width}px: {nav}")
    require(nav.get("position") == "static", f"Repository navigation is not in document flow at {width}px: {nav}")
    require(float(nav.get("minHeight", 0)) >= 47.5, f"Repository navigation target below 48px at {width}px: {nav}")
    require(float(nav.get("left", -1)) >= -1 and float(nav.get("right", width+2)) <= width+1, f"Repository navigation overflows at {width}px: {nav}")
    expected = 1 if width <= 420 else 2
    require(active_tracks(str(nav.get("tracks", ""))) == expected, f"Repository navigation is not {expected} columns at {width}px: {nav}")


def exercise(session_id: str, target_url: str) -> None:
    request("POST", f"/session/{session_id}/timeouts", {"implicit": 0, "pageLoad": 15000, "script": 10000})
    request("POST", f"/session/{session_id}/url", {"url": target_url})

    for requested_width, requested_height in VIEWPORTS:
        set_viewport(session_id, requested_width, requested_height)
        state = read_state(session_id)
        width = int(state.get("width", 0))
        require(abs(width-requested_width) <= 1, f"Repository CSS viewport is {width}px; expected {requested_width}px")
        require(state.get("ready") == "complete", f"Repository page did not finish loading at {width}px: {state}")
        require(state.get("title") == "GitHub Repositories — GoreeCloud", f"Unexpected repository page title: {state}")
        require(int(state.get("cards", 0)) == 57, f"Repository directory did not render all 57 repositories at {width}px: {state}")
        require(int(state.get("scrollWidth", width+2)) <= width+1, f"Repository page horizontally overflows at {width}px: {state}")
        require(state.get("headerPosition") not in {"sticky", "fixed"}, f"Repository header overlays content at {width}px: {state}")
        require(float(state.get("heroTop", 0))+1 >= float(state.get("headerBottom", 0)), f"Repository hero overlaps header at {width}px: {state}")

        expected_repo_columns = 2 if width > 900 else 1
        for tracks in state.get("gridTracks") or []:
            require(active_tracks(str(tracks)) == expected_repo_columns, f"Repository card grid is not {expected_repo_columns} columns at {width}px: {state}")
        expected_hero = 2 if width > 900 else 1
        require(active_tracks(str(state.get("heroTracks", ""))) == expected_hero, f"Repository hero is not {expected_hero} columns at {width}px: {state}")
        expected_filter = 3 if width > 1023 else (2 if width > 599 else 1)
        require(active_tracks(str(state.get("filterTracks", ""))) == expected_filter, f"Repository filters are not {expected_filter} columns at {width}px: {state}")
        expected_visibility = 3 if width > 599 else 1
        require(active_tracks(str(state.get("visibilityTracks", ""))) == expected_visibility, f"Repository visibility controls are not {expected_visibility} columns at {width}px: {state}")

        if width <= 720:
            actions = state.get("heroActions") or []
            action_width = float(state.get("actionWidth", 0))
            require(bool(actions) and action_width > 0, f"Repository hero actions missing at {width}px")
            require(all(float(action.get("width", 0)) >= action_width*.98 for action in actions), f"Repository hero actions are not full-width at {width}px: {state}")
            validate_nav(session_id, width)


def run(target: str) -> int:
    base_url = verify_remote_deployment.target_url(target)
    target_url = urljoin(base_url.rstrip("/")+"/", "repositories.html")
    process: subprocess.Popen[bytes] | None = None
    log_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="goreecloud-repositories-chromedriver-", suffix=".log", delete=False) as log:
            log_path = log.name
            process = subprocess.Popen([chromedriver(), f"--port={PORT}", "--allowed-ips=127.0.0.1"], stdout=log, stderr=subprocess.STDOUT)
        wait_driver()
        last: Exception | None = None
        for attempt in range(2):
            session_id: str | None = None
            try:
                session_id = create_session()
                exercise(session_id, target_url)
                print(f"Repository directory responsive Chrome smoke passed for {target}: {target_url}")
                return 0
            except Exception as error:
                last = error
                if attempt == 0:
                    print(f"Chrome session failed before repository responsive acceptance; retrying fresh: {error}")
            finally:
                if session_id:
                    try: request("DELETE", f"/session/{session_id}")
                    except Exception: pass
        raise BrowserError(str(last))
    except Exception as error:
        print(f"Repository directory responsive Chrome smoke failed for {target}: {target_url}")
        print(f"- {error}")
        if log_path:
            try: log_text = Path(log_path).read_text(encoding="utf-8", errors="replace")
            except OSError: log_text = ""
            if log_text: print(log_text[-8000:])
        return 1
    finally:
        if process:
            process.terminate()
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait(timeout=5)
        if log_path:
            try: Path(log_path).unlink()
            except OSError: pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("branch-preview", "production"), required=True)
    args = parser.parse_args()
    return run(args.target)


if __name__ == "__main__":
    raise SystemExit(main())
