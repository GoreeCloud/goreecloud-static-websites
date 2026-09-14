#!/usr/bin/env python3
"""Build GoreeCloud Projects as an exact GLAZE UI V1.4 publication artifact."""
from __future__ import annotations
import hashlib, json, os, re, shutil, urllib.request, urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DIST=ROOT/'dist'
VERSION='1.4.0'
REVISION='84cb3db4884042f0fa25ed6d475a127fb110f596'
ENTRY='glaze-v1.4.0.css'
ENTRY_BLOB='d48a9bc317090d152799769271de0fb4325494c4'
LEGACY_REV='8354308445da9ac35ced2b37a7f503a08a0aaf72'
IMPORT_RE=re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)',re.I)

def blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data,usedforsecurity=False).hexdigest()

def render(text:str)->str:
    pairs=(
      ('data-glaze-version="1.3.0"','data-glaze-version="1.4.0"'),
      ('name="goreecloud-glaze-ui" content="1.3.0"','name="goreecloud-glaze-ui" content="1.4.0"'),
      (f'name="goreecloud-glaze-source-revision" content="{LEGACY_REV}"',f'name="goreecloud-glaze-source-revision" content="{REVISION}"'),
      ('GLAZE UI V1.3 / 1.3.0','GLAZE UI V1.4 / 1.4.0'),('GLAZE UI V1.3','GLAZE UI V1.4'),('Glaze UI V1.3','Glaze UI V1.4'),
      ('1.3.0 current Official Stable','1.4.0 current Official Stable'),(LEGACY_REV,REVISION),
      ('data-glaze-ui="1.3.0"','data-glaze-consumer-adaptation="1.3-inherited"'),
    )
    for old,new in pairs:text=text.replace(old,new)
    shared='<link rel="stylesheet" href="/assets/glaze-v1.4.0.css" data-glaze-ui="1.4.0">'
    anchor='<link rel="stylesheet" href="/assets/glaze-v1.3-consumer.css?v=20260910-v13" data-glaze-consumer-adaptation="1.3-inherited">'
    if shared not in text and anchor in text:text=text.replace(anchor,shared+'\n  '+anchor,1)
    return text

def read_css(name:str,lock:dict)->bytes:
    source=os.environ.get('GLAZE_UI_SOURCE')
    if Path(name).name!=name or not name.endswith('.css'):raise SystemExit(f'unsafe Glaze dependency: {name}')
    if source:
        p=Path(source)/'css'/name
        if not p.is_file() or p.is_symlink():raise SystemExit(f'missing pinned Glaze source: {name}')
        data=p.read_bytes()
    else:
        url=f"https://raw.githubusercontent.com/{lock['repository']}/{lock['stable_commit']}/css/{name}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'GoreeCloud-projects-builder/1.4'}),timeout=20) as r:data=r.read()
        except urllib.error.URLError as e:raise SystemExit(f'failed to fetch {name}: {e}')
    if name==ENTRY and blob(data)!=ENTRY_BLOB:raise SystemExit('GLAZE UI V1.4 entrypoint integrity mismatch')
    return data

def main():
    lock=json.loads((ROOT/'glaze.lock.json').read_text())
    expect={'version':VERSION,'lifecycle':'Stable','stable_commit':REVISION,'entrypoint':ENTRY,'entrypoint_blob':ENTRY_BLOB,'consumer_state':'source-migrated-rendered-acceptance-pending'}
    for k,v in expect.items():
        if lock.get(k)!=v:raise SystemExit(f'invalid Projects Glaze lock {k}: {lock.get(k)!r}')
    if DIST.exists():shutil.rmtree(DIST)
    (DIST/'assets').mkdir(parents=True)
    for name in ('index.html','404.html','_headers'):
        src=ROOT/name
        if not src.is_file() or src.is_symlink():raise SystemExit(f'missing public Projects source: {name}')
        shutil.copy2(src,DIST/name)
    for page in ('index.html','404.html'):
        p=DIST/page;p.write_text(render(p.read_text(encoding='utf-8')),encoding='utf-8')
    assets=ROOT/'assets'
    for src in assets.rglob('*'):
        if src.is_symlink():raise SystemExit(f'unsafe Projects asset: {src}')
        if src.is_file():
            out=DIST/'assets'/src.relative_to(assets);out.parent.mkdir(parents=True,exist_ok=True)
            if src.suffix in {'.js','.css'}:
                out.write_text(render(src.read_text(encoding='utf-8')),encoding='utf-8')
            else:shutil.copy2(src,out)
    seen={}
    def collect(name:str):
        if name in seen:return
        data=read_css(name,lock);text=data.decode('utf-8')
        for stmt in re.findall(r'@import[^;]+;',text,flags=re.I):
            if 'http://' in stmt.lower() or 'https://' in stmt.lower() or '//' in stmt:raise SystemExit(f'remote Glaze import forbidden: {stmt}')
            m=IMPORT_RE.search(stmt)
            if not m:raise SystemExit(f'unsupported Glaze import: {stmt}')
            collect(m.group(1))
        seen[name]=data
    collect(ENTRY)
    for name,data in seen.items():(DIST/'assets'/name).write_bytes(data)
    print(f'Built Projects with GLAZE UI {VERSION} Stable pinned to {REVISION}')
if __name__=='__main__':main()
