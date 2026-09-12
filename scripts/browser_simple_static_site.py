#!/usr/bin/env python3
"""Exercise an exact built simple-static GoreeCloud artifact in headless Chrome.

The browser gate is intentionally content-agnostic. Package-specific validators own
site copy and information architecture; this script owns shared rendered invariants
needed before a Cloudflare source cutover can be considered safe.
"""

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

from simple_static_publication import resolve_site

ROOT = Path(__file__).resolve().parents[1]
VIEWPORTS = ((1180, 900), (768, 900), (390, 844), (320, 844))
DRIVER_HOST = "127.0.0.1"
DRIVER_PORT = 9530
DRIVER_BASE = f"http://{DRIVER_HOST}:{DRIVER_PORT}"
HTTP_TIMEOUT = 20
STARTUP_TIMEOUT = 15


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
        with urlopen(request, timeout=HTTP_TIMEOUT) as response:
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
            status = driver_request("GET", "/status")
            if isinstance(status, dict) and status.get("ready"):
                return
        except Exception as error:
            last = error
        time.sleep(0.2)
    raise BrowserError(f"chromedriver did not become ready: {last}")


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
    return driver_request(
        "POST",
        f"/session/{session_id}/execute/sync",
        {"script": script, "args": []},
    )


def set_viewport(session_id: str, width: int, height: int) -> None:
    driver_request(
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
    execute(session_id, "window.scrollTo(0,0); return true;")


def wait_http(url: str, timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    last: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (URLError, TimeoutError, OSError) as error:
            last = error
        time.sleep(0.1)
    raise BrowserError(f"local simple-static artifact server did not become ready: {last}")


def read_state(session_id: str) -> dict[str, Any]:
    state = execute(
        session_id,
        """
        const visible=node=>{
          const s=getComputedStyle(node); const r=node.getBoundingClientRect();
          return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;
        };
        const rect=node=>{const r=node.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height};};
        const controls=[...document.querySelectorAll('header nav a, header button')].filter(visible);
        const styles=[...document.querySelectorAll('link[rel="stylesheet"]')].map(link=>({href:link.href,loaded:Boolean(link.sheet)}));
        const images=[...document.images];
        const skip=document.querySelector('.skip-link');
        const bodyRegions=[...document.body.children].filter(node=>node!==skip&&visible(node)).map(node=>({tag:node.tagName.toLowerCase(),className:node.className||'',rect:rect(node)}));
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
          canonical:document.querySelector('link[rel="canonical"]')?.href||'',
          controlCount:controls.length,
          minControlHeight:controls.length?Math.min(...controls.map(node=>rect(node).height)):0,
          styles,
          brokenImages:images.filter(img=>!img.complete||img.naturalWidth<=0).map(img=>img.getAttribute('src')),
          bodyRegions,
          skipLinkExists:Boolean(skip),
        };
        """,
    )
    require(isinstance(state, dict), f"Could not read simple-static responsive state: {state!r}")
    return state


def inspect_skip_link(session_id: str) -> dict[str, Any] | None:
    state = execute(
        session_id,
        """
        const link=document.querySelector('.skip-link');
        if(!link)return null;
        const rect=node=>{const r=node.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height};};
        const before=rect(link);
        link.focus();
        const after=rect(link);
        const active=document.activeElement===link;
        link.blur();
        return {active,before,after};
        """,
    )
    if state is None:
        return None
    require(isinstance(state, dict), f"Could not inspect simple-static skip link: {state!r}")
    return state


def exercise(session_id: str, url: str, expected_title: str, canonical_host: str) -> None:
    driver_request(
        "POST",
        f"/session/{session_id}/timeouts",
        {"implicit": 0, "pageLoad": 15000, "script": 10000},
    )
    driver_request("POST", f"/session/{session_id}/url", {"url": url})

    for requested_width, requested_height in VIEWPORTS:
        set_viewport(session_id, requested_width, requested_height)
        time.sleep(0.1)
        state = read_state(session_id)
        width = int(state.get("width", 0))
        height = int(state.get("height", 0))
        require(abs(width - requested_width) <= 1 and abs(height - requested_height) <= 1, f"Unexpected simple-static CSS viewport at {requested_width}px: {state}")
        require(state.get("ready") == "complete", f"Simple-static page did not finish loading at {width}px: {state}")
        require(state.get("title") == expected_title, f"Unexpected simple-static title at {width}px: {state}")
        require(state.get("glaze") == "1.3.0", f"Simple-static Glaze version drift at {width}px: {state}")
        require(state.get("revision") == "8354308445da9ac35ced2b37a7f503a08a0aaf72", f"Simple-static Glaze revision drift at {width}px: {state}")
        require(state.get("consumerState") == "source-migrated-rendered-acceptance-pending", f"Simple-static consumer-state boundary drift at {width}px: {state}")
        require(canonical_host in str(state.get("canonical", "")), f"Simple-static canonical host drift at {width}px: {state}")
        require(int(state.get("scrollWidth", width + 10)) <= width + 1, f"Simple-static document overflows horizontally at {width}px: {state}")
        require(int(state.get("bodyScrollWidth", width + 10)) <= width + 1, f"Simple-static body overflows horizontally at {width}px: {state}")
        require(int(state.get("controlCount", 0)) >= 1, f"Simple-static public header has no visible navigation controls at {width}px: {state}")
        require(float(state.get("minControlHeight", 0)) >= 47.5, f"Simple-static public header target is below the 48px Glaze floor at {width}px: {state}")
        require(all(item.get("loaded") for item in state.get("styles") or []), f"Simple-static stylesheet failed to load at {width}px: {state}")
        require(not (state.get("brokenImages") or []), f"Simple-static page contains broken images at {width}px: {state}")
        for region in state.get("bodyRegions") or []:
            r = region.get("rect") or {}
            require(float(r.get("left", -999)) >= -1 and float(r.get("right", 99999)) <= width + 1, f"Simple-static top-level region escapes viewport at {width}px: {region}; full state={state}")

        if state.get("skipLinkExists"):
            skip = inspect_skip_link(session_id)
            require(skip is not None and skip.get("active") is True, f"Simple-static skip link could not receive focus at {width}px: {skip}")
            focused = skip.get("after") or {}
            require(
                float(focused.get("left", -999)) >= -1
                and float(focused.get("right", 99999)) <= width + 1
                and float(focused.get("top", -999)) >= -1
                and float(focused.get("bottom", 99999)) <= height + 1,
                f"Simple-static skip link is not viewport-contained when focused at {width}px: {skip}",
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site")
    args = parser.parse_args()
    spec = resolve_site(args.site)
    site = ROOT / spec.path
    dist = site / "dist"
    require(dist.is_dir() and (dist / "index.html").is_file(), f"{spec.site_id} dist/ is missing; build exact artifact first")

    web_port = {"roadmap": 8781, "blog": 8782, "archive": 8783}[spec.site_id]
    url = f"http://127.0.0.1:{web_port}/"
    server: subprocess.Popen[bytes] | None = None
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: Path | None = None
    try:
        server = subprocess.Popen(
            ["python3", "-m", "http.server", str(web_port), "--bind", "127.0.0.1", "--directory", str(dist)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        wait_http(url)
        with tempfile.NamedTemporaryFile(prefix=f"goreecloud-{spec.site_id}-chromedriver-", suffix=".log", delete=False) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen(
                [chromedriver(), f"--port={DRIVER_PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        wait_for_driver()
        session_id = create_session()
        exercise(session_id, url, spec.title, spec.canonical_host)
        print(f"{spec.site_id} built-artifact Chrome acceptance passed at 1180×900, 768×900, 390×844, and 320×844.")
        return 0
    except Exception as error:
        print(f"{spec.site_id} built-artifact Chrome acceptance failed: {error}")
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
                log_path.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
