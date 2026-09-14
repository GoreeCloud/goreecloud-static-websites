#!/usr/bin/env python3
"""Verify Projects production/preview against the exact built GLAZE UI V1.4 artifact."""
from __future__ import annotations
import argparse,os,re,ssl
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.parse import urljoin,urlparse
from urllib.request import HTTPRedirectHandler,HTTPSHandler,Request,build_opener
SITE=Path(__file__).resolve().parent;DIST=SITE/'dist'
PROD='projects.goreecloud.com';PAGES='goreecloud-projects.pages.dev';REV='84cb3db4884042f0fa25ed6d475a127fb110f596';TIMEOUT=15;MAX=4_194_304
BRANCH_RE=re.compile(r'[^a-z0-9-]+')
HEADERS={'content-security-policy':("default-src 'self'","frame-ancestors 'none'","object-src 'none'"),'strict-transport-security':('max-age=31536000',),'x-content-type-options':('nosniff',),'x-frame-options':('deny',),'permissions-policy':('camera=()','microphone=()','geolocation=()'),'cross-origin-opener-policy':('same-origin',)}
@dataclass(frozen=True)
class Resp:status:int;url:str;headers:dict[str,str];body:bytes
def label():
    raw=os.environ.get('GITHUB_HEAD_REF') or os.environ.get('GITHUB_REF_NAME')
    if not raw:raise ValueError('branch preview requires GitHub branch context')
    return re.sub(r'-+','-',BRANCH_RE.sub('-',raw.lower().replace('/','-')).strip('-'))[:28].rstrip('-')
def base(target):return f'https://{PROD}/' if target=='production' else f'https://{label()}.{PAGES}/'
def valid(url):
    p=urlparse(url);host=p.hostname or ''
    if p.scheme!='https' or not(host==PROD or host.endswith('.'+PAGES)) or p.username or p.password or p.query or p.fragment:raise ValueError(f'Projects deployment target outside allowlist: {url}')
class Redirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):valid(newurl);return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch(url):
    valid(url);op=build_opener(Redirect(),HTTPSHandler(context=ssl.create_default_context()));req=Request(url,headers={'User-Agent':'GoreeCloud-Projects-V14-Verifier/1','Accept-Encoding':'identity','Cache-Control':'no-cache','Pragma':'no-cache'})
    try:
        with op.open(req,timeout=TIMEOUT) as r:
            body=r.read(MAX+1);return Resp(r.status,r.geturl(),{k.lower():v for k,v in r.headers.items()},body)
    except HTTPError as e:return Resp(e.code,e.geturl(),{k.lower():v for k,v in e.headers.items()},e.read(MAX+1))
    except URLError as e:raise RuntimeError(f'network request failed: {url}: {e.reason}')
def expected():
    if not DIST.is_dir():raise ValueError('Projects dist/ missing; build exact artifact first')
    out={}
    for p in sorted(DIST.rglob('*')):
        if p.is_symlink():raise ValueError(f'Projects artifact symlink prohibited: {p}')
        if p.is_file() and p.name!='_headers':out[p.relative_to(DIST).as_posix()]=p.read_bytes()
    return out
def verify(target):
    root=base(target);errors=[]
    try:files=expected()
    except ValueError as e:return [str(e)]
    for rel,data in files.items():
        path='/' if rel=='index.html' else '/'+rel;url=urljoin(root,path.lstrip('/'))
        try:r=fetch(url)
        except Exception as e:errors.append(str(e));continue
        if r.status!=200:errors.append(f'{path} HTTP {r.status}; expected 200');continue
        if r.body!=data:errors.append(f'{path} mismatch expected {sha256(data).hexdigest()} deployed {sha256(r.body).hexdigest()}')
    try:
        r=fetch(root);text=r.body.decode('utf-8',errors='replace')
        for m in ('name="goreecloud-glaze-ui" content="1.4.0"',f'name="goreecloud-glaze-source-revision" content="{REV}"','data-glaze-ui="1.4.0"','<strong id="app-count">45</strong><span>Suite products</span>'):
            if m not in text:errors.append(f'Projects production root missing V1.4 marker: {m}')
        for h,vals in HEADERS.items():
            v=r.headers.get(h,'').lower()
            for x in vals:
                if x.lower() not in v:errors.append(f'Projects response missing {h}: {x}')
        if target=='production' and urlparse(r.url).hostname!=PROD:errors.append(f'Projects production redirected away from canonical host: {r.url}')
    except Exception as e:errors.append(str(e))
    try:
        r=fetch(urljoin(root,'__projects_v14_verifier__/missing'))
        if r.status!=404:errors.append(f'Projects missing path HTTP {r.status}; expected 404')
        exp=(DIST/'404.html').read_bytes()
        if r.body!=exp:errors.append('Projects deployed 404 body differs from exact V1.4 artifact')
    except Exception as e:errors.append(str(e))
    return errors
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--target',choices=('branch-preview','production'));ap.add_argument('--check-config',action='store_true');a=ap.parse_args()
    valid(f'https://{PROD}/')
    if a.check_config:print('Projects V1.4 deployment verifier configuration valid');return 0
    if not a.target:ap.error('--target required unless --check-config')
    errs=verify(a.target)
    if errs:
        print(f'Projects exact V1.4 deployment verification failed for {a.target}')
        for e in errs:print('- '+e)
        return 1
    print(f'Projects exact V1.4 deployment verification passed for {a.target}: {base(a.target)}');return 0
if __name__=='__main__':raise SystemExit(main())
