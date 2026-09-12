#!/usr/bin/env python3
from pathlib import Path
import argparse
import re

EXPECTED_REPOS={
'goreecloud-ai','goreecloud-index','goreecloud-code','goreecloud-terminal','goreecloud-home','goreecloud-home-security','goreecloud-router-os','goreecloud-boot','goreecloud-containers','goreecloud-app-store','goreecloud-sync','goreecloud-gateway','goreecloud-network','goreecloud-dns','goreecloud-monitor','goreecloud-search','goreecloud-browser','goreecloud-photos','goreecloud-video','goreecloud-music','goreecloud-messenger','goreecloud-launcher','goreecloud-health','goreecloud-reader','goreecloud-social','goreecloud-location','goreecloud-firefox-extensions'}
PLATFORM_HOSTS={'manage.goreecloud.com','id.goreecloud.com','design.goreecloud.com','security.goreecloud.com','privacy.goreecloud.com','everkeep.goreecloud.com','mesh.goreecloud.com'}

def require(ok,msg):
    if not ok: raise SystemExit(msg)

def validate(root:Path):
    required=['index.html','404.html','site.css','site.js','_headers','robots.txt','sitemap.xml','assets/goreecloud-logo.svg']
    for name in required: require((root/name).is_file(),f'missing {name}')
    html=(root/'index.html').read_text()
    headers=(root/'_headers').read_text()
    robots=(root/'robots.txt').read_text()
    require('https://labs.goreecloud.com/' in html,'canonical Labs URL missing')
    require('name="goreecloud-glaze-ui" content="1.3.0"' in html,'Glaze UI V1.3 marker missing')
    require('name="robots" content="noindex,nofollow"' in html,'candidate indexing boundary missing')
    require(html.count('data-workstream')==27,f'expected 27 Labs workstreams, found {html.count("data-workstream")}')
    require(html.count('data-lane=')==6,f'expected 6 Labs lanes, found {html.count("data-lane=")}')
    for repo in EXPECTED_REPOS: require(f'https://github.com/GoreeCloud/{repo}' in html,f'missing Labs source link: {repo}')
    for host in PLATFORM_HOSTS: require(f'https://{host}/' in html,f'missing platform-system link: {host}')
    require('45' in html and 'Suite products' in html,'Suite boundary metric missing')
    require('7' in html and 'Integral Platform Systems' in html,'platform-system boundary metric missing')
    require('Strict-Transport-Security: max-age=31536000' in headers,'HSTS missing')
    require("Content-Security-Policy: default-src 'self'" in headers,'CSP missing')
    require('Disallow: /' in robots,'candidate robots boundary missing')
    require('fonts.googleapis.com' not in html and 'fonts.gstatic.com' not in html,'external fonts are not allowed')
    require(not re.search(r'<script[^>]+src=["\']https?://',html,re.I),'external script is not allowed')
    print(f'Labs validation passed: {root}')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('root',nargs='?',default='.')
    args=parser.parse_args();validate(Path(args.root).resolve())
