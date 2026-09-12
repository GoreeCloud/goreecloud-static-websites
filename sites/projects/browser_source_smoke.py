#!/usr/bin/env python3
"""Exercise the exact centralized Projects source tree in headless Chrome.

This is a source/browser acceptance gate only. It deliberately serves the reviewed
`sites/projects` tree locally so CI does not depend on a Cloudflare source cutover.
Production publication remains a separate, manually dispatched verification gate.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen

import browser_smoke
import mobile_smoke

SITE = Path(__file__).resolve().parent
WEB_HOST = "127.0.0.1"
WEB_PORT = 8772
TARGET = f"http://{WEB_HOST}:{WEB_PORT}/"
INTERMEDIATE_VIEWPORT = (768, 900)
MOBILE_VIEWPORTS = ((320, 844), (360, 800), (390, 844), (412, 915))


def wait_http(timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urlopen(TARGET, timeout=1) as response:
                if response.status == 200:
                    return
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
        time.sleep(0.1)
    raise browser_smoke.WebDriverError(
        f"local Projects source server did not become ready: {last_error}"
    )


def inspect_intermediate(session_id: str, width: int) -> None:
    state = browser_smoke.execute(
        session_id,
        """
        const cards=[...document.querySelectorAll('#projects .card')];
        const foundation=[...document.querySelectorAll('.foundation-strip>a')];
        const rect=node=>node.getBoundingClientRect();
        return {
          viewport:window.innerWidth,
          scrollWidth:document.documentElement.scrollWidth,
          bodyScrollWidth:document.body.scrollWidth,
          cardCount:cards.length,
          cardLeft:cards.length?Math.min(...cards.map(node=>rect(node).left)):0,
          cardRight:cards.length?Math.max(...cards.map(node=>rect(node).right)):0,
          foundationLeft:foundation.length?Math.min(...foundation.map(node=>rect(node).left)):0,
          foundationRight:foundation.length?Math.max(...foundation.map(node=>rect(node).right)):0,
        };
        """,
    )
    browser_smoke.require(
        isinstance(state, dict),
        f"Projects intermediate responsive state unreadable at {width}px: {state!r}",
    )
    viewport = int(state.get("viewport", 0))
    browser_smoke.require(
        abs(viewport - width) <= 20,
        f"Projects intermediate viewport differs unexpectedly from requested width {width}px: {state}",
    )
    browser_smoke.require(
        int(state.get("scrollWidth", 99999)) <= viewport + 1,
        f"Projects document overflows horizontally at intermediate width {width}px: {state}",
    )
    browser_smoke.require(
        int(state.get("bodyScrollWidth", 99999)) <= viewport + 1,
        f"Projects body overflows horizontally at intermediate width {width}px: {state}",
    )
    browser_smoke.require(
        int(state.get("cardCount", 0)) >= browser_smoke.MIN_PROJECT_CARDS,
        f"Projects card render is incomplete at intermediate width {width}px: {state}",
    )
    browser_smoke.require(
        float(state.get("cardLeft", -1)) >= -1
        and float(state.get("cardRight", 99999)) <= viewport + 1,
        f"Projects cards escape the intermediate viewport at {width}px: {state}",
    )
    browser_smoke.require(
        float(state.get("foundationLeft", -1)) >= -1
        and float(state.get("foundationRight", 99999)) <= viewport + 1,
        f"Projects platform-system cards escape the intermediate viewport at {width}px: {state}",
    )


def main() -> int:
    browser = "chrome"
    driver_port = browser_smoke.DRIVER_PORTS[browser]
    server: subprocess.Popen[bytes] | None = None
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: Path | None = None

    try:
        server = subprocess.Popen(
            [
                "python3",
                "-m",
                "http.server",
                str(WEB_PORT),
                "--bind",
                WEB_HOST,
                "--directory",
                str(SITE),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        wait_http()

        browser_smoke.DRIVER_BASE = f"http://{browser_smoke.DRIVER_HOST}:{driver_port}"
        with tempfile.NamedTemporaryFile(
            prefix="projects-source-chromedriver-", suffix=".log", delete=False
        ) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen(
                browser_smoke.driver_command(browser, driver_port),
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )

        browser_smoke.wait_for_driver(browser)
        session_id = browser_smoke.create_session(browser)

        # Reuse the existing desktop interaction/portfolio/runtime acceptance logic.
        browser_smoke.exercise_page(session_id, TARGET, browser)

        browser_smoke.webdriver_request(
            "POST",
            f"/session/{session_id}/timeouts",
            {"implicit": 0, "pageLoad": 15_000, "script": 10_000},
        )
        mobile_smoke.set_viewport(session_id, *INTERMEDIATE_VIEWPORT)
        browser_smoke.webdriver_request(
            "POST", f"/session/{session_id}/url", {"url": TARGET}
        )
        time.sleep(0.2)
        inspect_intermediate(session_id, INTERMEDIATE_VIEWPORT[0])

        # Re-navigate before the mobile sequence so prior search/filter state cannot
        # leak into responsive acceptance.
        mobile_smoke.set_viewport(session_id, *MOBILE_VIEWPORTS[0])
        browser_smoke.webdriver_request(
            "POST", f"/session/{session_id}/url", {"url": TARGET}
        )
        for width, height in MOBILE_VIEWPORTS:
            mobile_smoke.set_viewport(session_id, width, height)
            time.sleep(0.2)
            mobile_smoke.inspect_mobile(session_id, browser, width)
            mobile_smoke.inspect_touch_assistance(session_id, browser, width)

        print(
            "Projects exact-source Chrome acceptance passed for desktop runtime, "
            "768px containment, and 320/360/390/412px mobile Glaze UI V1.3 behavior."
        )
        return 0
    except (browser_smoke.WebDriverError, OSError, ValueError) as error:
        print(f"Projects exact-source Chrome acceptance failed: {error}")
        if log_path:
            try:
                text = log_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            if text:
                print(text[-8_000:])
        return 1
    finally:
        if session_id:
            try:
                browser_smoke.webdriver_request(
                    "DELETE", f"/session/{session_id}"
                )
            except browser_smoke.WebDriverError:
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
        browser_smoke.DRIVER_BASE = ""


if __name__ == "__main__":
    raise SystemExit(main())
