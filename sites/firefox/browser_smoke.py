#!/usr/bin/env python3
"""Exercise the exact built Firefox showcase using the shared simple-static browser contract."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import browser_simple_static_site as smoke  # noqa: E402
from simple_static_publication import resolve_site  # noqa: E402

WEB_PORT = 8784


def main() -> int:
    spec = resolve_site("firefox")
    dist = REPO / spec.path / "dist"
    smoke.require(dist.is_dir() and (dist / "index.html").is_file(), "firefox dist/ is missing; build exact artifact first")
    url = f"http://127.0.0.1:{WEB_PORT}/"
    server: subprocess.Popen[bytes] | None = None
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: Path | None = None
    try:
        server = subprocess.Popen(
            ["python3", "-m", "http.server", str(WEB_PORT), "--bind", "127.0.0.1", "--directory", str(dist)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        smoke.wait_http(url)
        with tempfile.NamedTemporaryFile(prefix="goreecloud-firefox-chromedriver-", suffix=".log", delete=False) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen(
                [smoke.chromedriver(), f"--port={smoke.DRIVER_PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        smoke.wait_for_driver()
        session_id = smoke.create_session()
        smoke.exercise(session_id, url, spec.title, spec.canonical_host)
        print("firefox built-artifact Chrome acceptance passed at 1180×900, 768×900, 390×844, and 320×844.")
        return 0
    except Exception as error:
        print(f"firefox built-artifact Chrome acceptance failed: {error}")
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
                smoke.driver_request("DELETE", f"/session/{session_id}")
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
