#!/usr/bin/env python3
"""Validate GoreeCloud Projects mobile layout, Glaze UI targets, and branding identity."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile
import time

import browser_smoke
import verify_remote

VIEWPORTS=((360,800),(390,844),(412,915))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise browser_smoke.WebDriverError(message)


def set_viewport(session_id: str, width: int, height: int) -> None:
    browser_smoke.webdriver_request(
        "POST",
        f"/session/{session_id}/window/rect",
        {"x":0,"y":0,"width":width,"height":height},
    )


def inspect_mobile(session_id: str, browser: str, width: int) -> None:
    state=browser_smoke.execute(
        session_id,
        """
        const viewport=window.innerWidth;
        const rect=node=>node?node.getBoundingClientRect():null;
        const cards=[...document.querySelectorAll('#projects .card')];
        const filters=[...document.querySelectorAll('#filters .filter')];
        const nav=[...document.querySelectorAll('.topbar nav a')];
        const visibleThemes=[...document.querySelectorAll('.theme-group button')].filter(node=>getComputedStyle(node).display!=='none');
        const foundation=[...document.querySelectorAll('.foundation-strip>a')];
        const mesh=[...foundation].find(node=>node.textContent.includes('GoreeCloud Mesh'));
        return {
          viewport,
          scrollWidth:document.documentElement.scrollWidth,
          bodyScrollWidth:document.body.scrollWidth,
          cardCount:cards.length,
          cardRight:cards.length?Math.max(...cards.map(node=>rect(node).right)):0,
          cardLeft:cards.length?Math.min(...cards.map(node=>rect(node).left)):0,
          filterMinHeight:filters.length?Math.min(...filters.map(node=>rect(node).height)):0,
          navMinHeight:nav.length?Math.min(...nav.map(node=>rect(node).height)):0,
          themeMinHeight:visibleThemes.length?Math.min(...visibleThemes.map(node=>rect(node).height)):0,
          foundationRight:foundation.length?Math.max(...foundation.map(node=>rect(node).right)):0,
          foundationLeft:foundation.length?Math.min(...foundation.map(node=>rect(node).left)):0,
          statusAlign:getComputedStyle(document.querySelector('.card .status')).textAlign,
          cardBackdrop:getComputedStyle(document.querySelector('.card')).backdropFilter || getComputedStyle(document.querySelector('.card')).webkitBackdropFilter || 'none',
          meshArtwork:mesh?.querySelector('img')?.getAttribute('src')||'',
          meshLabel:mesh?.querySelector('small')?.textContent.trim()||'',
          wardveilLabel:document.querySelector('a[href="https://security.goreecloud.com/"] small')?.textContent.trim()||'',
          everkeepStatic:document.querySelector('a[href="https://everkeep.goreecloud.com/"] img')?.getAttribute('src')||'',
        };
        """,
    )
    require(isinstance(state,dict),f"Projects mobile state unreadable in {browser} at {width}px: {state!r}")
    require(int(state.get("scrollWidth",99999))<=int(state.get("viewport",0))+1,f"Projects document overflows horizontally in {browser} at {width}px: {state}")
    require(int(state.get("bodyScrollWidth",99999))<=int(state.get("viewport",0))+1,f"Projects body overflows horizontally in {browser} at {width}px: {state}")
    require(int(state.get("cardCount",0))>=browser_smoke.MIN_PROJECT_CARDS,f"Projects mobile card render incomplete in {browser} at {width}px: {state}")
    require(float(state.get("cardRight",99999))<=int(state.get("viewport",0))+1 and float(state.get("cardLeft",-1))>=-1,f"Projects cards escape the viewport in {browser} at {width}px: {state}")
    require(float(state.get("foundationRight",99999))<=int(state.get("viewport",0))+1 and float(state.get("foundationLeft",-1))>=-1,f"Projects foundation cards escape the viewport in {browser} at {width}px: {state}")
    require(float(state.get("filterMinHeight",0))>=47.5,f"Projects mobile filter targets are below the Glaze UI 2.1 48px floor in {browser} at {width}px: {state}")
    require(float(state.get("navMinHeight",0))>=47.5,f"Projects mobile navigation targets are below the Glaze UI 2.1 48px floor in {browser} at {width}px: {state}")
    require(float(state.get("themeMinHeight",0))>=47.5,f"Projects mobile appearance targets are below the Glaze UI 2.1 48px floor in {browser} at {width}px: {state}")
    require(state.get("statusAlign") in ("left","start"),f"Projects mobile status text is not left-aligned in {browser} at {width}px: {state}")
    require(str(state.get("cardBackdrop","none")) in ("none",""),f"Projects durable mobile cards must remain solid in {browser} at {width}px: {state}")
    require(state.get("meshArtwork")=="/assets/goreecloud-mesh-mark.svg",f"Projects mobile Mesh must use the approved Weave artwork in {browser} at {width}px: {state}")
    require(state.get("meshLabel")=="Mesh Center · Weave",f"Projects mobile Mesh identity label is stale in {browser} at {width}px: {state}")
    require(state.get("wardveilLabel")=="Security Center · Sentinel Fold",f"Projects mobile Wardveil identity label is stale in {browser} at {width}px: {state}")
    require(state.get("everkeepStatic")=="/assets/everkeep.svg",f"Projects mobile Everkeep artwork is incorrect in {browser} at {width}px: {state}")


def inspect_touch_assistance(session_id: str, browser: str, width: int) -> None:
    state=browser_smoke.execute(
        session_id,
        """
        document.documentElement.setAttribute('data-glaze-touch-assistance','true');
        const rect=node=>node?node.getBoundingClientRect():null;
        const filters=[...document.querySelectorAll('#filters .filter')];
        const nav=[...document.querySelectorAll('.topbar nav a')];
        const themes=[...document.querySelectorAll('.theme-group button')].filter(node=>getComputedStyle(node).display!=='none');
        const result={
          filterMinHeight:filters.length?Math.min(...filters.map(node=>rect(node).height)):0,
          navMinHeight:nav.length?Math.min(...nav.map(node=>rect(node).height)):0,
          themeMinHeight:themes.length?Math.min(...themes.map(node=>rect(node).height)):0,
        };
        document.documentElement.removeAttribute('data-glaze-touch-assistance');
        return result;
        """,
    )
    require(isinstance(state,dict),f"Projects Touch Assistance state unreadable in {browser} at {width}px: {state!r}")
    require(float(state.get("filterMinHeight",0))>=55.5,f"Projects filter targets do not reach the 56px Touch Assistance floor in {browser} at {width}px: {state}")
    require(float(state.get("navMinHeight",0))>=55.5,f"Projects navigation targets do not reach the 56px Touch Assistance floor in {browser} at {width}px: {state}")
    require(float(state.get("themeMinHeight",0))>=55.5,f"Projects appearance targets do not reach the 56px Touch Assistance floor in {browser} at {width}px: {state}")


def inspect_identities(session_id: str, browser: str) -> None:
    deadline=time.monotonic()+8
    state=None
    while time.monotonic()<deadline:
        state=browser_smoke.execute(
            session_id,
            """
            const cards=[...document.querySelectorAll('#projects .card')];
            const byName=name=>cards.find(card=>card.querySelector('h3')?.textContent===name);
            const images=[...document.querySelectorAll('#projects .project-icon img')];
            const icon=name=>byName(name)?.querySelector('.project-icon img')?.getAttribute('src')||'';
            const iconAbsolute=name=>byName(name)?.querySelector('.project-icon img')?.src||'';
            const noIcon=name=>Boolean(byName(name))&&!byName(name).querySelector('.project-icon');
            return {
              total:images.length,
              loaded:images.filter(img=>img.complete&&img.naturalWidth>0).length,
              generic:images.filter(img=>new URL(img.src).pathname==='/assets/goreecloud-logo.svg').length,
              suite:images.filter(img=>img.src.startsWith('https://www.goreecloud.com/assets/suite/')).length,
              glaze:icon('Glaze UI'),
              privacy:icon('GoreeCloud Privacy Shield'),
              wardveil:icon('Wardveil Security'),
              everkeep:icon('Everkeep'),
              mesh:icon('GoreeCloud Mesh'),
              suiteNoIcon:noIcon('GoreeCloud Suite'),
              githubDashboardNoIcon:noIcon('GoreeCloud GitHub Dashboard'),
              waypointNoIcon:noIcon('GoreeCloud Waypoint'),
              manager:iconAbsolute('GoreeCloud Manager'),
              browser:iconAbsolute('GoreeCloud Browser'),
              generatedData:images.filter(img=>img.src.startsWith('data:')).length,
            };
            """,
        )
        if isinstance(state,dict) and int(state.get("loaded",0))==int(state.get("total",-1)):
            break
        time.sleep(.25)
    require(isinstance(state,dict),f"Projects icon state unreadable in {browser}: {state!r}")
    require(int(state.get("loaded",0))==int(state.get("total",-1)),f"Projects contains unloaded approved branding artwork in {browser}: {state}")
    require(int(state.get("generic",99))==0,f"Projects still applies the GoreeCloud platform logo to repository cards in {browser}: {state}")
    require(int(state.get("generatedData",99))==0,f"Projects still generates unapproved data-URI artwork in {browser}: {state}")
    require(int(state.get("suite",0))>=30,f"Projects did not load the approved per-product publication derivatives in {browser}: {state}")
    require(state.get("glaze")=="/assets/glaze-ui-mark.svg",f"Projects Glaze UI card uses the wrong artwork in {browser}: {state}")
    require(state.get("privacy")=="/assets/privacy-shield-icon.svg",f"Projects Privacy Shield card uses the wrong artwork in {browser}: {state}")
    require(state.get("wardveil")=="/assets/wardveil-security-icon.svg",f"Projects Wardveil card uses the wrong artwork in {browser}: {state}")
    require(state.get("everkeep")=="/assets/everkeep.svg",f"Projects Everkeep card uses the wrong artwork in {browser}: {state}")
    require(state.get("mesh")=="/assets/goreecloud-mesh-mark.svg",f"Projects Mesh card uses the wrong artwork in {browser}: {state}")
    for field in ("suiteNoIcon","githubDashboardNoIcon","waypointNoIcon"):
        require(state.get(field) is True,f"Projects entry without approved catalog artwork must be text-only ({field}) in {browser}: {state}")
    require("/assets/suite/manager.svg" in str(state.get("manager","")),f"Projects Manager card is not using its approved derivative in {browser}: {state}")
    require("/assets/suite/browser.svg" in str(state.get("browser","")),f"Projects Browser card is not using its approved derivative in {browser}: {state}")


def run(target: str,browser: str) -> int:
    target_url=verify_remote.target_url(target)
    verify_remote.validate_url(target_url)
    port=browser_smoke.DRIVER_PORTS[browser]
    browser_smoke.DRIVER_BASE=f"http://{browser_smoke.DRIVER_HOST}:{port}"
    process=None
    session_id=None
    log_path=None
    try:
        with tempfile.NamedTemporaryFile(prefix=f"projects-mobile-{browser}-",suffix=".log",delete=False) as log_file:
            log_path=log_file.name
            process=subprocess.Popen(browser_smoke.driver_command(browser,port),stdout=log_file,stderr=subprocess.STDOUT)
        browser_smoke.wait_for_driver(browser)
        session_id=browser_smoke.create_session(browser)
        browser_smoke.webdriver_request("POST",f"/session/{session_id}/timeouts",{"implicit":0,"pageLoad":15000,"script":10000})
        set_viewport(session_id,*VIEWPORTS[0])
        browser_smoke.webdriver_request("POST",f"/session/{session_id}/url",{"url":target_url})
        inspect_identities(session_id,browser)
        for width,height in VIEWPORTS:
            set_viewport(session_id,width,height)
            time.sleep(.2)
            inspect_mobile(session_id,browser,width)
            inspect_touch_assistance(session_id,browser,width)
        print(f"Projects mobile {browser} branding/layout/Glaze UI 2.1 smoke passed for {target}: {target_url}")
        return 0
    except (browser_smoke.WebDriverError,OSError,ValueError) as error:
        print(f"Projects mobile {browser} branding/layout smoke failed for {target}: {target_url}")
        print(f"- {error}")
        if log_path:
            try:
                log_text=Path(log_path).read_text(encoding="utf-8",errors="replace")
            except OSError:
                log_text=""
            if log_text:
                print(log_text[-8000:])
        return 1
    finally:
        if session_id:
            try: browser_smoke.webdriver_request("DELETE",f"/session/{session_id}")
            except browser_smoke.WebDriverError: pass
        if process:
            process.terminate()
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill();process.wait(timeout=5)
        if log_path:
            try: Path(log_path).unlink()
            except OSError: pass
        browser_smoke.DRIVER_BASE=""


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--target",choices=("branch-preview","production"),required=True)
    parser.add_argument("--browser",choices=("chrome","firefox"),required=True)
    args=parser.parse_args()
    return run(args.target,args.browser)


if __name__=="__main__":
    raise SystemExit(main())
