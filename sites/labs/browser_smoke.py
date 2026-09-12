#!/usr/bin/env python3
from __future__ import annotations
import json,shutil,subprocess,time
from pathlib import Path
from typing import Any
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parent; DIST=ROOT/'dist'; HOST='127.0.0.1'; PORT=8788; TARGET=f'http://{HOST}:{PORT}/'; DRIVER_PORT=9534; DRIVER=f'http://{HOST}:{DRIVER_PORT}'; VIEWPORTS=((1180,900),(768,900),(390,844),(320,844))
class SmokeError(RuntimeError): pass
def require(ok,msg):
    if not ok: raise SmokeError(msg)
def req(method,path,payload=None):
    body=None if payload is None else json.dumps(payload).encode(); r=Request(DRIVER+path,data=body,method=method,headers={'Content-Type':'application/json'})
    try:
        with urlopen(r,timeout=20) as response: raw=response.read()
    except HTTPError as e: raise SmokeError(e.read().decode(errors='replace')) from e
    except (URLError,TimeoutError) as e: raise SmokeError(str(e)) from e
    if not raw:return None
    value=json.loads(raw.decode()).get('value');
    if isinstance(value,dict) and value.get('error'): raise SmokeError(value.get('message','webdriver error'))
    return value
def execute(s,script): return req('POST',f'/session/{s}/execute/sync',{'script':script,'args':[]})
def viewport(s,w,h): req('POST',f'/session/{s}/goog/cdp/execute',{'cmd':'Emulation.setDeviceMetricsOverride','params':{'width':w,'height':h,'deviceScaleFactor':1,'mobile':False}})
def session():
    value=req('POST','/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-background-networking','--no-first-run','--window-size=1180,900']}}}}); require(isinstance(value,dict),'bad Chrome response'); return value['sessionId']
def wait_driver():
    end=time.time()+15
    while time.time()<end:
        try:
            if req('GET','/status').get('ready'):return
        except Exception: pass
        time.sleep(.2)
    raise SmokeError('chromedriver did not become ready')
def wait_site():
    end=time.time()+10
    while time.time()<end:
        try:
            with urlopen(TARGET,timeout=1) as r:
                if r.status==200:return
        except Exception: pass
        time.sleep(.1)
    raise SmokeError('Labs server did not become ready')
def state(s):
    return execute(s,"""
    const visible=e=>{const r=e.getBoundingClientRect(),cs=getComputedStyle(e);return cs.display!=='none'&&cs.visibility!=='hidden'&&r.width>0&&r.height>0};
    const cols=e=>getComputedStyle(e).gridTemplateColumns.split(/\s+/).filter(Boolean).length;
    const cards=[...document.querySelectorAll('[data-workstream]')]; const lanes=[...document.querySelectorAll('[data-lane]')];
    return {title:document.title,width:innerWidth,scrollWidth:document.documentElement.scrollWidth,workstreams:cards.length,lanes:lanes.length,visibleLanes:lanes.filter(visible).length,broken:[...document.images].filter(i=>!i.complete||i.naturalWidth<=0).map(i=>i.src),minNav:Math.min(...[...document.querySelectorAll('.site-header a,.theme-group button')].filter(visible).map(e=>e.getBoundingClientRect().height)),columns:[...document.querySelectorAll('.workstream-grid')].filter(visible).map(cols)};
    """)
def exercise(s):
    req('POST',f'/session/{s}/url',{'url':TARGET})
    for w,h in VIEWPORTS:
        viewport(s,w,h); time.sleep(.08); st=state(s); require(st['title']=='GoreeCloud Labs — Development Center',f'title drift {st}'); require(st['workstreams']==27,f'workstream count drift {st}'); require(st['lanes']==6,f'lane count drift {st}'); require(st['scrollWidth']<=w+1,f'horizontal overflow at {w}: {st}'); require(not st['broken'],f'broken images at {w}: {st}'); require(st['minNav']>=47.5,f'target below 48px at {w}: {st}');
        expected=3 if w>=1051 else 2 if w>=761 else 1
        require(all(c==expected for c in st['columns']),f'grid columns drift at {w}: expected {expected}, got {st}')
    filtered=execute(s,"""document.querySelector('[data-filter=home]').click();const v=[...document.querySelectorAll('[data-lane]')].filter(e=>!e.hidden).map(e=>e.dataset.lane);return {visible:v,pressed:document.querySelector('[data-filter=home]').getAttribute('aria-pressed')};"""); require(filtered['visible']==['home'] and filtered['pressed']=='true',f'filter failed: {filtered}'); execute(s,"document.querySelector('[data-filter=all]').click();return true;")
    theme=execute(s,"""const click=v=>{const b=document.querySelector(`[data-theme-choice="${v}"]`);b.click();return {theme:document.documentElement.dataset.theme,pressed:b.getAttribute('aria-pressed')}};return {light:click('light'),dark:click('dark'),system:click('system')};"""); require(theme['light']['theme']=='light' and theme['dark']['theme']=='dark' and theme['system']['theme']=='system','theme controls failed')
def main():
    subprocess.run(['python3','build.py'],cwd=ROOT,check=True); subprocess.run(['python3','validate.py','dist'],cwd=ROOT,check=True)
    driver=shutil.which('chromedriver') or '/usr/local/share/chromedriver-linux64/chromedriver'; require(Path(driver).is_file(),'chromedriver unavailable')
    web=subprocess.Popen(['python3','-m','http.server',str(PORT),'--bind',HOST,'--directory',str(DIST)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); chrome=subprocess.Popen([driver,f'--port={DRIVER_PORT}',f'--url-base=/'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); sid=None
    try:
        wait_site();wait_driver();sid=session();exercise(sid);print('Labs Chrome smoke passed at 1180/768/390/320')
    finally:
        if sid:
            try:req('DELETE',f'/session/{sid}')
            except Exception:pass
        for p in (chrome,web): p.terminate()
if __name__=='__main__':main()
