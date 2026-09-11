#!/usr/bin/env python3
"""Exercise the live GoreeCloud Suite publication in headless Chrome."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import time

import browser_responsive_smoke as smoke

PRODUCTION_URL = "https://suite.goreecloud.com/"
EXPECTED_PRODUCT_COUNT = 45
EXPECTED_GROUP_COUNT = 9
REQUIRED_PRODUCTS = (
    "GoreeCloud Documents",
    "GoreeCloud Drive",
    "GoreeCloud File Manager",
    "GoreeCloud Mail",
    "GoreeCloud Messenger",
    "GoreeCloud Maps",
    "GoreeCloud Terminal",
    "GoreeCloud App Store",
    "GoreeCloud Gateway",
    "GoreeCloud AI",
    "GoreeCloud Index",
    "GoreeCloud Code",
    "GoreeCloud Health",
    "GoreeCloud Reader",
    "GoreeCloud Router OS",
    "GoreeCloud Social",
    "GoreeCloud Home",
    "GoreeCloud Home Security",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise smoke.BrowserError(message)


def verify_live_content(session_id: str) -> None:
    state = smoke.execute(
        session_id,
        """
        const cards=[...document.querySelectorAll('.app-card')];
        const groups=[...document.querySelectorAll('.product-group')];
        const images=[...document.images];
        return {
          title:document.title,
          glaze:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',
          glazeRevision:document.querySelector('meta[name="goreecloud-glaze-source-revision"]')?.content||'',
          productCount:cards.length,
          groupCount:groups.length,
          names:cards.map(card=>card.querySelector('h3')?.textContent.trim()||'').filter(Boolean),
          imageCount:images.length,
          loadedImages:images.filter(image=>image.complete&&image.naturalWidth>0&&image.naturalHeight>0).length,
          failedImages:images.filter(image=>image.complete&&(image.naturalWidth===0||image.naturalHeight===0)).map(image=>image.src),
          canonical:document.querySelector('link[rel="canonical"]')?.href||'',
          bodyText:document.body.innerText,
        };
        """,
    )
    require(isinstance(state, dict), f"Suite production browser state unreadable: {state!r}")
    require(state.get("title") == "GoreeCloud Suite", f"unexpected Suite production title: {state}")
    require(state.get("glaze") == "1.3.0", f"Suite production browser Glaze version mismatch: {state}")
    require(
        state.get("glazeRevision") == "8354308445da9ac35ced2b37a7f503a08a0aaf72",
        f"Suite production browser Glaze revision mismatch: {state}",
    )
    require(int(state.get("productCount", 0)) == EXPECTED_PRODUCT_COUNT, f"Suite browser rendered {state.get('productCount')} products; expected {EXPECTED_PRODUCT_COUNT}")
    require(int(state.get("groupCount", 0)) == EXPECTED_GROUP_COUNT, f"Suite browser rendered {state.get('groupCount')} groups; expected {EXPECTED_GROUP_COUNT}")
    names = set(state.get("names") or [])
    for product in REQUIRED_PRODUCTS:
        require(product in names, f"Suite production browser missing product card: {product}")
    require(state.get("canonical") == PRODUCTION_URL, f"Suite canonical link mismatch: {state.get('canonical')!r}")
    require(int(state.get("loadedImages", -1)) == int(state.get("imageCount", 0)), f"Suite production contains failed image loads: {state.get('failedImages')}")
    text = str(state.get("bodyText", ""))
    for marker in ("45\nverified Suite products", "9\nfunctional product groups", "GLAZE UI V1.3"):
        require(marker in text, f"Suite production browser missing rendered marker: {marker!r}")


def main() -> int:
    smoke.TARGET = PRODUCTION_URL
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="suite-production-chromedriver-", suffix=".log", delete=False) as log:
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
            "Suite production Chrome smoke passed at 1180, 768, 390, and 320px: canonical live page rendered 45 products in 9 groups, "
            "approved Glaze V1.3 identity, representative reconciled products, canonical URL, and all images loaded."
        )
        return 0
    except Exception as error:
        print(f"Suite production Chrome smoke failed: {error}")
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
