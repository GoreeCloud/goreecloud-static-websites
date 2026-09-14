#!/usr/bin/env python3
"""Validate retained Mesh Center source or exact GLAZE UI V1.4 publication artifact."""
from pathlib import Path
from html.parser import HTMLParser
import argparse, hashlib, json, re, sys
ROOT=Path(__file__).resolve().parents[1]; SOURCE=ROOT/"website"; DIST=ROOT/"dist"
p=argparse.ArgumentParser(); p.add_argument("--dist",action="store_true"); args=p.parse_args(); BASE=DIST if args.dist else SOURCE; errors=[]
SOURCE_COMMIT="8354308445da9ac35ced2b37a7f503a08a0aaf72"; PUB_COMMIT="84cb3db4884042f0fa25ed6d475a127fb110f596"; PUB_ENTRY="glaze-v1.4.0.css"; PUB_BLOB="d48a9bc317090d152799769271de0fb4325494c4"; IMPORT_RE=re.compile(r'@import\s+(?:url\()?\s*["\']?\.\/([^"\')\s;]+)',re.I)
def check(c,m):
    if not c: errors.append(m)
def blob_sha(path):
    d=path.read_bytes(); return hashlib.sha1(b"blob "+str(len(d)).encode()+b"\0"+d,usedforsecurity=False).hexdigest()
class Audit(HTMLParser):
    def handle_starttag(self,tag,attrs):
        v=dict(attrs)
        if "style" in v: errors.append("inline style attributes are forbidden by the public-site CSP")
        if tag=="script" and not v.get("src"): errors.append("inline scripts are forbidden by the public-site CSP")
        src=v.get("src","")
        if src.startswith(("http://","https://","//")): errors.append(f"remote runtime source is forbidden: {src}")
        if tag=="link":
            href=v.get("href",""); rel=v.get("rel","")
            if href.startswith(("http://","https://","//")) and "canonical" not in rel.split(): errors.append(f"remote runtime link is forbidden: {href}")
        if tag=="a" and v.get("href","").startswith("http://"): errors.append(f"external navigation must use HTTPS: {v.get('href')}")
def closure(entry):
    seen=set()
    def visit(name):
        if name in seen:return
        path=DIST/"assets"/name; check(Path(name).name==name and name.endswith(".css"),f"unsafe built Glaze dependency: {name}"); check(path.is_file() and not path.is_symlink(),f"missing built Glaze dependency: {name}")
        if not path.is_file() or path.is_symlink():return
        seen.add(name)
        for s in re.findall(r"@import[^;]+;",path.read_text(),flags=re.I):
            check("http://" not in s.lower() and "https://" not in s.lower() and "//" not in s,f"remote built Glaze import: {s}"); m=IMPORT_RE.search(s); check(m is not None,f"unsupported built Glaze import: {s}")
            if m: visit(m.group(1))
    visit(entry); return seen
