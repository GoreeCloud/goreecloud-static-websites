#!/usr/bin/env python3
"""Verify an approved GoreeCloud Main deployment against the exact V1.3 candidate.

Only the canonical production hostname and GoreeCloud's fixed Cloudflare Pages
project namespace are accepted. Every fetchable public artifact file, including the
complete pinned GLAZE UI V1.3 CSS dependency closure, must match byte-for-byte.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import os
import re
import ssl
from pathlib import Path
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener
import sys

from build_public_site import GENERATED_HTML, PUBLIC_FILES, ROOT
from glaze_v1_3 import collect_glaze_css
from normalize_homepage import normalize_homepage
from render_repository_portfolio import load_manifest, render_public_file

PRODUCTION_URL = "https://www.goreecloud.com"
PAGES_DOMAIN = "goreecloud-website.pages.dev"
DEFAULT_BRANCH_PREVIEW_URL = "https://agent-glaze-ui-interaction-p.goreecloud-website.pages.dev"
ALLOWED_HOSTS = {"www.goreecloud.com", "goreecloud.com"}
BRANCH_NAME_RE = re.compile(r"[^a-z0-9-]+")
NON_FETCHABLE = frozenset({"_headers"})
TIMEOUT_SECONDS = 15
MAX_BODY_BYTES = 2_097_152
SECURITY_RENEWAL_BUFFER = timedelta(days=30)

REQUIRED_HEADERS = {
    "content-security-policy": ("default-src 'self'", "script-src 'self'", "style-src 'self'", "frame-ancestors 'none'", "connect-src 'none'"),
    "permissions-policy": ("camera=()", "geolocation=()", "microphone=()"),
    "referrer-policy": ("no-referrer",),
    "x-content-type-options": ("nosniff",),
    "x-frame-options": ("DENY",),
    "strict-transport-security": ("max-age=31536000",),
}


@dataclass(frozen=True)
class Response:
    status: int
    final_url: str
    headers: Mapping[str, str]
    body: bytes


def branch_preview_url() -> str:
    branch = os.environ.get("GITHUB_HEAD_REF", "").strip()
    if not branch:
        return DEFAULT_BRANCH_PREVIEW_URL
    label = BRANCH_NAME_RE.sub("-", branch.lower().replace("/", "-")).strip("-")
    label = re.sub(r"-+", "-", label)[:28].rstrip("-")
    if not label:
        raise ValueError("branch preview label is empty")
    return f"https://{label}.{PAGES_DOMAIN}"


def host_allowed(hostname: str | None) -> bool:
    return bool(hostname and (hostname in ALLOWED_HOSTS or hostname.endswith(f".{PAGES_DOMAIN}")))


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not host_allowed(parsed.hostname):
        raise ValueError(f"deployment verifier target is outside approved HTTPS hosts: {url}")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(f"deployment verifier target contains unsupported URL components: {url}")


class SafeRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url: str) -> Response:
    validate_url(url)
    request = Request(url, headers={"User-Agent": "GoreeCloud-Deployment-Verifier/1.3", "Accept-Encoding": "identity"}, method="GET")
    opener = build_opener(SafeRedirects(), HTTPSHandler(context=ssl.create_default_context()))
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BODY_BYTES + 1)
            if len(body) > MAX_BODY_BYTES:
                raise RuntimeError(f"response exceeded verifier limit: {url}")
            return Response(response.status, response.geturl(), {k.lower(): v for k, v in response.headers.items()}, body)
    except HTTPError as exc:
        body = exc.read(MAX_BODY_BYTES + 1)
        return Response(exc.code, exc.geturl(), {k.lower(): v for k, v in exc.headers.items()}, body)
    except URLError as exc:
        raise RuntimeError(f"network request failed for {url}: {exc.reason}") from exc


def candidate_files() -> dict[str, bytes]:
    manifest = load_manifest(ROOT)
    files: dict[str, bytes] = {}
    for relative in PUBLIC_FILES:
        if relative in NON_FETCHABLE:
            continue
        source = ROOT / relative
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"candidate source unavailable or unsafe: {relative}")
        if relative.endswith(".html"):
            text = source.read_text(encoding="utf-8")
            if relative in GENERATED_HTML:
                text = render_public_file(relative, text, manifest)
                if relative == "index.html":
                    text = normalize_homepage(text)
            files[relative] = text.encode("utf-8")
        else:
            files[relative] = source.read_bytes()
    for name, data in collect_glaze_css(ROOT).items():
        files[f"css/{name}"] = data
    return files


def remote_path(relative: str) -> str:
    if relative == "index.html":
        return "/"
    if relative.startswith("/") or ".." in Path(relative).parts:
        raise ValueError(f"unsafe public integrity path: {relative}")
    return f"/{relative}"


def verify_security_txt(base: str, errors: list[str]) -> None:
    response = fetch(urljoin(base.rstrip("/") + "/", ".well-known/security.txt"))
    if response.status != 200:
        errors.append(f"security.txt returned HTTP {response.status}")
        return
    text = response.body.decode("utf-8", errors="replace")
    for marker in (
        "Contact: mailto:security@goreecloud.com",
        "Canonical: https://www.goreecloud.com/.well-known/security.txt",
        "Preferred-Languages: en",
    ):
        if marker not in text:
            errors.append(f"deployed security.txt missing: {marker}")
    match = re.search(r"^Expires:\s*(.+)$", text, re.MULTILINE)
    if not match:
        errors.append("deployed security.txt has no Expires field")
        return
    try:
        expires = datetime.fromisoformat(match.group(1).strip().replace("Z", "+00:00")).astimezone(timezone.utc)
        if expires <= datetime.now(timezone.utc) + SECURITY_RENEWAL_BUFFER:
            errors.append("deployed security.txt expires within the required renewal buffer")
    except ValueError:
        errors.append("deployed security.txt Expires value is invalid")


def verify(base: str) -> list[str]:
    validate_url(base)
    errors: list[str] = []
    try:
        expected = candidate_files()
    except (OSError, ValueError) as exc:
        return [str(exc)]

    for relative, expected_bytes in sorted(expected.items()):
        url = urljoin(base.rstrip("/") + "/", remote_path(relative).lstrip("/"))
        try:
            response = fetch(url)
        except (RuntimeError, ValueError) as exc:
            errors.append(str(exc)); continue
        if response.status != 200:
            errors.append(f"{remote_path(relative)} returned HTTP {response.status}; expected 200")
            continue
        if response.body != expected_bytes:
            errors.append(
                f"candidate mismatch for {remote_path(relative)}: expected {sha256(expected_bytes).hexdigest()}, deployed {sha256(response.body).hexdigest()}"
            )

    try:
        root = fetch(base.rstrip("/") + "/")
        for header, fragments in REQUIRED_HEADERS.items():
            value = root.headers.get(header, "")
            for fragment in fragments:
                if fragment not in value:
                    errors.append(f"required response header missing {header}: {fragment}")
    except RuntimeError as exc:
        errors.append(str(exc))

    try:
        missing = fetch(base.rstrip("/") + "/__goreecloud-deployment-smoke__/missing/path")
        if missing.status != 404:
            errors.append(f"missing-path check returned HTTP {missing.status}; expected 404")
    except RuntimeError as exc:
        errors.append(str(exc))

    try:
        verify_security_txt(base, errors)
    except (RuntimeError, ValueError) as exc:
        errors.append(str(exc))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", choices=("branch-preview", "production"))
    args = parser.parse_args()
    base = branch_preview_url() if args.target == "branch-preview" else PRODUCTION_URL
    errors = verify(base)
    if errors:
        print(f"Remote deployment verification failed for {base}:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"Remote deployment verification passed for exact GLAZE UI V1.3 candidate at {base}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
