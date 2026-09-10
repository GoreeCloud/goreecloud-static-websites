#!/usr/bin/env python3
"""Exercise GoreeCloud Projects in a real headless browser session.

The smoke test uses only Python's standard library plus browser/WebDriver binaries
available on the GitHub runner. It validates the current GLAZE UI V1.3 publication,
the authoritative 45-product Suite projection, local search/filter behavior, and
renderer health without claiming production acceptance.
"""

from __future__ import annotations

import argparse
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

import verify_remote

DRIVER_HOST = "127.0.0.1"
DRIVER_PORTS = {"chrome": 9515, "firefox": 9516}
DRIVER_BASE = ""
HTTP_TIMEOUT = 20
FIREFOX_SESSION_TIMEOUT = 45
STARTUP_TIMEOUT = 15
MIN_PROJECT_CARDS = 45
EXPECTED_SUITE_PRODUCTS = 45
MAX_STRESS_LOOP_MS = 5_000


class WebDriverError(RuntimeError):
    pass


def executable_from_env_or_path(browser: str) -> str:
    if browser == "chrome":
        env_name = "CHROMEWEBDRIVER"
        binary_name = "chromedriver"
        fallback = Path("/usr/local/share/chromedriver-linux64/chromedriver")
    else:
        env_name = "GECKOWEBDRIVER"
        binary_name = "geckodriver"
        fallback = Path("/usr/local/share/gecko_driver/geckodriver")

    candidates: list[Path] = []
    env_path = os.environ.get(env_name)
    if env_path:
        path = Path(env_path)
        candidates.append(path / binary_name if path.is_dir() else path)
    found = shutil.which(binary_name)
    if found:
        candidates.append(Path(found))
    candidates.append(fallback)

    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    raise WebDriverError(f"{binary_name} is unavailable on the runner.")


