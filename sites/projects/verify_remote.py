#!/usr/bin/env python3
"""Verify GoreeCloud Projects deployment against the exact reviewed static source."""

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
PRODUCTION_URL = "https://projects.goreecloud.com/"
PRODUCTION_HOST = "projects.goreecloud.com"
PAGES_DOMAIN = "goreecloud-projects.pages.dev"
BRANCH_NAME_RE = re.compile(r"[^a-z0-9-]+")
TIMEOUT_SECONDS = 15
MAX_BODY_BYTES = 2_000_000
GLAZE_REVISION = "8354308445da9ac35ced2b37a7f503a08a0aaf72"

REMOTE_FILES = (
    "index.html",
    "404.html",
    "assets/app.js",
    "assets/suite-portfolio.js",
    "assets/icon-refresh.js",
    "assets/styles.css",
    "assets/mobile-refresh.css",
    "assets/glaze-v1.3-consumer.css",
    "assets/goreecloud-logo.svg",
    "assets/manager.svg",
    "assets/glaze-ui-mark.svg",
    "assets/everkeep.svg",
    "assets/privacy-shield-icon.svg",
    "assets/wardveil-security-icon.svg",
    "assets/goreecloud-mesh-mark.svg",
    "assets/identity.svg",
)
CRITICAL_ASSET_PATHS = (
    "/assets/app.js",
    "/assets/suite-portfolio.js",
    "/assets/icon-refresh.js",
    "/assets/mobile-refresh.css",
    "/assets/glaze-v1.3-consumer.css",
)
REQUIRED_HEADER_MARKERS = {
    "content-security-policy": (
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self'",
        "img-src 'self' https://www.goreecloud.com",
        "font-src 'none'",
        "connect-src 'none'",
        "object-src 'none'",
        "base-uri 'none'",
        "form-action 'none'",
        "frame-ancestors 'none'",
        "upgrade-insecure-requests",
    ),
    "strict-transport-security": ("max-age=31536000",),
    "x-content-type-options": ("nosniff",),
    "x-frame-options": ("deny",),
    "referrer-policy": ("no-referrer",),
    "permissions-policy": ("camera=()", "microphone=()", "geolocation=()", "payment=()", "usb=()"),
    "cross-origin-opener-policy": ("same-origin",),
    "x-permitted-cross-domain-policies": ("none",),
    "origin-agent-cluster": ("?1",),
}


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
    return f"https://{normalize_branch_preview_label(branch)}.{PAGES_DOMAIN}/"


def target_url(target: str) -> str:
    return PRODUCTION_URL if target == "production" else branch_preview_url()


def host_is_allowed(hostname: str | None) -> bool:
    if not hostname:
        return False
    return hostname == PRODUCTION_HOST or hostname.endswith(f".{PAGES_DOMAIN}")


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"Only HTTPS deployment targets are allowed: {url}")
    if not host_is_allowed(parsed.hostname):
        raise ValueError(f"Deployment host is outside the Projects allowlist: {url}")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(f"Deployment URL must not contain credentials, query, or fragment: {url}")


def validate_configuration() -> None:
    validate_url(PRODUCTION_URL)
    for relative in REMOTE_FILES + ("_headers",):
        source = SITE / relative
        if not source.is_file() or source.is_symlink():
            raise SystemExit(f"Reviewed Projects source is missing or unsafe: {relative}")
    headers = (SITE / "_headers").read_text(encoding="utf-8")
    for header, markers in REQUIRED_HEADER_MARKERS.items():
        for marker in markers:
            if marker.lower() not in headers.lower():
                raise SystemExit(f"Projects committed header contract is missing {header}: {marker}")


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
            "User-Agent": "GoreeCloud-Projects-Deployment-Verifier/2.0",
            "Accept": "*/*",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
        method="GET",
    )
    opener = build_opener(AllowlistedRedirectHandler(), HTTPSHandler(context=ssl.create_default_context()))
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BODY_BYTES + 1)
            if len(body) > MAX_BODY_BYTES:
                raise RuntimeError(f"Response exceeded {MAX_BODY_BYTES} bytes: {url}")
            return Response(response.status, response.geturl(), {k.lower(): v for k, v in response.headers.items()}, body)
    except HTTPError as error:
        body = error.read(MAX_BODY_BYTES + 1)
        if len(body) > MAX_BODY_BYTES:
            raise RuntimeError(f"Error response exceeded {MAX_BODY_BYTES} bytes: {url}")
        return Response(error.code, error.geturl(), {k.lower(): v for k, v in error.headers.items()}, body)
    except URLError as error:
        raise RuntimeError(f"Network request failed for {url}: {error.reason}") from error


