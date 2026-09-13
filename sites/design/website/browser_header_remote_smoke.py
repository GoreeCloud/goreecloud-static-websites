#!/usr/bin/env python3
"""Verify the canonical live Design Center keeps the full wide-desktop identity visible."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile

import browser_artifact_smoke as smoke
import browser_header_smoke as header_smoke
import verify_remote


def main() -> int:
    target = verify_remote.target_url("production")
    verify_remote.validate_url(target)
    smoke.TARGET = target

    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix="goreecloud-design-production-header-chromedriver-",
            suffix=".log",
            delete=False,
        ) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen(
                [smoke.chromedriver(), f"--port={smoke.DRIVER_PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        smoke.wait_for_driver()
        session_id = smoke.create_session()
        header_smoke.exercise(session_id)
        print(
            "Design Center canonical production wide-header acceptance passed at "
            "1440×900 with the full GoreeCloud · Design Center · GLAZE UI identity visible "
            "and separated from navigation and appearance controls."
        )
        return 0
    except Exception as error:
        print(f"Design Center canonical production wide-header acceptance failed: {error}")
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
                smoke.request("DELETE", f"/session/{session_id}")
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
                log_path.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
