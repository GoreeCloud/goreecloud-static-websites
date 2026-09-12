#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent
DIST=ROOT/'dist'
if DIST.exists():
    shutil.rmtree(DIST)
(DIST/'assets').mkdir(parents=True)
for name in ('index.html','404.html','site.css','site.js','_headers','robots.txt','sitemap.xml'):
    shutil.copy2(ROOT/name,DIST/name)
shutil.copy2(ROOT/'assets'/'goreecloud-logo.svg',DIST/'assets'/'goreecloud-logo.svg')
print(f'Built {DIST}')