def verify_exact_files(base_url: str, errors: list[str]) -> None:
    for relative in REMOTE_FILES:
        source = SITE / relative
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


def verify_root_contract(base_url: str, target: str, errors: list[str]) -> None:
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
        '<link rel="canonical" href="https://projects.goreecloud.com/">',
        'name="goreecloud-glaze-ui" content="1.3.0"',
        f'name="goreecloud-glaze-source-revision" content="{GLAZE_REVISION}"',
        'data-glaze-ui="1.3.0"',
        '<strong id="app-count">45</strong><span>Suite products</span>',
        '<strong id="foundation-count">7</strong><span>Integral platform systems</span>',
        "GoreeCloud Vault",
        "GoreeCloud Health",
        "GoreeCloud Reader",
        "GoreeCloud Router OS",
        "Security Center · Sentinel Fold",
        "Mesh Center · Weave",
        "GoreeCloud Manager",
        "Identity Center",
        "GLAZE UI V1.3",
    ):
        if marker not in text:
            errors.append(f"Projects root is missing production marker: {marker}")
    for forbidden in (
        "GoreeVault",
        "/assets/public-refresh.js",
        "/assets/glaze-ui-2.1.0.css",
        "/assets/glaze-ui-2.0.0.css",
        "Mesh Center · artwork pending approval",
        "data:image/svg+xml",
        'data-glaze-ui="1.5.0"',
        'data-glaze-ui="2.0.0"',
        'data-glaze-ui="2.1.0"',
        "27 current Suite applications",
    ):
        if forbidden in text:
            errors.append(f"Projects root still publishes superseded marker: {forbidden}")
    for header, markers in REQUIRED_HEADER_MARKERS.items():
        value = response.headers.get(header, "")
        if not value:
            errors.append(f"Projects root is missing required response header: {header}")
            continue
        for marker in markers:
            if marker.lower() not in value.lower():
                errors.append(f"Projects root {header} is missing required value: {marker}")
    csp = response.headers.get("content-security-policy", "").lower()
    for forbidden in ("data:", "raw.githubusercontent.com", "githubusercontent.com"):
        if forbidden in csp:
            errors.append(f"Projects root CSP permits unauthorized image source: {forbidden}")
    if response.headers.get("server", "").lower() != "cloudflare":
        errors.append(f"Projects expected Cloudflare delivery; got server={response.headers.get('server', '')!r}")
    if target == "production" and urlparse(response.final_url).hostname != PRODUCTION_HOST:
        errors.append(f"Projects production root drifted from canonical host: {response.final_url}")


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
            errors.append(f"{path} must revalidate mutable Projects assets; got Cache-Control {cache_control!r}.")
        for forbidden in ("max-age=86400", "stale-while-revalidate"):
            if forbidden in cache_control:
                errors.append(f"{path} still exposes stale cache directive: {forbidden}")


def verify_not_found(base_url: str, target: str, errors: list[str]) -> None:
    path = "/__projects_deployment_verifier__/missing"
    try:
        response = fetch(build_url(base_url, path))
    except RuntimeError as error:
        errors.append(str(error))
        return
    if response.status != 404:
        errors.append(f"Projects missing path returned HTTP {response.status}; expected 404.")
    expected = (SITE / "404.html").read_bytes()
    if response.body != expected:
        errors.append(
            "Projects deployed 404 body differs from reviewed 404.html: "
            f"expected SHA-256 {sha256(expected).hexdigest()}, deployed SHA-256 {sha256(response.body).hexdigest()}."
        )
    if response.headers.get("server", "").lower() != "cloudflare":
        errors.append(f"Projects 404 expected Cloudflare delivery; got server={response.headers.get('server', '')!r}")
    if target == "production" and urlparse(response.final_url).hostname != PRODUCTION_HOST:
        errors.append(f"Projects production 404 drifted from canonical host: {response.final_url}")


def verify(target: str) -> int:
    base_url = target_url(target)
    validate_url(base_url)
    errors: list[str] = []
    verify_exact_files(base_url, errors)
    verify_root_contract(base_url, target, errors)
    verify_critical_asset_cache(base_url, errors)
    verify_not_found(base_url, target, errors)
    if errors:
        print(f"Projects remote deployment verification failed for {target}: {base_url}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Projects V1.3 / Suite-45 exact deployment verification passed for {target}: {base_url}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("branch-preview", "production"))
    parser.add_argument("--check-config", action="store_true")
    args = parser.parse_args()
    validate_configuration()
    if args.check_config:
        print("Projects production verifier configuration is valid; live verification remains separately gated.")
        return 0
    if not args.target:
        parser.error("--target is required unless --check-config is used")
    return verify(args.target)


if __name__ == "__main__":
    raise SystemExit(main())
