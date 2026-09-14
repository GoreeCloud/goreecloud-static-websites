#!/usr/bin/env python3
"""Exercise the exact built Projects GLAZE UI V1.4 artifact in Chrome."""
from __future__ import annotations
from pathlib import Path
import subprocess,tempfile,time
from urllib.request import urlopen
from urllib.error import URLError
import browser_smoke,mobile_smoke
SITE=Path(__file__).resolve().parent/'dist'; HOST='127.0.0.1'; PORT=8773; URL=f'http://{HOST}:{PORT}/'
VIEWPORTS=((1180,900),(768,900),(390,844),(320,844))
REV='84cb3db4884042f0fa25ed6d475a127fb110f596'
def wait_http():
    deadline=time.monotonic()+10
    while time.monotonic()<deadline:
        try:
            with urlopen(URL,timeout=1) as r:
                if r.status==200:return
        except (URLError,TimeoutError,OSError):pass
        time.sleep(.1)
    raise browser_smoke.WebDriverError('Projects V1.4 artifact server did not become ready')
def inspect(sid,width):
    s=browser_smoke.execute(sid,"""
    const vis=n=>{const s=getComputedStyle(n),r=n.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};
    const ctrls=[...document.querySelectorAll('.topbar nav a,.theme-group button,.filter,.glaze-button,.card footer a')].filter(vis);
    return {ready:document.readyState,title:document.title,glaze:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',rev:document.querySelector('meta[name="goreecloud-glaze-source-revision"]')?.content||'',suite:document.querySelector('#app-count')?.textContent||'',systems:document.querySelector('#foundation-count')?.textContent||'',scroll:document.documentElement.scrollWidth,body:document.body.scrollWidth,width:window.innerWidth,cards:document.querySelectorAll('#projects .card').length,min:ctrls.length?Math.min(...ctrls.map(n=>n.getBoundingClientRect().height)):0,resources:performance.getEntriesByType('resource').map(e=>e.name),broken:[...document.images].filter(i=>!i.complete||i.naturalWidth<=0).map(i=>i.src)};
    """)
    browser_smoke.require(s.get('ready')=='complete',f'Projects V1.4 not ready at {width}: {s}')
    browser_smoke.require(s.get('title')=='Projects — GoreeCloud',f'Projects title drift: {s}')
    browser_smoke.require(s.get('glaze')=='1.4.0' and s.get('rev')==REV,f'Projects V1.4 identity drift at {width}: {s}')
    browser_smoke.require(s.get('suite')=='45' and s.get('systems')=='7',f'Projects portfolio counts drift: {s}')
    browser_smoke.require(int(s.get('cards',0))>=browser_smoke.MIN_PROJECT_CARDS,f'Projects cards incomplete: {s}')
    viewport=int(s.get('width',0));browser_smoke.require(int(s.get('scroll',99999))<=viewport+1 and int(s.get('body',99999))<=viewport+1,f'Projects V1.4 overflows at {width}: {s}')
    browser_smoke.require(float(s.get('min',0))>=47.5,f'Projects controls below 48px at {width}: {s}')
    browser_smoke.require(any('/assets/glaze-v1.4.0.css' in r for r in s.get('resources',[])),f'Projects shared V1.4 CSS not loaded: {s}')
    browser_smoke.require(any('/assets/glaze-v1.3-consumer.css' in r for r in s.get('resources',[])),f'Projects inherited consumer adaptation not loaded: {s}')
    browser_smoke.require(not s.get('broken'),f'Projects broken images at {width}: {s}')
def main():
    server=driver=None;sid=None;log=None
    try:
        server=subprocess.Popen(['python3','-m','http.server',str(PORT),'--bind',HOST,'--directory',str(SITE)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);wait_http()
        browser_smoke.DRIVER_BASE=f'http://{browser_smoke.DRIVER_HOST}:{browser_smoke.DRIVER_PORTS["chrome"]}'
        with tempfile.NamedTemporaryFile(prefix='projects-v14-',suffix='.log',delete=False) as f:
            log=Path(f.name);driver=subprocess.Popen(browser_smoke.driver_command('chrome',browser_smoke.DRIVER_PORTS['chrome']),stdout=f,stderr=subprocess.STDOUT)
        browser_smoke.wait_for_driver('chrome');sid=browser_smoke.create_session('chrome')
        browser_smoke.webdriver_request('POST',f'/session/{sid}/timeouts',{'implicit':0,'pageLoad':15000,'script':10000})
        for w,h in VIEWPORTS:
            mobile_smoke.set_viewport(sid,w,h);browser_smoke.webdriver_request('POST',f'/session/{sid}/url',{'url':URL});time.sleep(.2);inspect(sid,w)
        print('Projects exact V1.4 artifact Chrome acceptance passed at 1180, 768, 390, and 320 widths');return 0
    except Exception as e:
        print(f'Projects V1.4 artifact Chrome acceptance failed: {e}');return 1
    finally:
        if sid:
            try:browser_smoke.webdriver_request('DELETE',f'/session/{sid}')
            except Exception:pass
        for p in (driver,server):
            if p:
                p.terminate()
                try:p.wait(timeout=5)
                except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
        if log:
            try:log.unlink()
            except OSError:pass
        browser_smoke.DRIVER_BASE=''
if __name__=='__main__':raise SystemExit(main())
