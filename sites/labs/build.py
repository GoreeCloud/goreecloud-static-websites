#!/usr/bin/env python3
"""Build GoreeCloud Labs as an exact GLAZE UI V1.4 publication artifact."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import urllib.request

ROOT=Path(__file__).resolve().parent
DIST=ROOT/'dist'
LOCK=json.loads((ROOT/'glaze.lock.json').read_text())
VERSION='1.4.0'; REV='84cb3db4884042f0fa25ed6d475a127fb110f596'; ENTRY='glaze-v1.4.0.css'; ENTRY_BLOB='d48a9bc317090d152799769271de0fb4325494c4'
IMPORT_RE=re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)',re.I)
for k,e in {'version':VERSION,'lifecycle':'Stable','repository':'GoreeCloud/goreecloud-glaze-ui','stable_commit':REV,'entrypoint':ENTRY,'entrypoint_blob':ENTRY_BLOB,'consumer_state':'build-migrated-rendered-acceptance-pending'}.items():
    if LOCK.get(k)!=e: raise SystemExit(f'unexpected Labs GLAZE UI lock {k}: {LOCK.get(k)!r}')
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data,usedforsecurity=False).hexdigest()
def read_glaze(name):
    if Path(name).name!=name or not name.endswith('.css'): raise SystemExit(f'unsafe Glaze dependency: {name}')
    src=os.environ.get('GLAZE_UI_SOURCE')
    if src:
        p=Path(src)/'css'/name
        if not p.is_file() or p.is_symlink(): raise SystemExit(f'missing pinned Glaze source: {name}')
        data=p.read_bytes()
    else:
        url=f"https://raw.githubusercontent.com/{LOCK['repository']}/{LOCK['stable_commit']}/css/{name}"
        req=urllib.request.Request(url,headers={'User-Agent':'GoreeCloud-Labs-builder/1.4'})
        with urllib.request.urlopen(req,timeout=20) as r:data=r.read()
    if name==ENTRY and blob(data)!=ENTRY_BLOB: raise SystemExit('Labs V1.4 entrypoint integrity mismatch')
    return data
def collect(name,out):
    if name in out:return
    data=read_glaze(name); text=data.decode()
    for s in re.findall(r'@import[^;]+;',text,flags=re.I):
        if 'http://' in s.lower() or 'https://' in s.lower() or '//' in s: raise SystemExit(f'remote Glaze import forbidden: {s}')
        m=IMPORT_RE.search(s)
        if not m: raise SystemExit(f'unsupported Glaze import: {s}')
        collect(m.group(1),out)
    out[name]=data
def render(text):
    text=text.replace('data-glaze-version="1.3.0"','data-glaze-version="1.4.0"').replace('name="goreecloud-glaze-ui" content="1.3.0"','name="goreecloud-glaze-ui" content="1.4.0"')
    anchor='<meta name="goreecloud-glaze-ui" content="1.4.0">'
    if 'name="goreecloud-glaze-source-revision"' not in text:
        text=text.replace(anchor,anchor+f'\n  <meta name="goreecloud-glaze-source-revision" content="{REV}">\n  <meta name="goreecloud-glaze-consumer-state" content="build-migrated-rendered-acceptance-pending">',1)
    css='<link rel="stylesheet" href="/assets/glaze-v1.4.0.css" data-glaze-ui="1.4.0">'
    if css not in text:
        text=text.replace('<link rel="stylesheet" href="/site.css">',css+'\n  <link rel="stylesheet" href="/site.css">',1)
    return text
if DIST.exists():
    if DIST.is_symlink(): raise SystemExit('Labs dist must not be a symlink')
    shutil.rmtree(DIST)
(DIST/'assets').mkdir(parents=True)
for name in ('index.html','404.html','site.css','site.js','_headers','robots.txt','sitemap.xml'):
    src=ROOT/name; dst=DIST/name
    if not src.is_file() or src.is_symlink(): raise SystemExit(f'missing or unsafe Labs source: {name}')
    shutil.copy2(src,dst)
    if name.endswith('.html'): dst.write_text(render(dst.read_text()))
shutil.copy2(ROOT/'assets'/'goreecloud-logo.svg',DIST/'assets'/'goreecloud-logo.svg')
styles={};collect(ENTRY,styles)
for name,data in sorted(styles.items()):(DIST/'assets'/name).write_bytes(data)
print(f'Built Labs V1.4 publication artifact: {DIST}')
