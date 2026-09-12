#!/usr/bin/env python3
"""Exercise the exact built GoreeCloud Main artifact in headless Chrome."""

from __future__ import annotations

from pathlib import Path
import subprocess
import time
from urllib.error import URLError
from urllib.request import urlopen

import browser_responsive_smoke as smoke
from build_public_site import DIST

WEB_HOST = "127.0.0.1"
WEB_PORT = 8770
TARGET = f"http://{WEB_HOST}:{WEB_PORT}/"


def wait_http(timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    last: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urlopen(TARGET, timeout=1) as response:
                if response.status == 200:
                    return
        except (URLError, TimeoutError, OSError) as error:
            last = error
        time.sleep(0.1)
    raise smoke.BrowserError(f"local Main artifact server did not become ready: {last}")


def main() -> int:
    smoke.require(DIST.is_dir() and (DIST / "index.html").is_file(), "Main dist/ artifact is missing; run build first")
    server: subprocess.Popen[bytes] | None = None
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: Path | None = None
    try:
        server = subprocess.Popen(
            ["python3", "-m", "http.server", str(WEB_PORT), "--bind", WEB_HOST, "--directory", str(DIST)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        wait_http()

        import tempfile

        with tempfile.NamedTemporaryFile(prefix="goreecloud-main-artifact-chromedriver-", suffix=".log", delete=False) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen(
                [smoke.chromedriver(), f"--port={smoke.PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        smoke.wait_for_driver()
        session_id = smoke.create_session()
        smoke.exercise(session_id, TARGET)
        print(
            "Main built-artifact responsive Chrome smoke passed at 1180×900, 768×900, 390×844, and 320×844, including bounded mobile navigation."
        )
        return 0
    except Exception as error:
        print(f"Main built-artifact responsive Chrome smoke failed: {error}")
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
                smoke.request("DELETE", f"/session/{session_id}")
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
