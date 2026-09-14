#!/usr/bin/env python3
"""Exercise the live GoreeCloud Labs V1.4 canonical publication in headless Chrome."""
from __future__ import annotations
from pathlib import Path
import subprocess,tempfile
import browser_smoke as smoke
PRODUCTION_URL='https://labs.goreecloud.com/'; REV='84cb3db4884042f0fa25ed6d475a127fb110f596'
def require(ok,msg):
    if not ok: raise smoke.SmokeError(msg)
def verify_live_content(sid):
    state=smoke.execute(sid,r"""const images=[...document.images];return {title:document.title,glaze:document.querySelector('meta[name="goreecloud-glaze-ui"]')?.content||'',revision:document.querySelector('meta[name="goreecloud-glaze-source-revision"]')?.content||'',consumer:document.querySelector('meta[name="goreecloud-glaze-consumer-state"]')?.content||'',robots:document.querySelector('meta[name="robots"]')?.content||'',canonical:document.querySelector('link[rel="canonical"]')?.href||'',workstreams:document.querySelectorAll('[data-workstream]').length,lanes:document.querySelectorAll('[data-lane]').length,filters:document.querySelectorAll('[data-filter]').length,imageCount:images.length,loadedImages:images.filter(i=>i.complete&&i.naturalWidth>0&&i.naturalHeight>0).length,failedImages:images.filter(i=>i.complete&&(i.naturalWidth===0||i.naturalHeight===0)).map(i=>i.src),bodyText:document.body.innerText};""")
    require(isinstance(state,dict),f'Labs production browser state unreadable: {state!r}');require(state.get('title')=='GoreeCloud Labs — Development Center',f'unexpected Labs title: {state}');require(state.get('glaze')=='1.4.0',f'Labs Glaze version mismatch: {state}');require(state.get('revision')==REV,f'Labs Glaze revision mismatch: {state}');require(state.get('consumer')=='build-migrated-rendered-acceptance-pending',f'Labs consumer state mismatch: {state}');require(state.get('robots')=='noindex,nofollow',f'Labs indexing boundary drifted: {state}');require(state.get('canonical')==PRODUCTION_URL,f'Labs canonical drifted: {state}');require(int(state.get('workstreams',0))==27 and int(state.get('lanes',0))==6 and int(state.get('filters',0))==7,f'Labs structure drift: {state}');require(int(state.get('loadedImages',-1))==int(state.get('imageCount',0)),f"Labs failed images: {state.get('failedImages')}")
    text=str(state.get('bodyText',''))
    for m in ('Where GoreeCloud gets built next.','Labs is not a release channel.','Development workstreams','Integral Platform Systems','Privacy Shield','GoreeCloud Mesh','Evidence stays scoped'):require(m in text,f'Labs production missing marker: {m!r}')
def main():
    smoke.TARGET=PRODUCTION_URL;driver=None;sid=None;log_path=None
    try:
        with tempfile.NamedTemporaryFile(prefix='labs-v14-production-chromedriver-',suffix='.log',delete=False) as log:
            log_path=Path(log.name);driver_path=__import__('shutil').which('chromedriver') or '/usr/local/share/chromedriver-linux64/chromedriver';require(Path(driver_path).is_file(),'chromedriver unavailable');driver=subprocess.Popen([driver_path,f'--port={smoke.DRIVER_PORT}','--allowed-ips=127.0.0.1'],stdout=log,stderr=subprocess.STDOUT)
        smoke.wait_driver();sid=smoke.session();smoke.exercise(sid);verify_live_content(sid);print('Labs canonical production Chrome acceptance passed for GLAZE UI V1.4 publication; indexing release remains separate');return 0
    except Exception as e:print(f'Labs production Chrome smoke failed: {e}');return 1
    finally:
        if sid:
            try:smoke.req('DELETE',f'/session/{sid}')
            except Exception:pass
        if driver:
            driver.terminate()
            try:driver.wait(timeout=5)
            except subprocess.TimeoutExpired:driver.kill();driver.wait(timeout=5)
        if log_path:
            try:log_path.unlink()
            except OSError:pass
if __name__=='__main__':raise SystemExit(main())