lock=json.loads((SOURCE/"glaze.lock.json").read_text())
for k,e in {"version":"1.4.0","lifecycle":"Stable","repository":"GoreeCloud/goreecloud-glaze-ui","stable_commit":PUB_COMMIT,"entrypoint":PUB_ENTRY,"entrypoint_blob":PUB_BLOB,"consumer_state":"build-migrated-rendered-acceptance-pending"}.items(): check(lock.get(k)==e,f"Mesh current publication lock mismatch for {k}: {lock.get(k)!r}")
html=(BASE/"index.html").read_text(); nf=(BASE/"404.html").read_text(); css=(BASE/"assets"/"site.css" if args.dist else SOURCE/"site.css").read_text(); v13=(BASE/"assets"/"v1.3-site.css" if args.dist else SOURCE/"v1.3-site.css").read_text(); js=(BASE/"assets"/"site.js" if args.dist else SOURCE/"site.js").read_text()
for page in (BASE/"index.html",BASE/"404.html"): Audit().feed(page.read_text())
required=(('data-glaze-version="1.4.0"','name="goreecloud-glaze-ui" content="1.4.0"',f'name="goreecloud-glaze-source-revision" content="{PUB_COMMIT}"','name="goreecloud-glaze-consumer-state" content="build-migrated-rendered-acceptance-pending"','/assets/glaze-v1.4.0.css') if args.dist else ('data-glaze-version="1.3.0"','name="goreecloud-glaze-ui" content="1.3.0"',f'name="goreecloud-glaze-source-revision" content="{SOURCE_COMMIT}"','name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"','/assets/glaze-v1.3.0.css'))
for n,t in (("index",html),("404",nf)):
    for m in required: check(m in t,f"{n}: missing Mesh {'V1.4 publication' if args.dist else 'V1.3 template'} marker: {m}")
    for stale in ('data-glaze-version="2.2.0"','name="goreecloud-glaze-ui" content="2.2.0"','/assets/glaze-2.2.0.css','Glaze UI 2.2 Stable'): check(stale not in t,f"{n}: superseded Glaze marker remains: {stale}")
for m in ("--mesh-v13-control:48px","--mesh-v13-control-coarse:56px","pointer:coarse","prefers-reduced-motion:reduce","prefers-reduced-transparency:reduce","prefers-contrast:more","forced-colors:active","focus-visible","@media print"): check(m in v13,f"missing inherited Mesh V1.3 adaptation marker: {m}")
for m in ("prefers-reduced-motion:reduce","forced-colors:active","prefers-contrast:more","data-reduce-transparency"): check(m in css,f"base adaptation missing: {m}")
check("localStorage" in js and all(c in js for c in ("system","light","dark")),"appearance modes missing"); check("fonts.googleapis" not in html+css+v13,"remote fonts are forbidden"); check("googletagmanager" not in html.lower() and "segment.com" not in html.lower(),"analytics/tracker runtime is forbidden")
headers=(BASE/"_headers").read_text()
for m in ("Content-Security-Policy:","connect-src 'none'","Strict-Transport-Security: max-age=31536000","Referrer-Policy: no-referrer"): check(m in headers,f"Mesh security-header contract missing: {m}")
mark=SOURCE/"assets"/"goreecloud-mesh-mark.svg"; check(mark.exists() and not mark.is_symlink(),"Mesh mark missing or unsafe")
if mark.exists(): check(blob_sha(mark)=="5362a52bd9fb38379f083a4d894934ed1acf9b67","Mesh mark diverged from canonical branding asset")
for m in ("authority_transfer = false",'rel="canonical" href="https://mesh.goreecloud.com/"',"Production acceptance stays explicit","Mesh itself remains in Development","Mesh Center remains planned","8da8e52593dad045ed2356182b7ba755b789b79f"): check(m in html,f"Mesh public truth boundary missing: {m}")
if args.dist:
    entry=DIST/"assets"/PUB_ENTRY; check(entry.is_file() and not entry.is_symlink(),"built GLAZE UI V1.4 entrypoint missing")
    if entry.is_file(): check(blob_sha(entry)==PUB_BLOB,"built GLAZE UI V1.4 entrypoint integrity mismatch"); closure(PUB_ENTRY)
    check(css.startswith('@import url("./v1.3-site.css");'),"built Mesh CSS does not activate inherited V1.3 adaptation")
    built=DIST/"assets"/mark.name; check(built.exists(),f"missing built product mark: {mark.name}")
    if built.exists(): check(blob_sha(built)==blob_sha(mark),f"built product mark integrity mismatch: {mark.name}")
if errors:
    print("Mesh public website validation failed:",file=sys.stderr)
    for e in errors: print(" - "+e,file=sys.stderr)
    raise SystemExit(1)
print(f"Mesh public website validation passed ({'V1.4 artifact' if args.dist else 'retained V1.3 source template'}); runtime and production acceptance remain separate")
