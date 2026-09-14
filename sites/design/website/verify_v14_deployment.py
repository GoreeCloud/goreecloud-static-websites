#!/usr/bin/env python3
"""Verify a governed Design Center GLAZE UI V1.4 deployment against exact dist bytes."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import re
import ssl
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

SITE = Path(__file__).resolve().parent
DIST = SITE / "dist"
PRODUCTION_URL = "https://design.goreecloud.com"
PAGES_DOMAIN = "goreecloud-design.pages.dev"
REVISION = "84cb3db4884042f0fa25ed6d475a127fb110f596"
BRANCH_NAME_RE = re.compile(r"[^a-z0-9-]+")
TIMEOUT = 15
MAX_BYTES = 2_097_152
NON_FETCHABLE = frozenset({"_headers"})
REQUIRED_HEADERS = {
    "content-security-policy": ("default-src 'self'", "script-src 'self'", "style-src 'self'", "connect-src 'none'", "frame-ancestors 'none'", "object-src 'none'"),
    "permissions-policy": ("camera=()", "geolocation=()", "microphone=()"),
    "x-content-type-options": ("nosniff",),
    "x-frame-options": ("DENY",),
    "cross-origin-opener-policy": ("same-origin",),
    "cross-origin-resource-policy": ("same-origin",),
    "strict-transport-security": ("max-age=31536000",),
}

@dataclass(frozen=True)
class Response:
    status: int
    final_url: str
    headers: Mapping[str, str]
    body: bytes

def branch_label() -> str:
    raw = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not raw:
        raise ValueError("branch preview verification requires GITHUB_HEAD_REF or GITHUB_REF_NAME")
    label = BRANCH_NAME_RE.sub("-", raw.lower().replace("/", "-")).strip("-")
    label = re.sub(r"-+", "-", label)[:28].rstrip("-")
    if not label:
        raise ValueError("Design Center branch preview label is empty")
    return label

def target_url(target: str) -> str:
    return PRODUCTION_URL if target == "production" else f"https://{branch_label()}.{PAGES_DOMAIN}"

def validate_url(url: str) -> None:
    parsed = urlparse(url)
    allowed = parsed.hostname == "design.goreecloud.com" or bool(parsed.hostname and parsed.hostname.endswith(f".{PAGES_DOMAIN}"))
    if parsed.scheme != "https" or not allowed:
        raise ValueError(f"Design Center V1.4 verifier target outside approved HTTPS hosts: {url}")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(f"unsupported URL components: {url}")

class SafeRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch(url: str) -> Response:
    validate_url(url)
    request = Request(url, headers={"User-Agent":"GoreeCloud-Design-Deployment-Verifier/1.4","Accept-Encoding":"identity","Cache-Control":"no-cache","Pragma":"no-cache"}, method="GET")
    opener = build_opener(SafeRedirects(), HTTPSHandler(context=ssl.create_default_context()))
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                raise RuntimeError(f"response exceeded verifier limit: {url}")
            return Response(response.status, response.geturl(), {k.lower():v for k,v in response.headers.items()}, body)
    except HTTPError as error:
        return Response(error.code, error.geturl(), {k.lower():v for k,v in error.headers.items()}, error.read(MAX_BYTES + 1))
    except URLError as error:
        raise RuntimeError(f"network request failed for {url}: {error.reason}") from error

def candidate_files() -> dict[str, bytes]:
    if not DIST.is_dir():
        raise ValueError("Design Center V1.4 dist missing; run build_v14.py first")
    result = {}
    for path in sorted(DIST.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Design Center artifact contains symlink: {path}")
        if path.is_file():
            rel = path.relative_to(DIST).as_posix()
            if rel not in NON_FETCHABLE:
                result[rel] = path.read_bytes()
    if "index.html" not in result or "404.html" not in result:
        raise ValueError("Design Center V1.4 artifact incomplete")
    return result

def remote_path(relative: str) -> str:
    return "/" if relative == "index.html" else f"/{relative}"

def verify(target: str) -> int:
    base = target_url(target)
    validate_url(base)
    errors = []
    try:
        expected = candidate_files()
    except ValueError as error:
        errors.append(str(error)); expected = {}
    for relative, expected_bytes in sorted(expected.items()):
        url = urljoin(base.rstrip("/") + "/", remote_path(relative).lstrip("/"))
        try:
            response = fetch(url)
        except Exception as error:
            errors.append(str(error)); continue
        if response.status != 200:
            errors.append(f"{remote_path(relative)} returned HTTP {response.status}; expected 200"); continue
        if response.body != expected_bytes:
            errors.append(f"candidate mismatch for {remote_path(relative)}: expected {sha256(expected_bytes).hexdigest()}, deployed {sha256(response.body).hexdigest()}")
    try:
        root = fetch(base.rstrip("/") + "/")
        text = root.body.decode("utf-8", errors="replace")
        for marker in (
            "<title>GoreeCloud Design Center — GLAZE UI V1.4</title>",
            'name="goreecloud-glaze-ui" content="1.4.0"',
            f'name="goreecloud-glaze-source-revision" content="{REVISION}"',
            'name="goreecloud-glaze-consumer-state" content="build-migrated-rendered-acceptance-pending"',
            "Current Official Stable · 1.4.0",
        ):
            if marker not in text:
                errors.append(f"Design Center root missing V1.4 marker: {marker}")
        for header, fragments in REQUIRED_HEADERS.items():
            value = root.headers.get(header, "")
            for fragment in fragments:
                if fragment not in value:
                    errors.append(f"required response header missing {header}: {fragment}")
        if target == "production" and urlparse(root.final_url).hostname != "design.goreecloud.com":
            errors.append(f"canonical Design Center root redirected away from production host: {root.final_url}")
    except Exception as error:
        errors.append(str(error))
    try:
        missing = fetch(base.rstrip("/") + "/__goreecloud_design_v14_verifier__/missing")
        if missing.status != 404:
            errors.append(f"Design Center missing-path check returned HTTP {missing.status}; expected 404")
    except Exception as error:
        errors.append(str(error))
    if errors:
        print(f"Design Center V1.4 remote verification failed for {target}: {base}")
        for error in errors: print(f"- {error}")
        return 1
    print(f"Design Center exact GLAZE UI V1.4 remote verification passed for {target}: {base}")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("branch-preview","production"))
    parser.add_argument("--check-config", action="store_true")
    args = parser.parse_args()
    validate_url(PRODUCTION_URL)
    if args.check_config:
        print("Design Center V1.4 deployment verifier configuration is valid; live verification remains separate")
        return 0
    if not args.target:
        parser.error("--target is required unless --check-config is used")
    return verify(args.target)

if __name__ == "__main__":
    raise SystemExit(main())
