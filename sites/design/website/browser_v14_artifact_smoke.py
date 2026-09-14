#!/usr/bin/env python3
"""Exercise the exact built Design Center GLAZE UI V1.4 artifact in Chrome."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json

SITE = Path(__file__).resolve().parent
DIST = SITE / "dist"
HOST = "127.0.0.1"
WEB_PORT = 8784
DRIVER_PORT = 9540
URL = f"http://{HOST}:{WEB_PORT}/"
VIEWPORTS = ((1180, 900), (768, 900), (390, 844), (320, 844))
REVISION = "84cb3db4884042f0fa25ed6d475a127fb110f596"

class SmokeError(RuntimeError):
    pass

def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeError(message)

def request_driver(method: str, path: str, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(f"http://{HOST}:{DRIVER_PORT}{path}", data=data, method=method, headers={"Content-Type":"application/json"})
    try:
        with urlopen(req, timeout=20) as response:
            raw = response.read()
    except HTTPError as error:
        raise SmokeError(error.read().decode("utf-8", errors="replace")) from error
    except (URLError, TimeoutError) as error:
        raise SmokeError(str(error)) from error
    if not raw:
        return None
    value = json.loads(raw.decode("utf-8")).get("value")
    if isinstance(value, dict) and value.get("error"):
        raise SmokeError(str(value))
    return value

def execute(session: str, script: str):
    return request_driver("POST", f"/session/{session}/execute/sync", {"script":script,"args":[]})

def wait_ready(url: str, driver=False) -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        try:
            if driver:
                state = request_driver("GET", "/status")
                if isinstance(state, dict) and state.get("ready"):
                    return
            else:
                with urlopen(url, timeout=1) as response:
                    if response.status == 200:
                        return
        except Exception:
            pass
        time.sleep(.2)
    raise SmokeError(f"service did not become ready: {url}")

def main() -> int:
    require(DIST.is_dir() and (DIST/"index.html").is_file(), "Design Center dist missing; build_v14.py must run first")
    driver_bin = shutil.which("chromedriver") or "/usr/local/share/chromedriver-linux64/chromedriver"
    require(Path(driver_bin).is_file(), "chromedriver unavailable")
    server = driver = None
    session = None
    log_path = None
    try:
        server = subprocess.Popen(["python3","-m","http.server",str(WEB_PORT),"--bind",HOST,"--directory",str(DIST)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wait_ready(URL)
        with tempfile.NamedTemporaryFile(prefix="design-v14-chromedriver-", suffix=".log", delete=False) as log:
            log_path = Path(log.name)
            driver = subprocess.Popen([driver_bin,f"--port={DRIVER_PORT}","--allowed-ips=127.0.0.1"], stdout=log, stderr=subprocess.STDOUT)
        wait_ready(f"http://{HOST}:{DRIVER_PORT}/status", driver=True)
        value = request_driver("POST","/session",{"capabilities":{"alwaysMatch":{"browserName":"chrome","goog:chromeOptions":{"args":["--headless=new","--no-sandbox","--disable-dev-shm-usage","--disable-background-networking","--window-size=1180,900"]}}}})
        require(isinstance(value, dict) and value.get("sessionId"), f"Chrome session unavailable: {value}")
        session = value["sessionId"]
        request_driver("POST",f"/session/{session}/url",{"url":URL})
        for width,height in VIEWPORTS:
            request_driver("POST",f"/session/{session}/goog/cdp/execute",{"cmd":"Emulation.setDeviceMetricsOverride","params":{"width":width,"height":height,"deviceScaleFactor":1,"mobile":False}})
            time.sleep(.1)
            state = execute(session, """
            const visible=n=>{const s=getComputedStyle(n),r=n.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};
            const controls=[...document.querySelectorAll('header a,header button,.glaze-button')].filter(visible);
            return {ready:document.readyState,title:document.title,glaze:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',revision:document.querySelector('meta[name="goreecloud-glaze-source-revision"]')?.content||'',consumer:document.querySelector('meta[name="goreecloud-glaze-consumer-state"]')?.content||'',width:window.innerWidth,scroll:document.documentElement.scrollWidth,body:document.body.scrollWidth,min:controls.length?Math.min(...controls.map(n=>n.getBoundingClientRect().height)):0,styles:[...document.querySelectorAll('link[rel="stylesheet"]')].map(n=>({href:n.href,loaded:Boolean(n.sheet)})),broken:[...document.images].filter(i=>!i.complete||i.naturalWidth<=0).map(i=>i.src)};
            """)
            require(state.get("ready") == "complete", f"Design Center did not finish loading at {width}px: {state}")
            require(state.get("title") == "GoreeCloud Design Center — GLAZE UI V1.4", f"Design Center title drift: {state}")
            require(state.get("glaze") == "1.4.0" and state.get("revision") == REVISION, f"Design Center V1.4 identity drift: {state}")
            require(state.get("consumer") == "build-migrated-rendered-acceptance-pending", f"Design Center acceptance boundary drift: {state}")
            require(int(state.get("scroll",99999)) <= int(state.get("width",0))+1 and int(state.get("body",99999)) <= int(state.get("width",0))+1, f"Design Center horizontal overflow at {width}px: {state}")
            require(float(state.get("min",0)) >= 47.5, f"Design Center interaction target below 48px at {width}px: {state}")
            require(all(item.get("loaded") for item in state.get("styles") or []), f"Design Center stylesheet load failure at {width}px: {state}")
            require(not state.get("broken"), f"Design Center broken image at {width}px: {state}")
        print("Design Center V1.4 built-artifact Chrome acceptance passed at 1180, 768, 390, and 320px")
        return 0
    except Exception as error:
        print(f"Design Center V1.4 built-artifact Chrome acceptance failed: {error}")
        return 1
    finally:
        if session:
            try: request_driver("DELETE",f"/session/{session}")
            except Exception: pass
        for proc in (driver,server):
            if proc:
                proc.terminate()
                try: proc.wait(timeout=5)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=5)
        if log_path:
            try: log_path.unlink()
            except OSError: pass

if __name__ == "__main__":
    raise SystemExit(main())
