#!/usr/bin/env python3
"""Verify the Mesh Center GLAZE UI V1.4 public deployment against exact built bytes."""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
SOURCE=ROOT/'website'
BASE='https://mesh.goreecloud.com/'
HOST='mesh.goreecloud.com'
REV='84cb3db4884042f0fa25ed6d475a127fb110f596'
MAX=2_000_000
HEADERS={
 'content-security-policy':("default-src 'self'","frame-ancestors 'none'","connect-src 'none'"),
 'strict-transport-security':('max-age=31536000',),
 'x-content-type-options':('nosniff',),
 'x-frame-options':('DENY',),
 'referrer-policy':('no-referrer',),
 'cross-origin-opener-policy':('same-origin',),
}
class Redirects(HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  p=urlparse(newurl)
  if p.scheme!='https' or p.hostname!=HOST: raise URLError(f'cross-host redirect rejected: {newurl}')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch(path):
 url=urljoin(BASE,path.lstrip('/'));req=Request(url,headers={'User-Agent':'GoreeCloud-Mesh-V1.4-Verifier/1','Accept-Encoding':'identity','Cache-Control':'no-cache'},method='GET')
 opener=build_opener(Redirects(),HTTPSHandler(context=ssl.create_default_context()))
 try:
  with opener.open(req,timeout=15) as r:return r.status,r.geturl(),{k.lower():v for k,v in r.headers.items()},r.read(MAX+1)
 except HTTPError as e:return e.code,e.geturl(),{k.lower():v for k,v in e.headers.items()},e.read(MAX+1)
def validate_config():
 p=urlparse(BASE)
 if p.scheme!='https' or p.hostname!=HOST: raise SystemExit('Mesh verifier must remain fixed to canonical HTTPS host')
 for rel in ('index.html','404.html','_headers','robots.txt','assets/goreecloud-mesh-mark.svg'):
  if not (SOURCE/rel).is_file(): raise SystemExit(f'missing Mesh source: {rel}')
def verify():
 if not DIST.is_dir(): raise SystemExit('Mesh dist missing; build first')
 errors=[]
 for file in sorted(DIST.rglob('*')):
  if not file.is_file() or file.name=='_headers': continue
  rel=file.relative_to(DIST).as_posix();path='/' if rel=='index.html' else '/'+rel
  try: status,final,headers,body=fetch(path)
  except Exception as e: errors.append(f'{path}: {e}');continue
  if status!=200: errors.append(f'{path}: HTTP {status}, expected 200');continue
  expected=file.read_bytes()
  if body!=expected: errors.append(f'{path}: byte mismatch expected {sha256(expected).hexdigest()} deployed {sha256(body).hexdigest()}')
  if urlparse(final).hostname!=HOST: errors.append(f'{path}: host drift {final}')
 try:
  status,final,headers,body=fetch('/');text=body.decode('utf-8',errors='replace')
  for marker in ('name="goreecloud-glaze-ui" content="1.4.0"',f'name="goreecloud-glaze-source-revision" content="{REV}"','name="goreecloud-glaze-consumer-state" content="build-migrated-rendered-acceptance-pending"','authority_transfer = false'):
   if marker not in text: errors.append(f'/: missing V1.4/Mesh marker: {marker}')
  if headers.get('server','').lower()!='cloudflare': errors.append('/: expected Cloudflare delivery')
  for h,frags in HEADERS.items():
   value=headers.get(h,'')
   for frag in frags:
    if frag.lower() not in value.lower(): errors.append(f'/: {h} missing {frag}')
 except Exception as e: errors.append(f'/: {e}')
 try:
  status,final,headers,body=fetch('/__goreecloud_mesh_v14_missing__')
  if status!=404: errors.append(f'404: HTTP {status}, expected 404')
  if body!=(DIST/'404.html').read_bytes(): errors.append('404: body differs from exact built 404.html')
 except Exception as e: errors.append(f'404: {e}')
 if errors:
  print('Mesh V1.4 production verification failed:');[print('- '+e) for e in errors];return 1
 print('Mesh Center exact GLAZE UI V1.4 production publication verification passed; Mesh runtime acceptance remains separate');return 0
def main():
 p=argparse.ArgumentParser();p.add_argument('--check-config',action='store_true');p.add_argument('--target',choices=('production',));a=p.parse_args();validate_config()
 if a.check_config: print('Mesh V1.4 verifier configuration valid; live acceptance remains separate');return 0
 if a.target!='production': p.error('--target production is required unless --check-config is used')
 return verify()
if __name__=='__main__':raise SystemExit(main())
