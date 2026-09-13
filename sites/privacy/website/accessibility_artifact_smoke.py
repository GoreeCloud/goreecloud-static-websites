#!/usr/bin/env python3
"""Automated accessibility smoke for the exact built Privacy Center artifact.

This verifies browser accessibility semantics and selected user-preference behavior.
It is not screen-reader, assistive-technology, device, or human accessibility
acceptance and cannot promote the Privacy Center or Privacy Shield lifecycle.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile

import browser_artifact_smoke as browser


def require(condition: bool, message: str) -> None:
    if not condition:
        raise browser.BrowserError(message)


def cdp(session_id: str, cmd: str, params: dict | None = None):
    return browser.request(
        "POST",
        f"/session/{session_id}/goog/cdp/execute",
        {"cmd": cmd, "params": params or {}},
    )


def validate_accessibility_tree(session_id: str) -> None:
    tree = cdp(session_id, "Accessibility.getFullAXTree")
    require(isinstance(tree, dict), f"Chrome did not return an accessibility tree: {tree!r}")
    nodes = tree.get("nodes") or []
    require(nodes, "Privacy Center accessibility tree is empty")

    roles: set[str] = set()
    named: list[tuple[str, str]] = []
    for node in nodes:
        role = ((node.get("role") or {}).get("value") or "") if isinstance(node, dict) else ""
        name = ((node.get("name") or {}).get("value") or "") if isinstance(node, dict) else ""
        if role:
            roles.add(str(role))
        if role and name:
            named.append((str(role), str(name)))

    for required_role in ("RootWebArea", "banner", "navigation", "main", "contentinfo", "heading", "link", "button"):
        require(required_role in roles, f"Privacy Center accessibility tree missing role {required_role!r}; roles={sorted(roles)}")

    names = {name for _, name in named}
    require("GoreeCloud Privacy Center — Privacy Shield" in names, "Privacy Center accessible root name drifted")
    require("Privacy authorization that travels with the operation." in names, "Privacy Center primary heading is missing from accessibility tree")
    require("Primary" in names, "Privacy Center primary navigation lacks an accessible name")
    require(
        any(role == "button" and name.startswith("Appearance: System.") for role, name in named),
        f"Privacy Center appearance control lacks its expected accessible name: {named}",
    )


def validate_focus_contract(session_id: str) -> None:
    state = browser.execute(
        session_id,
        """
        const candidates=[...document.querySelectorAll('a[href],button,[tabindex]')]
          .filter(el=>!el.hasAttribute('disabled')&&el.getAttribute('tabindex')!=='-1');
        const summary=candidates.map(el=>({tag:el.tagName.toLowerCase(),cls:el.className||'',text:(el.textContent||'').trim(),aria:el.getAttribute('aria-label')||'',href:el.getAttribute('href')||''}));
        const unnamed=summary.filter(x=>!(x.aria||x.text));
        return {first:summary[0]||null,unnamed,count:summary.length,theme:summary.find(x=>x.cls.includes('theme-button'))||null};
        """,
    )
    require(isinstance(state, dict), f"Could not read Privacy Center focus contract: {state!r}")
    first = state.get("first") or {}
    require("skip-link" in (first.get("cls") or ""), f"Privacy Center skip link is not first in focus order: {state}")
    require(not (state.get("unnamed") or []), f"Privacy Center has unnamed focusable controls: {state}")
    theme = state.get("theme") or {}
    require((theme.get("aria") or "").startswith("Appearance: System."), f"Privacy Center appearance button is not descriptively named: {state}")


def validate_reduced_motion(session_id: str) -> None:
    cdp(
        session_id,
        "Emulation.setEmulatedMedia",
        {"features": [{"name": "prefers-reduced-motion", "value": "reduce"}]},
    )
    state = browser.execute(
        session_id,
        """
        const b=document.querySelector('.theme-button');
        const style=getComputedStyle(b);
        return {matches:matchMedia('(prefers-reduced-motion: reduce)').matches,scroll:getComputedStyle(document.documentElement).scrollBehavior,transition:style.transitionDuration,animation:style.animationDuration};
        """,
    )
    require(isinstance(state, dict) and state.get("matches") is True, f"Chrome did not apply reduced-motion emulation: {state}")
    require(state.get("scroll") == "auto", f"Privacy Center smooth scrolling remains enabled under reduced motion: {state}")


def validate_increased_contrast(session_id: str) -> None:
    cdp(
        session_id,
        "Emulation.setEmulatedMedia",
        {"features": [{"name": "prefers-contrast", "value": "more"}]},
    )
    state = browser.execute(
        session_id,
        """
        const card=document.querySelector('.glass-card');
        const status=document.querySelector('.status-row span');
        const cr=parseFloat(getComputedStyle(card).borderTopWidth)||0;
        const sr=parseFloat(getComputedStyle(status).borderTopWidth)||0;
        return {matches:matchMedia('(prefers-contrast: more)').matches,cardBorder:cr,statusBorder:sr};
        """,
    )
    require(isinstance(state, dict) and state.get("matches") is True, f"Chrome did not apply increased-contrast emulation: {state}")
    require(float(state.get("cardBorder", 0)) >= 2 and float(state.get("statusBorder", 0)) >= 2, f"Privacy Center increased-contrast borders did not strengthen: {state}")


def main() -> int:
    require(browser.DIST.is_dir() and (browser.DIST / "index.html").is_file(), "Privacy Center dist/ is missing; run build.py first")
    server: subprocess.Popen[bytes] | None = None
    driver: subprocess.Popen[bytes] | None = None
    session_id: str | None = None
    log_path: Path | None = None
    try:
        server = subprocess.Popen(
            ["python3", "-m", "http.server", str(browser.WEB_PORT), "--bind", browser.WEB_HOST, "--directory", str(browser.DIST)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        browser.wait_http()
        with tempfile.NamedTemporaryFile(prefix="goreecloud-privacy-a11y-chromedriver-", suffix=".log", delete=False) as log_file:
            log_path = Path(log_file.name)
            driver = subprocess.Popen(
                [browser.chromedriver(), f"--port={browser.DRIVER_PORT}", "--allowed-ips=127.0.0.1"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        browser.wait_for_driver()
        session_id = browser.create_session()
        browser.request("POST", f"/session/{session_id}/timeouts", {"implicit": 0, "pageLoad": 15000, "script": 10000})
        browser.navigate(session_id, browser.TARGET)
        validate_accessibility_tree(session_id)
        validate_focus_contract(session_id)
        validate_reduced_motion(session_id)
        validate_increased_contrast(session_id)
        print("Privacy Center automated accessibility artifact smoke passed; assistive-technology/device/human acceptance remains separate.")
        return 0
    except Exception as error:
        print(f"Privacy Center automated accessibility artifact smoke failed: {error}")
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
                browser.request("DELETE", f"/session/{session_id}")
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
