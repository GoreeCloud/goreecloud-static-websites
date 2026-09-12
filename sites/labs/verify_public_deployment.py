#!/usr/bin/env python3
"""Verify labs.goreecloud.com against the exact reviewed GoreeCloud Labs artifact."""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
PRODUCTION_URL = "https://labs.goreecloud.com/"
EXPECTED_HOST = "labs.goreecloud.com"
MAX_BODY_BYTES = 2_000_000
REQUEST_TIMEOUT_SECONDS = 12
RETRY_ATTEMPTS = 18
RETRY_DELAY_SECONDS = 10

REQUIRED_HEADER_MARKERS = {
    "content-security-policy": (
        "default-src 'self'",
        "frame-ancestors 'none'",
        "form-action 'none'",
        "object-src 'none'",
    ),
    "strict-transport-security": ("max-age=31536000",),
    "x-content-type-options": ("nosniff",),
    "x-frame-options": ("DENY",),
    "referrer-policy": ("no-referrer",),
    "cross-origin-opener-policy": ("same-origin",),
    "cross-origin-resource-policy": ("same-origin",),
}


class SameHostRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname != EXPECTED_HOST:
            raise URLError(f"redirect outside canonical Labs host rejected: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def validate_configuration() -> None:
    parsed = urlparse(PRODUCTION_URL)
    if parsed.scheme != "https" or parsed.hostname != EXPECTED_HOST:
        raise SystemExit("Labs production verifier must remain fixed to the canonical HTTPS host")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise SystemExit("Labs production verifier target must not contain credentials, query, or fragment")
    for relative in (
        "index.html",
        "404.html",
        "site.css",
        "site.js",
        "_headers",
        "robots.txt",
        "sitemap.xml",
        "assets/goreecloud-logo.svg",
    ):
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"missing or unsafe reviewed Labs source: {relative}")


def validate_artifact() -> None:
    required = (
        "index.html",
        "404.html",
        "site.css",
        "site.js",
        "_headers",
        "robots.txt",
        "sitemap.xml",
        "assets/goreecloud-logo.svg",
    )
    for relative in required:
        path = DIST / relative
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"missing or unsafe reviewed Labs artifact: {relative}; run build.py first")


def fetch(path: str) -> tuple[int, str, dict[str, str], bytes]:
    if not path.startswith("/"):
        raise ValueError("remote path must be origin-rooted")
    url = urljoin(PRODUCTION_URL, path.lstrip("/"))
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != EXPECTED_HOST:
        raise ValueError(f"remote URL escaped canonical Labs host: {url}")
    request = Request(
        url,
        headers={
            "User-Agent": "GoreeCloud-Labs-Publication-Verifier/1.0",
            "Accept": "*/*",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
        },
        method="GET",
    )
    opener = build_opener(SameHostRedirectHandler(), HTTPSHandler(context=ssl.create_default_context()))
    try:
        with opener.open(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BODY_BYTES + 1)
            if len(body) > MAX_BODY_BYTES:
                raise RuntimeError(f"response too large: {path}")
            return response.status, response.geturl(), {k.lower(): v for k, v in response.headers.items()}, body
    except HTTPError as error:
        body = error.read(MAX_BODY_BYTES + 1)
        if len(body) > MAX_BODY_BYTES:
            raise RuntimeError(f"error response too large: {path}")
        return error.code, error.geturl(), {k.lower(): v for k, v in error.headers.items()}, body


def expected_bytes(path: str) -> bytes:
    relative = "index.html" if path == "/" else path.lstrip("/")
    return (DIST / relative).read_bytes()


def exact_public_paths() -> tuple[str, ...]:
    return (
        "/",
        "/robots.txt",
        "/sitemap.xml",
        "/site.css",
        "/site.js",
        "/assets/goreecloud-logo.svg",
    )


