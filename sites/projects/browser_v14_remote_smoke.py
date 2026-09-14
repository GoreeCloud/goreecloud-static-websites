#!/usr/bin/env python3
"""Exercise the canonical Projects V1.4 production surface in Chrome after exact deployment verification."""
from __future__ import annotations
from pathlib import Path
import subprocess,tempfile,time
import browser_smoke,mobile_smoke
import verify_v14_deployment as remote
VIEWPORTS=((1180,900),(768,900),(390,844),(320,844))
REV='84cb3db4884042f0fa25ed6d475a127fb110f596'
def inspect(sid,width):
    state=browser_smoke.execute(sid,"""
    const vis=n=>{const s=getComputedStyle(n),r=n.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};
    const ctrls=[...document.querySelectorAll('.topbar nav a,.theme-group button,.filter,.glaze-button,.card footer a')].filter(vis);
    return {ready:document.readyState,title:document.title,glaze:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',rev:document.querySelector('meta[name="goreecloud-glaze-source-revision"]')?.content||'',suite:document.querySelector('#app-count')?.textContent||'',systems:document.querySelector('#foundation-count')?.textContent||'',scroll:document.documentElement.scrollWidth,body:document.body.scrollWidth,width:window.innerWidth,cards:document.querySelectorAll('#projects .card').length,min:ctrls.length?Math.min(...ctrls.map(n=>n.getBoundingClientRect().height)):0,resources:performance.getEntriesByType('resource').map(e=>e.name),broken:[...document.images].filter(i=>!i.complete||i.naturalWidth<=0).map(i=>i.src)};
    """)
    browser_smoke.require(state.get('ready')=='complete',f'Projects production V1.4 not ready at {width}: {state}')
    browser_smoke.require(state.get('title')=='Projects — GoreeCloud',f'Projects production title drift: {state}')
    browser_smoke.require(state.get('glaze')=='1.4.0' and state.get('rev')==REV,f'Projects production V1.4 identity drift at {width}: {state}')
    browser_smoke.require(state.get('suite')=='45' and state.get('systems')=='7',f'Projects production portfolio counts drift: {state}')
    browser_smoke.require(int(state.get('cards',0))>=browser_smoke.MIN_PROJECT_CARDS,f'Projects production cards incomplete: {state}')
    viewport=int(state.get('width',0));browser_smoke.require(int(state.get('scroll',99999))<=viewport+1 and int(state.get('body',99999))<=viewport+1,f'Projects production overflows at {width}: {state}')
    browser_smoke.require(float(state.get('min',0))>=47.5,f'Projects production controls below 48px at {width}: {state}')
    browser_smoke.require(any('/assets/glaze-v1.4.0.css' in r for r in state.get('resources',[])),f'Projects production shared V1.4 CSS not loaded: {state}')
    browser_smoke.require(any('/assets/glaze-v1.3-consumer.css' in r for r in state.get('resources',[])),f'Projects production inherited consumer adaptation not loaded: {state}')
    browser_smoke.require(not state.get('broken'),f'Projects production broken images at {width}: {state}')
def main():
    url=remote.base('production');remote.valid(url)
    driver=None;sid=None;log=None
    try:
        browser_smoke.DRIVER_BASE=f'http://{browser_smoke.DRIVER_HOST}:{browser_smoke.DRIVER_PORTS["chrome"]}'
        with tempfile.NamedTemporaryFile(prefix='projects-v14-production-',suffix='.log',delete=False) as f:
            log=Path(f.name);driver=subprocess.Popen(browser_smoke.driver_command('chrome',browser_smoke.DRIVER_PORTS['chrome']),stdout=f,stderr=subprocess.STDOUT)
        browser_smoke.wait_for_driver('chrome');sid=browser_smoke.create_session('chrome')
        browser_smoke.webdriver_request('POST',f'/session/{sid}/timeouts',{'implicit':0,'pageLoad':15000,'script':10000})
        for w,h in VIEWPORTS:
            mobile_smoke.set_viewport(sid,w,h);browser_smoke.webdriver_request('POST',f'/session/{sid}/url',{'url':url});time.sleep(.2);inspect(sid,w)
        print('Projects canonical V1.4 Chrome acceptance passed at 1180, 768, 390, and 320 widths');return 0
    except Exception as e:
        print(f'Projects canonical V1.4 Chrome acceptance failed: {e}');return 1
    finally:
        if sid:
            try:browser_smoke.webdriver_request('DELETE',f'/session/{sid}')
            except Exception:pass
        if driver:
            driver.terminate()
            try:driver.wait(timeout=5)
            except subprocess.TimeoutExpired:driver.kill();driver.wait(timeout=5)
        if log:
            try:log.unlink()
            except OSError:pass
        browser_smoke.DRIVER_BASE=''
if __name__=='__main__':raise SystemExit(main())
