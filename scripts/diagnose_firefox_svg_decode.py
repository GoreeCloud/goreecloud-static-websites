#!/usr/bin/env python3
"""Diagnose SVG decoding for the selected Firefox publication without mutating production."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ORIGIN = os.environ.get("FIREFOX_VERIFY_ORIGIN", "https://www.goreecloud.com").rstrip("/")
PAGE = ORIGIN + "/firefox-extensions/"
ASSET = PAGE + "assets/goreecloud-logo.svg"
PORT = 9541
BASE = f"http://127.0.0.1:{PORT}"
TIMEOUT = 20


class DiagnosticError(RuntimeError):
    pass


def request(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(
        BASE + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            raw = response.read()
    except HTTPError as error:
        raise DiagnosticError(f"WebDriver HTTP {error.code}: {error.read().decode('utf-8', errors='replace')}") from error
    except (URLError, TimeoutError) as error:
        raise DiagnosticError(f"WebDriver request failed: {error}") from error
    if not raw:
        return None
    value = json.loads(raw.decode("utf-8")).get("value")
    if isinstance(value, dict) and value.get("error"):
        raise DiagnosticError(f"WebDriver {value.get('error')}: {value.get('message', '')}")
    return value


def chromedriver() -> str:
    for candidate in (shutil.which("chromedriver"), "/usr/local/share/chromedriver-linux64/chromedriver"):
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise DiagnosticError("chromedriver is unavailable")


def wait_for_driver() -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        try:
            status = request("GET", "/status")
            if isinstance(status, dict) and status.get("ready"):
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise DiagnosticError("chromedriver did not become ready")


def main() -> int:
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="goreecloud-firefox-svg-diagnostic-", suffix=".log", delete=False) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen(
                [chromedriver(), f"--port={PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        wait_for_driver()
        value = request(
            "POST",
            "/session",
            {
                "capabilities": {
                    "alwaysMatch": {
                        "browserName": "chrome",
                        "goog:chromeOptions": {
                            "args": [
                                "--headless=new",
                                "--no-sandbox",
                                "--disable-dev-shm-usage",
                                "--no-first-run",
                                "--window-size=900,700",
                            ]
                        },
                    }
                }
            },
        )
        if not isinstance(value, dict) or not value.get("sessionId"):
            raise DiagnosticError(f"Chrome session creation failed: {value!r}")
        session_id = str(value["sessionId"])
        request("POST", f"/session/{session_id}/timeouts", {"pageLoad": 20000, "script": 15000})
        request("POST", f"/session/{session_id}/url", {"url": PAGE})
        result = request(
            "POST",
            f"/session/{session_id}/execute/async",
            {
                "script": r"""
                const done = arguments[arguments.length - 1];
                const asset = document.querySelector('img[src="assets/goreecloud-logo.svg"]')?.currentSrc || location.href + 'assets/goreecloud-logo.svg';
                const decode = async src => {
                  const img = new Image();
                  img.width = 32; img.height = 32; img.src = src;
                  document.body.appendChild(img);
                  try {
                    await img.decode();
                    const out = {ok:true, complete:img.complete, naturalWidth:img.naturalWidth, naturalHeight:img.naturalHeight, currentSrc:img.currentSrc};
                    img.remove(); return out;
                  } catch (error) {
                    const out = {ok:false, complete:img.complete, naturalWidth:img.naturalWidth, naturalHeight:img.naturalHeight, currentSrc:img.currentSrc, error:String(error)};
                    img.remove(); return out;
                  }
                };
                (async () => {
                  const minimalText = '<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2" viewBox="0 0 2 2"><rect width="2" height="2" fill="red"/></svg>';
                  const minimal = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(minimalText);
                  let response, text, headers = {}, fetchError = '';
                  try {
                    response = await fetch(asset, {cache:'no-store'});
                    for (const [k,v] of response.headers.entries()) headers[k]=v;
                    text = await response.text();
                  } catch (error) {
                    fetchError = String(error); text = '';
                  }
                  const parser = new DOMParser().parseFromString(text || '<svg/>', 'image/svg+xml');
                  const parserError = parser.querySelector('parsererror')?.textContent || '';
                  const reloaded = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(text);
                  const direct = await decode(asset);
                  const fetchedBytesAsData = text ? await decode(reloaded) : {ok:false,error:'fetch produced no text'};
                  const minimalData = await decode(minimal);
                  done({asset, fetchStatus:response?.status || 0, fetchError, headers, byteLength:new TextEncoder().encode(text).length, prefix:text.slice(0,160), parserError, direct, fetchedBytesAsData, minimalData});
                })().catch(error => done({fatal:String(error)}));
                """,
                "args": [],
            },
        )
        print("Firefox SVG decode diagnostic:")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as error:
        print(f"Firefox SVG diagnostic failed to execute: {error}")
        return 1
    finally:
        if session_id:
            try:
                request("DELETE", f"/session/{session_id}")
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
