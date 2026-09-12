#!/usr/bin/env python3
"""Exercise the live GoreeCloud Manager public site in headless Chrome."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile

import browser_responsive_smoke as smoke

PRODUCTION_URL = "https://manage.goreecloud.com/"
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
          robots:document.querySelector('meta[name="robots"]')?.content||'',
          canonical:document.querySelector('link[rel="canonical"]')?.href||'',
          capabilityCards:document.querySelectorAll('#visibility .cap-grid article').length,
          authorityCards:document.querySelectorAll('#boundaries .principle-grid article').length,
          readinessCards:document.querySelectorAll('#readiness .status-grid article').length,
          imageCount:images.length,
          loadedImages:images.filter(image=>image.complete&&image.naturalWidth>0&&image.naturalHeight>0).length,
          failedImages:images.filter(image=>image.complete&&(image.naturalWidth===0||image.naturalHeight===0)).map(image=>image.src),
          bodyText:document.body.innerText,
        };
        """,
    )
    require(isinstance(state, dict), f"Manager production browser state unreadable: {state!r}")
    require(
        state.get("title") == "GoreeCloud Manager — Operational visibility with explicit authority",
        f"unexpected Manager public-site title: {state.get('title')!r}",
    )
    require(state.get("glaze") == "1.3.0", f"Manager Glaze version mismatch: {state}")
    require(state.get("glazeRevision") == GLAZE_REVISION, f"Manager Glaze revision mismatch: {state}")
    require(
        state.get("consumerState") == "source-migrated-rendered-acceptance-pending",
        f"Manager consumer-state mismatch: {state}",
    )
    require(state.get("robots") == "noindex,nofollow,noarchive", f"Manager robots metadata drifted: {state}")
    require(state.get("canonical") == PRODUCTION_URL, f"Manager canonical link mismatch: {state.get('canonical')!r}")
    require(
        int(state.get("capabilityCards", 0)) == 6,
        f"Manager rendered {state.get('capabilityCards')} capability cards; expected 6",
    )
    require(
        int(state.get("authorityCards", 0)) == 6,
        f"Manager rendered {state.get('authorityCards')} authority cards; expected 6",
    )
    require(
        int(state.get("readinessCards", 0)) == 2,
        f"Manager rendered {state.get('readinessCards')} readiness cards; expected 2",
    )
    require(
        int(state.get("loadedImages", -1)) == int(state.get("imageCount", 0)),
        f"Manager contains failed image loads: {state.get('failedImages')}",
    )
    text = str(state.get("bodyText", ""))
    for marker in (
        "Understand the platform.",
        "Preserve each system’s authority.",
        "Conceptual · no live data",
        "A unified view must not become a competing source of truth.",
        "Visibility before mutation",
        "Production remains separately unapproved.",
    ):
        require(marker in text, f"Manager production browser missing rendered marker: {marker!r}")


def main() -> int:
    smoke.TARGET = PRODUCTION_URL
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="manager-production-chromedriver-", suffix=".log", delete=False) as log:
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
            "Manager production Chrome smoke passed at 1180, 768, 390, and 320px: canonical live page rendered the reviewed public Manager surface, exact Glaze V1.3 identity, visibility/authority/readiness content, working appearance controls, canonical URL, and all images loaded."
        )
        return 0
    except Exception as error:
        print(f"Manager production Chrome smoke failed: {error}")
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