def webdriver_request(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    *,
    timeout: int = HTTP_TIMEOUT,
) -> Any:
    if not DRIVER_BASE:
        raise WebDriverError("WebDriver endpoint has not been initialized.")
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{DRIVER_BASE}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as error:
        raw = error.read()
        try:
            detail = json.loads(raw.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            detail = raw.decode("utf-8", errors="replace")
        raise WebDriverError(f"WebDriver HTTP {error.code} for {path}: {detail}") from error
    except (URLError, TimeoutError) as error:
        raise WebDriverError(f"WebDriver request failed for {path}: {error}") from error

    if not raw:
        return None
    response = json.loads(raw.decode("utf-8"))
    value = response.get("value")
    if isinstance(value, dict) and value.get("error"):
        raise WebDriverError(
            f"WebDriver {value.get('error')} for {path}: {value.get('message', 'unknown error')}"
        )
    return value


def wait_for_driver(browser: str) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            status = webdriver_request("GET", "/status")
            if isinstance(status, dict) and status.get("ready"):
                return
        except (WebDriverError, json.JSONDecodeError) as error:
            last_error = error
        time.sleep(0.2)
    raise WebDriverError(f"{browser} WebDriver did not become ready: {last_error}")


def create_session(browser: str) -> str:
    if browser == "chrome":
        always_match: dict[str, Any] = {
            "browserName": "chrome",
            "goog:chromeOptions": {
                "args": [
                    "--headless=new",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-background-networking",
                    "--disable-component-update",
                    "--disable-default-apps",
                    "--disable-extensions",
                    "--disable-sync",
                    "--metrics-recording-only",
                    "--no-first-run",
                    "--window-size=1440,1200",
                ]
            },
        }
        session_timeout = HTTP_TIMEOUT
    else:
        always_match = {
            "browserName": "firefox",
            "moz:firefoxOptions": {
                "args": ["-headless"],
                "prefs": {
                    "browser.shell.checkDefaultBrowser": False,
                    "browser.startup.homepage_override.mstone": "ignore",
                    "datareporting.policy.dataSubmissionEnabled": False,
                    "toolkit.telemetry.enabled": False,
                },
            },
        }
        session_timeout = FIREFOX_SESSION_TIMEOUT

    value = webdriver_request(
        "POST",
        "/session",
        {"capabilities": {"alwaysMatch": always_match}},
        timeout=session_timeout,
    )
    if not isinstance(value, dict):
        raise WebDriverError(f"Unexpected {browser} WebDriver session response: {value!r}")
    session_id = value.get("sessionId")
    if not isinstance(session_id, str) or not session_id:
        raise WebDriverError(f"{browser} WebDriver did not return a session id: {value!r}")
    return session_id


def execute(session_id: str, script: str) -> Any:
    return webdriver_request(
        "POST",
        f"/session/{session_id}/execute/sync",
        {"script": script, "args": []},
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WebDriverError(message)


def exercise_page(session_id: str, target_url: str, browser: str) -> None:
    webdriver_request(
        "POST",
        f"/session/{session_id}/timeouts",
        {"implicit": 0, "pageLoad": 15_000, "script": 10_000},
    )
    webdriver_request("POST", f"/session/{session_id}/url", {"url": target_url})

    initial = execute(
        session_id,
        """
        const card=document.querySelector('#projects .card');
        const cardStyle=card?getComputedStyle(card):null;
        return {
          ready:document.readyState,
          title:document.title,
          cards:document.querySelectorAll('#projects .card').length,
          result:document.querySelector('#result-count')?.textContent||'',
          resources:performance.getEntriesByType('resource').map(entry=>entry.name),
          glazeVersion:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',
          suiteCount:document.querySelector('#app-count')?.textContent||'',
          platformCount:document.querySelector('#foundation-count')?.textContent||'',
          suiteFilter:Boolean([...document.querySelectorAll('#filters .filter')].find(node=>node.textContent.trim()==='Suite products')),
          cardBackdrop:cardStyle?.backdropFilter||cardStyle?.webkitBackdropFilter||'none',
        };
        """,
    )
    require(isinstance(initial, dict), f"Projects runtime state was not readable in {browser}: {initial!r}")
    require(initial.get("ready") == "complete", f"Projects document did not finish loading in {browser}: {initial}")
    require(initial.get("title") == "Projects — GoreeCloud", f"Unexpected Projects title in {browser}: {initial.get('title')!r}")
    require(int(initial.get("cards", 0)) >= MIN_PROJECT_CARDS, f"Projects rendered too few cards in {browser}: {initial}")
    require(initial.get("glazeVersion") == "1.3.0", f"Projects did not expose the Glaze UI V1.3 document contract in {browser}: {initial}")
    require(initial.get("suiteCount") == "45", f"Projects did not expose the authoritative 45-product Suite count in {browser}: {initial}")
    require(initial.get("platformCount") == "7", f"Projects did not expose the seven Integral Platform Systems in {browser}: {initial}")
    require(initial.get("suiteFilter") is True, f"Projects Suite products filter is missing in {browser}: {initial}")
    require(str(initial.get("cardBackdrop", "none")) in ("none", ""), f"Durable Projects content cards must remain solid under Glaze UI V1.3 in {browser}: {initial}")

    resources = initial.get("resources") or []
    require(any("/assets/app.js?v=20260910-v13" in resource for resource in resources), f"Headless {browser} did not load the Projects app.js V1.3 resource.")
    require(any("/assets/suite-portfolio.js?v=20260910-v45" in resource for resource in resources), f"Headless {browser} did not load the authoritative Suite portfolio projection.")
    require(any("/assets/icon-refresh.js?v=20260910-portfolio45" in resource for resource in resources), f"Headless {browser} did not load the reconciled Projects branding resource.")
    require(any("/assets/glaze-v1.3-consumer.css?v=20260910-v13" in resource for resource in resources), f"Headless {browser} did not load the Glaze UI V1.3 consumer layer.")
    require(not any("/assets/public-refresh.js" in resource for resource in resources), f"Headless {browser} still loaded the superseded Projects public-refresh overlay.")
    require(not any("glaze-ui-2.1.0.css" in resource or "glaze-ui-2.0.0.css" in resource for resource in resources), f"Headless {browser} loaded a superseded Glaze stylesheet.")

    searched = execute(
        session_id,
        """
        const input=document.querySelector('#search');
        if(!input)throw new Error('Projects search input is missing');
        input.value='GoreeCloud Health';
        input.dispatchEvent(new Event('input',{bubbles:true}));
        return {
          cards:document.querySelectorAll('#projects .card').length,
          names:[...document.querySelectorAll('#projects .card h3')].map(node=>node.textContent.trim()),
        };
        """,
    )
    require(isinstance(searched, dict), f"Projects search did not return state in {browser}: {searched!r}")
    require("GoreeCloud Health" in (searched.get("names") or []), f"Projects search failed to retain GoreeCloud Health in {browser}: {searched}")

    suite = execute(
        session_id,
        """
        const input=document.querySelector('#search');
        input.value='';
        input.dispatchEvent(new Event('input',{bubbles:true}));
        const button=[...document.querySelectorAll('#filters .filter')].find(node=>node.textContent.trim()==='Suite products');
        if(!button)throw new Error('Suite products filter is missing');
        button.click();
        const cards=[...document.querySelectorAll('#projects .card')];
        return {
          cards:cards.length,
          suiteFlags:cards.map(card=>card.dataset.suiteMember),
          names:cards.map(card=>card.querySelector('h3')?.textContent.trim()||''),
        };
        """,
    )
    require(isinstance(suite, dict), f"Projects Suite filter did not return state in {browser}: {suite!r}")
    require(int(suite.get("cards", 0)) == EXPECTED_SUITE_PRODUCTS, f"Suite filter must render exactly 45 products in {browser}: {suite}")
    require(all(flag == "true" for flag in (suite.get("suiteFlags") or [])), f"Suite filter leaked a non-Suite entry in {browser}: {suite}")
    for name in ("GoreeCloud Index", "GoreeVault", "GoreeCloud Health", "GoreeCloud Reader", "GoreeCloud Router OS", "GoreeCloud Social", "GoreeCloud Home", "GoreeCloud Home Security"):
        require(name in (suite.get("names") or []), f"Suite filter is missing {name} in {browser}: {suite}")

    foundations = execute(
        session_id,
        """
        const button=[...document.querySelectorAll('#filters .filter')].find(node=>node.textContent.trim()==='Foundations');
        if(!button)throw new Error('Foundations filter is missing');
        button.click();
        const cards=[...document.querySelectorAll('#projects .card')];
        return {cards:cards.length,kinds:cards.map(card=>card.dataset.kind)};
        """,
    )
    require(isinstance(foundations, dict), f"Projects filter did not return state in {browser}: {foundations!r}")
    require(int(foundations.get("cards", 0)) >= 1, f"Foundations filter rendered no cards in {browser}: {foundations}")
    require(all(kind == "foundation" for kind in (foundations.get("kinds") or [])), f"Foundations filter leaked non-foundation cards in {browser}: {foundations}")

    stressed = execute(
        session_id,
        """
        const input=document.querySelector('#search');
        const buttons=[...document.querySelectorAll('#filters .filter')];
        const all=buttons.find(node=>node.textContent.trim()==='All');
        if(!input||!buttons.length||!all)throw new Error('Projects controls are incomplete');
        const start=performance.now();
        for(let i=0;i<60;i+=1){
          input.value=i%3===0?'GoreeCloud':(i%3===1?'Native':'');
          input.dispatchEvent(new Event('input',{bubbles:true}));
          buttons[i%buttons.length].click();
        }
        input.value='';
        input.dispatchEvent(new Event('input',{bubbles:true}));
        all.click();
        return {elapsed:performance.now()-start,cards:document.querySelectorAll('#projects .card').length,ping:42};
        """,
    )
    require(isinstance(stressed, dict), f"Projects stress exercise did not return state in {browser}: {stressed!r}")
    require(stressed.get("ping") == 42, f"Projects renderer stopped responding in {browser}: {stressed}")
    require(int(stressed.get("cards", 0)) >= MIN_PROJECT_CARDS, f"Projects did not recover after repeated interactions in {browser}: {stressed}")
    require(float(stressed.get("elapsed", MAX_STRESS_LOOP_MS + 1)) <= MAX_STRESS_LOOP_MS, f"Projects repeated render loop was unexpectedly slow in {browser}: {stressed}")


def driver_command(browser: str, port: int) -> list[str]:
    binary = executable_from_env_or_path(browser)
    if browser == "chrome":
        return [binary, f"--port={port}", "--allowed-ips=127.0.0.1"]
    return [binary, "--host", DRIVER_HOST, "--port", str(port)]


def run(target: str, browser: str) -> int:
    global DRIVER_BASE
    target_url = verify_remote.target_url(target)
    verify_remote.validate_url(target_url)
    port = DRIVER_PORTS[browser]
    DRIVER_BASE = f"http://{DRIVER_HOST}:{port}"
    log_path: str | None = None
    process: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=f"projects-{browser}-webdriver-", suffix=".log", delete=False) as log_file:
            log_path = log_file.name
            process = subprocess.Popen(driver_command(browser, port), stdout=log_file, stderr=subprocess.STDOUT)
        wait_for_driver(browser)
        session_id = create_session(browser)
        exercise_page(session_id, target_url, browser)
        print(f"Projects headless {browser} Glaze UI V1.3 / Suite-45 smoke passed for {target}: {target_url}")
        return 0
    except (WebDriverError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Projects headless {browser} runtime smoke failed for {target}: {target_url}")
        print(f"- {error}")
        if log_path:
            try:
                log_text = Path(log_path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                log_text = ""
            if log_text:
                print(f"{browser} WebDriver log:")
                print(log_text[-8_000:])
        return 1
    finally:
        if session_id:
            try:
                webdriver_request("DELETE", f"/session/{session_id}")
            except WebDriverError:
                pass
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if log_path:
            try:
                Path(log_path).unlink()
            except OSError:
                pass
        DRIVER_BASE = ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("branch-preview", "production"), required=True)
    parser.add_argument("--browser", choices=("chrome", "firefox"), required=True)
    args = parser.parse_args()
    return run(args.target, args.browser)


if __name__ == "__main__":
    raise SystemExit(main())
