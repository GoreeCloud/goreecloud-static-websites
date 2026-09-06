#!/usr/bin/env python3
"""Real-browser responsive acceptance for Blog, Roadmap, and Archive."""

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

ROOT = Path(__file__).resolve().parents[1]
HOST = "127.0.0.1"
WEB_PORT = 8770
DRIVER_PORT = 9520
DRIVER_BASE = f"http://{HOST}:{DRIVER_PORT}"
TARGET = f"http://{HOST}:{WEB_PORT}/"
VIEWPORTS = ((1180, 900), (768, 900), (390, 844), (320, 844))


class BrowserError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise BrowserError(message)


def request(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    body = None if payload is None else json.dumps(payload).encode()
    req = Request(f"{DRIVER_BASE}{path}", data=body, method=method, headers={"Content-Type":"application/json"})
    try:
        with urlopen(req, timeout=25) as response:
            raw = response.read()
    except HTTPError as error:
        raise BrowserError(error.read().decode(errors="replace")) from error
    except (URLError, TimeoutError) as error:
        raise BrowserError(str(error)) from error
    if not raw:
        return None
    value = json.loads(raw.decode()).get("value")
    if isinstance(value, dict) and value.get("error"):
        raise BrowserError(str(value))
    return value


def wait_url(url: str, seconds: float = 12) -> None:
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            pass
        time.sleep(.15)
    raise BrowserError(f"server not ready: {url}")


def chromedriver() -> str:
    for value in (shutil.which("chromedriver"), "/usr/local/share/chromedriver-linux64/chromedriver"):
        if value and Path(value).is_file():
            return value
    raise BrowserError("chromedriver unavailable")


def wait_driver() -> None:
    end = time.monotonic() + 15
    while time.monotonic() < end:
        try:
            value = request("GET", "/status")
            if isinstance(value, dict) and value.get("ready"):
                return
        except Exception:
            pass
        time.sleep(.2)
    raise BrowserError("chromedriver not ready")


def create_session() -> str:
    value = request("POST", "/session", {"capabilities":{"alwaysMatch":{"browserName":"chrome","goog:chromeOptions":{"args":["--headless=new","--no-sandbox","--disable-dev-shm-usage","--disable-background-networking","--disable-extensions","--no-first-run"]}}}})
    require(isinstance(value, dict) and isinstance(value.get("sessionId"), str), f"bad session: {value!r}")
    return value["sessionId"]


def execute(session: str, script: str) -> Any:
    return request("POST", f"/session/{session}/execute/sync", {"script":script,"args":[]})


def set_viewport(session: str, width: int, height: int) -> None:
    request("POST", f"/session/{session}/goog/cdp/execute", {"cmd":"Emulation.setDeviceMetricsOverride","params":{"width":width,"height":height,"deviceScaleFactor":1,"mobile":False}})
    execute(session, "window.scrollTo(0,0); return window.innerWidth;")


def row_capacity(rects: list[dict[str, float]]) -> int:
    if not rects:
        return 0
    return max(
        sum(1 for candidate in rects if abs(float(candidate["top"]) - float(rect["top"])) <= 2)
        for rect in rects
    )


def state_script(site: str) -> str:
    config = {
        "blog": (".top", ".top nav", ".grid .card:not(.featured)"),
        "roadmap": (".site-header", ".nav nav", ".cards article"),
        "archive": (".top", ".top nav", ".timeline article"),
    }
    header, nav, items = config[site]
    return f"""
    const header=document.querySelector('{header}');
    const nav=document.querySelector('{nav}');
    const itemRects=[...document.querySelectorAll('{items}')].map(el=>el.getBoundingClientRect()).filter(r=>r.width>0&&r.height>0).map(r=>({{left:r.left,right:r.right,top:r.top,width:r.width,height:r.height}}));
    const navRects=[...nav.querySelectorAll('a')].map(el=>el.getBoundingClientRect()).filter(r=>r.width>0&&r.height>0);
    const hs=getComputedStyle(header), ns=getComputedStyle(nav), hr=header.getBoundingClientRect(), main=document.querySelector('main').getBoundingClientRect();
    return {{width:window.innerWidth,scrollWidth:document.documentElement.scrollWidth,headerPosition:hs.position,headerBottom:hr.bottom,mainTop:main.top,navDisplay:ns.display,navTracks:ns.gridTemplateColumns,minNavHeight:navRects.length?Math.min(...navRects.map(r=>r.height)):0,items:itemRects}};
    """


def active_tracks(value: str) -> int:
    result = 0
    for token in value.split():
        try:
            if float(token.removesuffix("px")) > 1:
                result += 1
        except ValueError:
            pass
    return result


def validate(site: str, session: str) -> None:
    request("POST", f"/session/{session}/url", {"url":TARGET})
    for requested_width, height in VIEWPORTS:
        set_viewport(session, requested_width, height)
        state = execute(session, state_script(site))
        require(isinstance(state, dict), f"{site} state unreadable")
        width = int(state["width"])
        require(abs(width-requested_width)<=1, f"{site} viewport {width}, expected {requested_width}")
        require(int(state["scrollWidth"])<=width+1, f"{site} horizontal overflow at {width}: {state}")
        require(state["headerPosition"] not in {"sticky","fixed"}, f"{site} header overlays content at {width}: {state}")
        require(float(state["mainTop"])+1>=float(state["headerBottom"]), f"{site} main content overlaps header at {width}: {state}")
        require(float(state["minNavHeight"])>=47.5, f"{site} nav target below 48px at {width}: {state}")
        items = state.get("items") or []
        require(bool(items), f"{site} rendered no review items at {width}")

        if site == "blog":
            expected = 3 if width>1060 else (2 if width>760 else 1)
            require(row_capacity(items)==expected, f"Blog cards are not {expected} columns at {width}: {state}")
            if width<=760:
                nav_expected = 1 if width<=420 else 3
                require(active_tracks(str(state["navTracks"]))==nav_expected, f"Blog nav is not {nav_expected} columns at {width}: {state}")
        elif site == "roadmap":
            expected = 2 if width>700 else 1
            require(row_capacity(items)==expected, f"Roadmap cards are not {expected} columns at {width}: {state}")
            if width<=700:
                nav_expected = 1 if width<=420 else 2
                require(active_tracks(str(state["navTracks"]))==nav_expected, f"Roadmap nav is not {nav_expected} columns at {width}: {state}")
        else:
            if width<=430:
                require(row_capacity(items)==1, f"Archive timeline is not one readable column at {width}: {state}")
            if width<=760:
                nav_expected = 1 if width<=430 else 2
                require(active_tracks(str(state["navTracks"]))==nav_expected, f"Archive nav is not {nav_expected} columns at {width}: {state}")


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--site",choices=("blog","roadmap","archive"),required=True); args=parser.parse_args()
    site_dir=ROOT/"sites"/args.site
    require((site_dir/"index.html").is_file(), f"missing site: {site_dir}")
    server=driver=None; session=None; log_path=None
    try:
        server=subprocess.Popen(["python3","-m","http.server",str(WEB_PORT),"--bind",HOST,"--directory",str(site_dir)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        wait_url(TARGET)
        with tempfile.NamedTemporaryFile(prefix=f"{args.site}-chrome-",suffix=".log",delete=False) as log:
            log_path=log.name; driver=subprocess.Popen([chromedriver(),f"--port={DRIVER_PORT}","--allowed-ips=127.0.0.1"],stdout=log,stderr=subprocess.STDOUT)
        wait_driver(); session=create_session(); validate(args.site,session)
        print(f"{args.site} responsive Chrome acceptance passed at 1180/768/390/320px."); return 0
    except Exception as error:
        print(f"{args.site} responsive Chrome acceptance failed: {error}")
        if log_path:
            try: print(Path(log_path).read_text(encoding="utf-8",errors="replace")[-6000:])
            except OSError: pass
        return 1
    finally:
        if session:
            try: request("DELETE",f"/session/{session}")
            except Exception: pass
        for process in (driver,server):
            if process:
                process.terminate()
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=5)
        if log_path:
            try: Path(log_path).unlink()
            except OSError: pass


if __name__=="__main__": raise SystemExit(main())
