#!/usr/bin/env python3
"""Verify deployed GoreeCloud Manager public-site bytes against the exact reviewed built artifact."""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PRODUCTION_URL = "https://manage.goreecloud.com/"
EXPECTED_HOST = "manage.goreecloud.com"
EXPECTED_GLAZE_REVISION = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
EXPECTED_GLAZE_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"
MAX_BODY_BYTES = 2_000_000
REQUEST_TIMEOUT_SECONDS = 12
RETRY_ATTEMPTS = 18
RETRY_DELAY_SECONDS = 10

REQUIRED_HEADER_MARKERS = {
    "content-security-policy": ("default-src 'self'", "frame-ancestors 'none'", "connect-src 'none'"),
    "strict-transport-security": ("max-age=31536000",),
    "x-content-type-options": ("nosniff",),
    "x-frame-options": ("DENY",),
    "referrer-policy": ("no-referrer",),
    "cross-origin-opener-policy": ("same-origin",),
}


class SameHostRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname != EXPECTED_HOST:
            raise URLError(f"redirect outside canonical Manager public host rejected: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def validate_configuration() -> None:
    parsed = urlparse(PRODUCTION_URL)
    if parsed.scheme != "https" or parsed.hostname != EXPECTED_HOST:
        raise SystemExit("production verifier must remain fixed to the canonical HTTPS Manager public host")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise SystemExit("production verifier target must not contain credentials, query, or fragment")
    for relative in ("index.html", "robots.txt", "404.html", "_headers", "assets/manager-mark.svg"):
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"missing or unsafe reviewed Manager public-site source: {relative}")


def validate_artifact() -> None:
    required = (
        "index.html",
        "404.html",
        "_headers",
        "robots.txt",
        "assets/site.css",
        "assets/v1.3-site.css",
        "assets/site.js",
        "assets/manager-mark.svg",
        "assets/glaze-v1.3.0.css",
    )
    for relative in required:
        path = DIST / relative
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"missing or unsafe reviewed Manager artifact: {relative}; build the site first")


def fetch(path: str) -> tuple[int, str, dict[str, str], bytes]:
    if not path.startswith("/"):
        raise ValueError("remote path must be origin-rooted")
    url = urljoin(PRODUCTION_URL, path.lstrip("/"))
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != EXPECTED_HOST:
        raise ValueError(f"remote URL escaped canonical Manager public host: {url}")

    request = Request(
        url,
        headers={
            "User-Agent": "GoreeCloud-Manager-Publication-Verifier/1.0",
            "Accept": "*/*",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
        },
        method="GET",
    )
    opener = build_opener(
        SameHostRedirectHandler(),
        HTTPSHandler(context=ssl.create_default_context()),
    )
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


def exact_public_paths() -> list[str]:
    paths = [
        "/",
        "/robots.txt",
        "/assets/site.css",
        "/assets/v1.3-site.css",
        "/assets/site.js",
        "/assets/manager-mark.svg",
    ]
    for file in sorted((DIST / "assets").glob("glaze-*.css")):
        if file.is_file() and not file.is_symlink():
            paths.append(f"/assets/{file.name}")
    return paths


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
            "GoreeCloud Manager — Operational visibility with explicit authority",
            '<link rel="canonical" href="https://manage.goreecloud.com/">',
            'name="goreecloud-glaze-ui" content="1.3.0"',
            f'name="goreecloud-glaze-source-revision" content="{EXPECTED_GLAZE_REVISION}"',
            'name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"',
            'name="robots" content="noindex,nofollow,noarchive"',
            "Conceptual · no live data",
            "Visibility before mutation",
            "Production remains separately unapproved.",
        ):
            if marker not in text:
                errors.append(f"/: missing expected Manager deployment marker: {marker}")
        if "manager.goreecloud.com" in text:
            errors.append("/: private Manager application hostname is exposed in public website bytes")
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
        status, final_url, headers, body = fetch("/__goreecloud_manager_missing_verification_path__")
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

    glaze = DIST / "assets" / "glaze-v1.3.0.css"
    data = glaze.read_bytes()
    blob = __import__("hashlib").sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data,
        usedforsecurity=False,
    ).hexdigest()
    if blob != EXPECTED_GLAZE_BLOB:
        errors.append(f"reviewed built Glaze entrypoint blob drifted before production verification: {blob}")

    return errors


def verify_with_retry() -> None:
    validate_artifact()
    last_errors: list[str] = []
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        last_errors = verify_once()
        if not last_errors:
            print(
                "Manager production HTTP verification passed for manage.goreecloud.com: exact reviewed root/404/robots/site assets/Manager identity/Glaze bytes, committed headers, canonical host, and Cloudflare delivery verified. Private Manager runtime and platform-system production acceptance remain separate."
            )
            return
        if attempt < RETRY_ATTEMPTS:
            print(
                f"Manager production does not yet match the exact reviewed artifact "
                f"(attempt {attempt}/{RETRY_ATTEMPTS}); waiting {RETRY_DELAY_SECONDS} seconds."
            )
            time.sleep(RETRY_DELAY_SECONDS)

    print("Manager production verification failed:")
    for error in last_errors:
        print(f"- {error}")
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-config", action="store_true")
    args = parser.parse_args()
    validate_configuration()
    if args.check_config:
        print("Manager production verifier configuration is valid; live verification requires a built artifact.")
        return
    verify_with_retry()


if __name__ == "__main__":
    main()
