#!/usr/bin/env python3
"""Verify the GoreeCloud Projects deployment against the reviewed source tree."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import os
import re
import ssl
from pathlib import Path
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

SITE = Path(__file__).resolve().parent
PRODUCTION_URL = "https://projects.goreecloud.com"
PAGES_DOMAIN = "goreecloud-projects.pages.dev"
BRANCH_NAME_RE = re.compile(r"[^a-z0-9-]+")
TIMEOUT_SECONDS = 15
MAX_BODY_BYTES = 2_000_000

REMOTE_FILES = (
    "index.html",
    "404.html",
    "assets/app.js",
    "assets/icon-refresh.js",
    "assets/styles.css",
    "assets/mobile-refresh.css",
    "assets/glaze-ui-2.1.0.css",
    "assets/goreecloud-logo.svg",
    "assets/glaze-ui-mark.svg",
    "assets/everkeep.svg",
    "assets/privacy-shield-icon.svg",
    "assets/wardveil-security-icon.svg",
    "assets/goreecloud-mesh-mark.svg",
    "assets/identity.svg",
)
CRITICAL_ASSET_PATHS = (
    "/assets/app.js",
    "/assets/icon-refresh.js",
    "/assets/mobile-refresh.css",
    "/assets/glaze-ui-2.1.0.css",
)


@dataclass(frozen=True)
class Response:
    status: int
    final_url: str
    headers: Mapping[str, str]
    body: bytes


def normalize_branch_preview_label(branch: str) -> str:
    label = BRANCH_NAME_RE.sub("-", branch.strip().lower().replace("/", "-")).strip("-")
    label = re.sub(r"-+", "-", label)
    if not label:
        raise ValueError("Branch preview name resolves to an empty Cloudflare label.")
    return label[:28].rstrip("-")


def branch_preview_url() -> str:
    branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not branch:
        raise ValueError("Branch preview verification requires GITHUB_HEAD_REF or GITHUB_REF_NAME.")
    return f"https://{normalize_branch_preview_label(branch)}.{PAGES_DOMAIN}"


def target_url(target: str) -> str:
    return PRODUCTION_URL if target == "production" else branch_preview_url()


def host_is_allowed(hostname: str | None) -> bool:
    if not hostname:
        return False
    return hostname == "projects.goreecloud.com" or hostname.endswith(f".{PAGES_DOMAIN}")


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"Only HTTPS deployment targets are allowed: {url}")
    if not host_is_allowed(parsed.hostname):
        raise ValueError(f"Deployment host is outside the Projects allowlist: {url}")
    if parsed.username or parsed.password or parsed.fragment:
        raise ValueError(f"Deployment URL must not contain credentials or fragments: {url}")


class AllowlistedRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def build_url(base_url: str, path: str) -> str:
    url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    validate_url(url)
    return url


def fetch(url: str) -> Response:
    validate_url(url)
    request = Request(
        url,
        headers={
            "User-Agent": "GoreeCloud-Projects-Deployment-Verifier/1.0",
            "Accept": "*/*",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
        method="GET",
    )
    opener = build_opener(
        AllowlistedRedirectHandler(),
        HTTPSHandler(context=ssl.create_default_context()),
    )
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BODY_BYTES + 1)
            if len(body) > MAX_BODY_BYTES:
                raise RuntimeError(f"Response exceeded {MAX_BODY_BYTES} bytes: {url}")
            return Response(
                status=response.status,
                final_url=response.geturl(),
                headers={key.lower(): value for key, value in response.headers.items()},
                body=body,
            )
    except HTTPError as error:
        return Response(
            status=error.code,
            final_url=error.geturl(),
            headers={key.lower(): value for key, value in error.headers.items()},
            body=error.read(MAX_BODY_BYTES + 1),
        )
    except URLError as error:
        raise RuntimeError(f"Network request failed for {url}: {error.reason}") from error


def verify_exact_files(base_url: str, errors: list[str]) -> None:
    for relative in REMOTE_FILES:
        source = SITE / relative
        if not source.is_file() or source.is_symlink():
            errors.append(f"Reviewed Projects source is missing or unsafe: {relative}")
            continue
        path = "/" if relative == "index.html" else f"/{relative}"
        try:
            response = fetch(build_url(base_url, path))
        except RuntimeError as error:
            errors.append(str(error))
            continue
        if response.status != 200:
            errors.append(f"{path} returned HTTP {response.status}; expected 200.")
            continue
        expected = source.read_bytes()
        if response.body != expected:
            errors.append(
                f"Deployed Projects content mismatch for {path}: expected SHA-256 "
                f"{sha256(expected).hexdigest()}, deployed SHA-256 {sha256(response.body).hexdigest()}."
            )


def verify_root_contract(base_url: str, errors: list[str]) -> None:
    try:
        response = fetch(build_url(base_url, "/"))
    except RuntimeError as error:
        errors.append(str(error))
        return
    if response.status != 200:
        errors.append(f"Projects root returned HTTP {response.status}; expected 200.")
        return
    text = response.body.decode("utf-8", errors="replace")
    for marker in (
        "<title>Projects — GoreeCloud</title>",
        'name="goreecloud-glaze-ui" content="2.1.0"',
        'data-glaze-ui="2.1.0"',
        "/assets/app.js?v=20260831-source-native",
        "/assets/icon-refresh.js?v=20260828-identities1",
        "/assets/mobile-refresh.css?v=20260827-mobile2",
        "/assets/glaze-ui-2.1.0.css",
        "/assets/everkeep.svg",
        "/assets/privacy-shield-icon.svg",
        "/assets/wardveil-security-icon.svg",
        "/assets/goreecloud-mesh-mark.svg",
        "/assets/identity.svg",
        "Security Center · Sentinel Fold",
        "Mesh Center · Weave",
        "GoreeCloud Identity",
        "Identity Center",
        "GoreeCloud software portfolio",
        "Glaze UI 2.1",
    ):
        if marker not in text:
            errors.append(f"Projects root is missing production marker: {marker}")
    for forbidden in (
        "/assets/public-refresh.js",
        "Mesh Center · artwork pending approval",
        "data:image/svg+xml",
        'data-glaze-ui="1.5.0"',
        'data-glaze-ui="2.0.0"',
        "/assets/glaze-ui-2.0.0.css",
        "2.1 remains Candidate",
    ):
        if forbidden in text:
            errors.append(f"Projects root still publishes superseded or generated artwork/design marker: {forbidden}")
    csp = response.headers.get("content-security-policy", "").lower()
    for marker in (
        "default-src 'self'",
        "script-src 'self'",
        "connect-src 'none'",
        "frame-ancestors 'none'",
        "img-src 'self' https://www.goreecloud.com",
    ):
        if marker not in csp:
            errors.append(f"Projects root CSP is missing: {marker}")
    for forbidden in ("data:", "raw.githubusercontent.com", "githubusercontent.com"):
        if forbidden in csp:
            errors.append(f"Projects root CSP permits an unauthorized branding image source: {forbidden}")
    if response.headers.get("x-content-type-options", "").lower() != "nosniff":
        errors.append("Projects root is missing X-Content-Type-Options: nosniff.")


def verify_critical_asset_cache(base_url: str, errors: list[str]) -> None:
    for path in CRITICAL_ASSET_PATHS:
        try:
            response = fetch(build_url(base_url, path))
        except RuntimeError as error:
            errors.append(str(error))
            continue
        if response.status != 200:
            errors.append(f"{path} returned HTTP {response.status}; expected 200.")
            continue
        cache_control = response.headers.get("cache-control", "").lower()
        if "max-age=0" not in cache_control or "must-revalidate" not in cache_control:
            errors.append(
                f"{path} must revalidate mutable Projects assets; got Cache-Control {cache_control!r}."
            )
        for forbidden in ("max-age=86400", "stale-while-revalidate"):
            if forbidden in cache_control:
                errors.append(f"{path} still exposes stale cache directive: {forbidden}")


def verify_not_found(base_url: str, errors: list[str]) -> None:
    path = "/__projects_deployment_verifier__/missing"
    try:
        response = fetch(build_url(base_url, path))
    except RuntimeError as error:
        errors.append(str(error))
        return
    if response.status != 404:
        errors.append(f"Projects missing path returned HTTP {response.status}; expected 404.")


def verify(target: str) -> int:
    base_url = target_url(target)
    validate_url(base_url)
    errors: list[str] = []
    verify_exact_files(base_url, errors)
    verify_root_contract(base_url, errors)
    verify_critical_asset_cache(base_url, errors)
    verify_not_found(base_url, errors)
    if errors:
        print(f"Projects remote deployment verification failed for {target}: {base_url}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Projects remote deployment verification passed for {target}: {base_url}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("branch-preview", "production"), required=True)
    args = parser.parse_args()
    return verify(args.target)


if __name__ == "__main__":
    raise SystemExit(main())
