#!/usr/bin/env python3
"""Exercise the live GoreeCloud Labs canonical host in headless Chrome."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile

import browser_smoke as smoke

PRODUCTION_URL = "https://labs.goreecloud.com/"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise smoke.SmokeError(message)


def verify_live_content(session_id: str) -> None:
    state = smoke.execute(
        session_id,
        r"""
        const images=[...document.images];
        return {
          title:document.title,
          glaze:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',
          robots:document.querySelector('meta[name="robots"]')?.content||'',
          canonical:document.querySelector('link[rel="canonical"]')?.href||'',
          workstreams:document.querySelectorAll('[data-workstream]').length,
          lanes:document.querySelectorAll('[data-lane]').length,
          filters:document.querySelectorAll('[data-filter]').length,
          imageCount:images.length,
          loadedImages:images.filter(image=>image.complete&&image.naturalWidth>0&&image.naturalHeight>0).length,
          failedImages:images.filter(image=>image.complete&&(image.naturalWidth===0||image.naturalHeight===0)).map(image=>image.src),
          bodyText:document.body.innerText,
        };
        """,
    )
    require(isinstance(state, dict), f"Labs production browser state unreadable: {state!r}")
    require(state.get("title") == "GoreeCloud Labs — Development Center", f"unexpected Labs title: {state.get('title')!r}")
    require(state.get("glaze") == "1.3.0", f"Labs Glaze version mismatch: {state}")
    require(state.get("robots") == "noindex,nofollow", f"Labs indexing boundary drifted: {state}")
    require(state.get("canonical") == PRODUCTION_URL, f"Labs canonical link mismatch: {state.get('canonical')!r}")
    require(int(state.get("workstreams", 0)) == 27, f"Labs rendered {state.get('workstreams')} workstreams; expected 27")
    require(int(state.get("lanes", 0)) == 6, f"Labs rendered {state.get('lanes')} lanes; expected 6")
    require(int(state.get("filters", 0)) == 7, f"Labs rendered {state.get('filters')} filter controls; expected 7")
    require(
        int(state.get("loadedImages", -1)) == int(state.get("imageCount", 0)),
        f"Labs contains failed image loads: {state.get('failedImages')}",
    )
    text = str(state.get("bodyText", ""))
    for marker in (
        "Where GoreeCloud gets built next.",
        "Labs is not a release channel.",
        "Development workstreams",
        "Integral Platform Systems",
        "Privacy Shield",
        "GoreeCloud Mesh",
        "Evidence stays scoped",
    ):
        require(marker in text, f"Labs production browser missing rendered marker: {marker!r}")


def main() -> int:
    smoke.TARGET = PRODUCTION_URL
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="labs-production-chromedriver-", suffix=".log", delete=False) as log:
            log_path = log.name
            driver_path = __import__("shutil").which("chromedriver") or "/usr/local/share/chromedriver-linux64/chromedriver"
            require(Path(driver_path).is_file(), "chromedriver unavailable")
            driver = subprocess.Popen(
                [driver_path, f"--port={smoke.DRIVER_PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        smoke.wait_driver()
        session_id = smoke.session()
        smoke.exercise(session_id)
        verify_live_content(session_id)
        print(
            "Labs production Chrome smoke passed at 1180/768/390/320: canonical live page rendered 27 workstreams across six lanes, filter and appearance interactions passed, viewport containment held, canonical/noindex/Glaze metadata matched, and all images loaded."
        )
        return 0
    except Exception as error:
        print(f"Labs production Chrome smoke failed: {error}")
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
                smoke.req("DELETE", f"/session/{session_id}")
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
