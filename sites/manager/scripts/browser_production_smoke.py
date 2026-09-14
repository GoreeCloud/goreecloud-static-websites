#!/usr/bin/env python3
"""Exercise the live GoreeCloud Manager V1.4 public site in headless Chrome."""
from __future__ import annotations
from pathlib import Path
import subprocess
import tempfile
import browser_responsive_smoke as smoke

PRODUCTION_URL = "https://manage.goreecloud.com/"
GLAZE_REVISION = "84cb3db4884042f0fa25ed6d475a127fb110f596"

def require(condition: bool, message: str) -> None:
    if not condition:
        raise smoke.BrowserError(message)

def verify_live_content(session_id: str) -> None:
    state = smoke.execute(session_id, r"""
    const images=[...document.images];
    return {title:document.title,glaze:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',glazeRevision:document.querySelector('meta[name="goreecloud-glaze-source-revision"]')?.content||'',consumerState:document.querySelector('meta[name="goreecloud-glaze-consumer-state"]')?.content||'',robots:document.querySelector('meta[name="robots"]')?.content||'',canonical:document.querySelector('link[rel="canonical"]')?.href||'',capabilityCards:document.querySelectorAll('#visibility .cap-grid article').length,authorityCards:document.querySelectorAll('#boundaries .principle-grid article').length,readinessCards:document.querySelectorAll('#readiness .status-grid article').length,imageCount:images.length,loadedImages:images.filter(image=>image.complete&&image.naturalWidth>0&&image.naturalHeight>0).length,failedImages:images.filter(image=>image.complete&&(image.naturalWidth===0||image.naturalHeight===0)).map(image=>image.src),bodyText:document.body.innerText};
    """)
    require(isinstance(state, dict), f"Manager production browser state unreadable: {state!r}")
    require(state.get("title") == "GoreeCloud Manager — Operational visibility with explicit authority", f"unexpected Manager title: {state}")
    require(state.get("glaze") == "1.4.0", f"Manager GLAZE UI version mismatch: {state}")
    require(state.get("glazeRevision") == GLAZE_REVISION, f"Manager GLAZE UI revision mismatch: {state}")
    require(state.get("consumerState") == "build-migrated-rendered-acceptance-pending", f"Manager consumer state mismatch: {state}")
    require(state.get("robots") == "noindex,nofollow,noarchive", f"Manager robots drifted: {state}")
    require(state.get("canonical") == PRODUCTION_URL, f"Manager canonical mismatch: {state}")
    require(int(state.get("capabilityCards",0)) == 6 and int(state.get("authorityCards",0)) == 6 and int(state.get("readinessCards",0)) == 2, f"Manager card structure drift: {state}")
    require(int(state.get("loadedImages",-1)) == int(state.get("imageCount",0)), f"Manager failed images: {state.get('failedImages')}")
    text=str(state.get("bodyText",""))
    for marker in ("Understand the platform.","Preserve each system’s authority.","Conceptual · no live data","A unified view must not become a competing source of truth.","Visibility before mutation","Production remains separately unapproved.","GLAZE UI V1.4 publication target"):
        require(marker in text, f"Manager production missing marker: {marker!r}")

def main() -> int:
    smoke.TARGET = PRODUCTION_URL
    driver=None;session_id=None;log_path=None
    try:
        with tempfile.NamedTemporaryFile(prefix="manager-v14-production-chromedriver-",suffix=".log",delete=False) as log:
            log_path=Path(log.name);driver=subprocess.Popen([smoke.chromedriver(),f"--port={smoke.DRIVER_PORT}","--allowed-ips=127.0.0.1"],stdout=log,stderr=subprocess.STDOUT)
        smoke.wait_driver();session_id=smoke.create_session();smoke.exercise(session_id);verify_live_content(session_id)
        print("Manager canonical production Chrome acceptance passed for GLAZE UI V1.4 publication; private Manager runtime acceptance remains separate")
        return 0
    except Exception as error:
        print(f"Manager production Chrome acceptance failed: {error}")
        return 1
    finally:
        if session_id:
            try: smoke.driver_request("DELETE",f"/session/{session_id}")
            except Exception: pass
        if driver:
            driver.terminate()
            try: driver.wait(timeout=5)
            except subprocess.TimeoutExpired: driver.kill();driver.wait(timeout=5)
        if log_path:
            try: log_path.unlink()
            except OSError: pass

if __name__ == "__main__":
    raise SystemExit(main())
