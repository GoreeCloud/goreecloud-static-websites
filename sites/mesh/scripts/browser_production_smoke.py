#!/usr/bin/env python3
"""Exercise the live GoreeCloud Mesh Center V1.4 publication in headless Chrome."""
from __future__ import annotations
from pathlib import Path
import subprocess
import tempfile
import browser_responsive_smoke as smoke

PRODUCTION_URL = "https://mesh.goreecloud.com/"
GLAZE_REVISION = "84cb3db4884042f0fa25ed6d475a127fb110f596"

def require(condition: bool, message: str) -> None:
    if not condition:
        raise smoke.BrowserError(message)

def verify_live_content(session_id: str) -> None:
    state = smoke.execute(session_id, r"""
    const images=[...document.images];
    return {title:document.title,glaze:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',glazeRevision:document.querySelector('meta[name="goreecloud-glaze-source-revision"]')?.content||'',consumerState:document.querySelector('meta[name="goreecloud-glaze-consumer-state"]')?.content||'',canonical:document.querySelector('link[rel="canonical"]')?.href||'',capabilityCards:document.querySelectorAll('#model .cap-grid article').length,evidenceCards:document.querySelectorAll('#evidence .principle-grid article').length,authorityCards:document.querySelectorAll('#boundaries .boundary-list article').length,imageCount:images.length,loadedImages:images.filter(image=>image.complete&&image.naturalWidth>0&&image.naturalHeight>0).length,failedImages:images.filter(image=>image.complete&&(image.naturalWidth===0||image.naturalHeight===0)).map(image=>image.src),bodyText:document.body.innerText};
    """)
    require(isinstance(state, dict), f"Mesh production browser state unreadable: {state!r}")
    require(state.get("title") == "GoreeCloud Mesh — Coordination without authority transfer", f"unexpected Mesh title: {state}")
    require(state.get("glaze") == "1.4.0", f"Mesh GLAZE UI version mismatch: {state}")
    require(state.get("glazeRevision") == GLAZE_REVISION, f"Mesh GLAZE UI revision mismatch: {state}")
    require(state.get("consumerState") == "build-migrated-rendered-acceptance-pending", f"Mesh consumer-state mismatch: {state}")
    require(state.get("canonical") == PRODUCTION_URL, f"Mesh canonical mismatch: {state}")
    require(int(state.get("capabilityCards",0)) == 6 and int(state.get("evidenceCards",0)) == 6 and int(state.get("authorityCards",0)) == 6, f"Mesh card structure drift: {state}")
    require(int(state.get("loadedImages",-1)) == int(state.get("imageCount",0)), f"Mesh failed images: {state.get('failedImages')}")
    text=str(state.get("bodyText",""))
    for marker in ("Coordinate the platform.","Keep authority distributed.","Move evidence without inventing truth.","authority_transfer = false","Production acceptance stays explicit.","Mesh itself remains in Development."):
        require(marker in text, f"Mesh production missing marker: {marker!r}")

def main() -> int:
    smoke.TARGET=PRODUCTION_URL;driver=None;session_id=None;log_path=None
    try:
        with tempfile.NamedTemporaryFile(prefix="mesh-v14-production-chromedriver-",suffix=".log",delete=False) as log:
            log_path=Path(log.name);driver=subprocess.Popen([smoke.chromedriver(),f"--port={smoke.DRIVER_PORT}","--allowed-ips=127.0.0.1"],stdout=log,stderr=subprocess.STDOUT)
        smoke.wait_driver();session_id=smoke.create_session();smoke.exercise(session_id);verify_live_content(session_id)
        print("Mesh Center canonical production Chrome acceptance passed for GLAZE UI V1.4 publication; Mesh runtime acceptance remains separate")
        return 0
    except Exception as error:
        print(f"Mesh Center production Chrome acceptance failed: {error}");return 1
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
if __name__=='__main__':raise SystemExit(main())
