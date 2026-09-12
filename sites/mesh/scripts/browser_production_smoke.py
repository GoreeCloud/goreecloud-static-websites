#!/usr/bin/env python3
"""Exercise the live GoreeCloud Mesh Center in headless Chrome."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile

import browser_responsive_smoke as smoke

PRODUCTION_URL = "https://mesh.goreecloud.com/"
GLAZE_REVISION = "8354308445da9ac35ced2b37a7f503a08a0aaf72"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise smoke.BrowserError(message)


def verify_live_content(session_id: str) -> None:
    state = smoke.execute(
        session_id,
        r"""
        const images=[...document.images];
        return {
          title:document.title,
          glaze:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',
          glazeRevision:document.querySelector('meta[name="goreecloud-glaze-source-revision"]')?.content||'',
          consumerState:document.querySelector('meta[name="goreecloud-glaze-consumer-state"]')?.content||'',
          canonical:document.querySelector('link[rel="canonical"]')?.href||'',
          capabilityCards:document.querySelectorAll('#model .cap-grid article').length,
          evidenceCards:document.querySelectorAll('#evidence .principle-grid article').length,
          authorityCards:document.querySelectorAll('#boundaries .boundary-list article').length,
          imageCount:images.length,
          loadedImages:images.filter(image=>image.complete&&image.naturalWidth>0&&image.naturalHeight>0).length,
          failedImages:images.filter(image=>image.complete&&(image.naturalWidth===0||image.naturalHeight===0)).map(image=>image.src),
          bodyText:document.body.innerText,
        };
        """,
    )
    require(isinstance(state, dict), f"Mesh Center production browser state unreadable: {state!r}")
    require(state.get("title") == "GoreeCloud Mesh — Coordination without authority transfer", f"unexpected Mesh Center title: {state.get('title')!r}")
    require(state.get("glaze") == "1.3.0", f"Mesh Center Glaze version mismatch: {state}")
    require(state.get("glazeRevision") == GLAZE_REVISION, f"Mesh Center Glaze revision mismatch: {state}")
    require(state.get("consumerState") == "source-migrated-rendered-acceptance-pending", f"Mesh Center consumer-state mismatch: {state}")
    require(state.get("canonical") == PRODUCTION_URL, f"Mesh Center canonical link mismatch: {state.get('canonical')!r}")
    require(int(state.get("capabilityCards", 0)) == 6, f"Mesh Center rendered {state.get('capabilityCards')} capability cards; expected 6")
    require(int(state.get("evidenceCards", 0)) == 6, f"Mesh Center rendered {state.get('evidenceCards')} evidence cards; expected 6")
    require(int(state.get("authorityCards", 0)) == 6, f"Mesh Center rendered {state.get('authorityCards')} authority cards; expected 6")
    require(int(state.get("loadedImages", -1)) == int(state.get("imageCount", 0)), f"Mesh Center contains failed image loads: {state.get('failedImages')}")
    text = str(state.get("bodyText", ""))
    for marker in (
        "Coordinate the platform.",
        "Keep authority distributed.",
        "Move evidence without inventing truth.",
        "authority_transfer = false",
        "Production acceptance stays explicit.",
        "Mesh itself remains in Development.",
    ):
        require(marker in text, f"Mesh Center production browser missing rendered marker: {marker!r}")


def main() -> int:
    smoke.TARGET = PRODUCTION_URL
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="mesh-production-chromedriver-", suffix=".log", delete=False) as log:
            log_path = log.name
            driver = subprocess.Popen(
                [smoke.chromedriver(), f"--port={smoke.DRIVER_PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        smoke.wait_driver()
        session_id = smoke.create_session()
        smoke.exercise(session_id)
        verify_live_content(session_id)
        print(
            "Mesh Center production Chrome smoke passed at 1180, 768, 390, and 320px: canonical live page rendered the reviewed Mesh surface, exact Glaze V1.3 identity, capability/evidence/authority cards, working appearance controls, canonical URL, and all images loaded."
        )
        return 0
    except Exception as error:
        print(f"Mesh Center production Chrome smoke failed: {error}")
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
                smoke.driver_request("DELETE", f"/session/{session_id}")
            except Exception:
                pass
        if driver:
            driver.terminate()
            try:
                driver.wait(timeout=5)
            except subprocess.TimeoutExpired:
                driver.kill()
                driver.wait(timeout=5)
        if log_path:
            try:
                Path(log_path).unlink()
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
