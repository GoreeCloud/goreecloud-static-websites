#!/usr/bin/env python3
"""Exercise a governed canonical simple-static production site in headless Chrome."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile

import browser_simple_static_site as smoke
from simple_static_publication import resolve_site
import verify_simple_static_deployment as remote


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site")
    args = parser.parse_args()
    spec = resolve_site(args.site)
    url = remote.target_url(spec, "production")
    remote.validate_url(spec, url)

    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=f"goreecloud-{spec.site_id}-production-chromedriver-", suffix=".log", delete=False) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen(
                [smoke.chromedriver(), f"--port={smoke.DRIVER_PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        smoke.wait_for_driver()
        session_id = smoke.create_session()
        smoke.exercise(session_id, url, spec.title, spec.canonical_host)
        print(f"{spec.site_id} canonical production Chrome acceptance passed at 1180×900, 768×900, 390×844, and 320×844.")
        return 0
    except Exception as error:
        print(f"{spec.site_id} canonical production Chrome acceptance failed: {error}")
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