def verify_exact_response(path: str, errors: list[str]) -> tuple[dict[str, str], bytes] | None:
    try:
        status, final_url, headers, body = fetch(path)
    except (URLError, RuntimeError, ValueError) as error:
        errors.append(f"{path}: network verification failed: {error}")
        return None
    if status != 200:
        errors.append(f"{path}: expected HTTP 200, got {status}")
        return None
    if urlparse(final_url).hostname != EXPECTED_HOST:
        errors.append(f"{path}: final host drifted to {final_url}")
    expected = expected_bytes(path)
    if body != expected:
        errors.append(
            f"{path}: deployed bytes differ from reviewed built artifact; "
            f"expected sha256={sha256(expected).hexdigest()} deployed sha256={sha256(body).hexdigest()}"
        )
    return headers, body


def verify_once() -> list[str]:
    errors: list[str] = []
    root_headers: dict[str, str] = {}
    root_body = b""

    for path in exact_public_paths():
        result = verify_exact_response(path, errors)
        if path == "/" and result is not None:
            root_headers, root_body = result

    if root_body:
        text = root_body.decode("utf-8", errors="replace")
        for marker in (
            "GoreeCloud Labs — Development Center",
            '<link rel="canonical" href="https://labs.goreecloud.com/">',
            'name="goreecloud-glaze-ui" content="1.3.0"',
            'name="robots" content="noindex,nofollow"',
            "Where GoreeCloud gets built next.",
            "Labs is not a release channel.",
            "27",
            "6",
            "45",
            "Integral Platform Systems",
        ):
            if marker not in text:
                errors.append(f"/: missing expected Labs deployment marker: {marker}")
        if root_headers.get("server", "").lower() != "cloudflare":
            errors.append(f"/: expected Cloudflare delivery, got server={root_headers.get('server', '')!r}")
        for header, markers in REQUIRED_HEADER_MARKERS.items():
            value = root_headers.get(header, "")
            if not value:
                errors.append(f"/: missing required response header: {header}")
                continue
            for marker in markers:
                if marker.lower() not in value.lower():
                    errors.append(f"/: {header} missing required value: {marker}")

    try:
        status, final_url, headers, body = fetch("/__goreecloud_labs_missing_verification_path__")
        if status != 404:
            errors.append(f"404 behavior: expected HTTP 404, got {status}")
        if urlparse(final_url).hostname != EXPECTED_HOST:
            errors.append(f"404 behavior: final host drifted to {final_url}")
        expected_404 = (DIST / "404.html").read_bytes()
        if body != expected_404:
            errors.append(
                "404 behavior: deployed 404 body differs from reviewed built 404.html; "
                f"expected sha256={sha256(expected_404).hexdigest()} deployed sha256={sha256(body).hexdigest()}"
            )
        if headers.get("server", "").lower() != "cloudflare":
            errors.append(f"404 behavior: expected Cloudflare delivery, got server={headers.get('server', '')!r}")
    except (URLError, RuntimeError, ValueError) as error:
        errors.append(f"404 behavior: network verification failed: {error}")

    return errors


def verify_with_retry() -> None:
    validate_artifact()
    last_errors: list[str] = []
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        last_errors = verify_once()
        if not last_errors:
            print(
                "Labs production HTTP verification passed for labs.goreecloud.com: exact reviewed root/404/robots/sitemap/CSS/JS/logo bytes, committed security headers, canonical host, and Cloudflare delivery verified. Indexing release and migration-registry production acceptance remain separate gates."
            )
            return
        if attempt < RETRY_ATTEMPTS:
            print(
                f"Labs production does not yet match the exact reviewed artifact "
                f"(attempt {attempt}/{RETRY_ATTEMPTS}); waiting {RETRY_DELAY_SECONDS} seconds."
            )
            time.sleep(RETRY_DELAY_SECONDS)

    print("Labs production verification failed:")
    for error in last_errors:
        print(f"- {error}")
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-config", action="store_true")
    args = parser.parse_args()
    validate_configuration()
    if args.check_config:
        print("Labs production verifier configuration is valid; live verification requires a built artifact.")
        return
    verify_with_retry()


if __name__ == "__main__":
    main()
