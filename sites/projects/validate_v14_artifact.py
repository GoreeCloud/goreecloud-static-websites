#!/usr/bin/env python3
"""Fail-closed validation for the built Projects GLAZE UI V1.4 artifact."""
from __future__ import annotations
import hashlib, re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DIST=ROOT/'dist'
REV='84cb3db4884042f0fa25ed6d475a127fb110f596'
ENTRY='glaze-v1.4.0.css'
ENTRY_BLOB='d48a9bc317090d152799769271de0fb4325494c4'
for rel in ('index.html','404.html','_headers','assets/app.js','assets/suite-portfolio.js','assets/icon-refresh.js','assets/styles.css','assets/mobile-refresh.css','assets/glaze-v1.3-consumer.css',f'assets/{ENTRY}'):
    p=DIST/rel
    if not p.is_file() or p.is_symlink():raise SystemExit(f'missing or unsafe Projects V1.4 artifact file: {rel}')
for page in ('index.html','404.html'):
    text=(DIST/page).read_text(encoding='utf-8')
    for marker in ('data-glaze-version="1.4.0"','name="goreecloud-glaze-ui" content="1.4.0"',f'name="goreecloud-glaze-source-revision" content="{REV}"','data-glaze-ui="1.4.0"','/assets/glaze-v1.4.0.css','/assets/glaze-v1.3-consumer.css','glaze-canvas'):
        if marker not in text:raise SystemExit(f'{page} missing Projects V1.4 publication marker: {marker}')
    for stale in ('data-glaze-ui="1.3.0"','name="goreecloud-glaze-ui" content="1.3.0"','GLAZE UI V1.3'):
        if stale in text:raise SystemExit(f'{page} retains stale current-target marker: {stale}')
index=(DIST/'index.html').read_text(encoding='utf-8')
portfolio=(DIST/'assets'/'suite-portfolio.js').read_text(encoding='utf-8')
app=(DIST/'assets'/'app.js').read_text(encoding='utf-8')
for marker in ('<strong id="app-count">45</strong><span>Suite products</span>','<strong id="foundation-count">7</strong><span>Integral platform systems</span>','GLAZE UI V1.4','Security Center · Sentinel Fold','Mesh Center · Weave'):
    if marker not in index:raise SystemExit(f'Projects V1.4 artifact missing static publication marker: {marker}')
for product in ('GoreeCloud Vault','GoreeCloud Health','GoreeCloud Reader','GoreeCloud Router OS','GoreeCloud Social','GoreeCloud Home','GoreeCloud Home Security'):
    if product not in portfolio+app:raise SystemExit(f'Projects V1.4 artifact missing dynamic portfolio marker: {product}')
try:
    group_block=portfolio.split('const suitePortfolioGroups=Object.freeze({',1)[1].split('});',1)[0]
except IndexError as exc:
    raise SystemExit('Projects V1.4 Suite portfolio group authority is missing') from exc
portfolio_names=re.findall(r"'(GoreeCloud[^']*)'",group_block)
if len(portfolio_names)!=45 or len(set(portfolio_names))!=45:raise SystemExit(f'Projects V1.4 Suite portfolio must contain exactly 45 unique products; got {len(portfolio_names)}')
if len(re.findall(r"^\s*'[^']+':\[",group_block,flags=re.MULTILINE))!=9:raise SystemExit('Projects V1.4 Suite portfolio must preserve exactly 9 functional groups')
data=(DIST/'assets'/ENTRY).read_bytes()
actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data,usedforsecurity=False).hexdigest()
if actual!=ENTRY_BLOB:raise SystemExit(f'Projects V1.4 entrypoint blob mismatch: {actual}')
seen=set()
def visit(name:str):
    if name in seen:return
    p=DIST/'assets'/name
    if not p.is_file() or p.is_symlink():raise SystemExit(f'missing Projects Glaze dependency: {name}')
    seen.add(name)
    for stmt in re.findall(r'@import[^;]+;',p.read_text(encoding='utf-8'),flags=re.I):
        if 'http://' in stmt.lower() or 'https://' in stmt.lower() or '//' in stmt:raise SystemExit(f'remote Glaze import forbidden: {stmt}')
        m=re.search(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)',stmt,re.I)
        if not m:raise SystemExit(f'unsupported built Glaze import: {stmt}')
        visit(m.group(1))
visit(ENTRY)
if 'glaze-v1.3.0.css' not in seen:raise SystemExit('Projects V1.4 inherited Stable dependency closure is incomplete')
print('Projects exact GLAZE UI V1.4 built artifact validated: 45 Suite products, 9 groups, exact Stable dependency closure')
