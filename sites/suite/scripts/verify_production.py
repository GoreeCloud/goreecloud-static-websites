#!/usr/bin/env python3
"""Verify the live GoreeCloud Suite publication against the reviewed built artifact.

This verifier is intentionally read-only. It validates only the public static website
publication at suite.goreecloud.com. Passing it does not promote any Suite product,
platform runtime, lifecycle, security, privacy, continuity, or release state.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener
import ssl

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BASE_URL = "https://suite.goreecloud.com/"
HOST = "suite.goreecloud.com"
TIMEOUT_SECONDS = 20
MAX_BODY_BYTES = 2_000_000
EXPECTED_GLAZE_REVISION = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
EXPECTED_GLAZE_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"
EXPECTED_PRODUCT_COUNT = 45
EXPECTED_GROUP_COUNT = 9

REPRESENTATIVE_PRODUCTS = (
    "GoreeCloud Documents",
    "GoreeCloud Drive",
    "GoreeCloud File Manager",
    "GoreeCloud Mail",
    "GoreeCloud Messenger",
    "GoreeCloud Maps",
    "GoreeCloud Terminal",
    "GoreeCloud App Store",
    "GoreeCloud Gateway",
    "GoreeCloud AI",
    "GoreeCloud Index",
    "GoreeCloud Code",
    "GoreeCloud Health",
    "GoreeCloud Reader",
    "GoreeCloud Router OS",
    "GoreeCloud Social",
    "GoreeCloud Home",
    "GoreeCloud Home Security",
)


@dataclass(frozen=True)
class Response:
    status: int
    final_url: str
    headers: Mapping[str, str]
    body: bytes


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError(f"unexpected redirect from {req.full_url} to {newurl} (HTTP {code})")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    require(parsed.scheme == "https", f"Suite production verifier requires HTTPS: {url}")
    require(parsed.hostname == HOST, f"Suite production verifier refuses non-canonical host: {url}")
    require(not parsed.username and not parsed.password and not parsed.fragment, f"unsafe Suite production URL: {url}")


def build_url(path: str) -> str:
    url = urljoin(BASE_URL, path.lstrip("/"))
    validate_url(url)
    return url


def fetch(path: str) -> Response:
    url = build_url(path)
    request = Request(
        url,
        method="GET",
        headers={
            "User-Agent": "GoreeCloud-Suite-Production-Verifier/1.0",
            "Accept": "*/*",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    opener = build_opener(NoRedirects(), HTTPSHandler(context=ssl.create_default_context()))
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BODY_BYTES + 1)
            require(len(body) <= MAX_BODY_BYTES, f"Suite response exceeded size limit: {url}")
            return Response(
                status=response.status,
                final_url=response.geturl(),
                headers={key.lower(): value for key, value in response.headers.items()},
                body=body,
            )
    except HTTPError as error:
        body = error.read(MAX_BODY_BYTES + 1)
        require(len(body) <= MAX_BODY_BYTES, f"Suite error response exceeded size limit: {url}")
        return Response(
            status=error.code,
            final_url=error.geturl(),
            headers={key.lower(): value for key, value in error.headers.items()},
            body=body,
        )
    except URLError as error:
        raise RuntimeError(f"Suite production request failed for {url}: {error.reason}") from error


def require_cloudflare(response: Response, path: str) -> None:
    require(HOST in urlparse(response.final_url).netloc, f"{path} left canonical Suite host: {response.final_url}")
    server = response.headers.get("server", "").lower()
    require("cloudflare" in server, f"{path} is not visibly served through Cloudflare: server={server!r}")


def require_security_headers(response: Response) -> None:
    csp = response.headers.get("content-security-policy", "").lower()
    for marker in (
        "default-src 'self'",
        "script-src 'none'",
        "object-src 'none'",
        "base-uri 'none'",
        "frame-ancestors 'none'",
        "form-action 'none'",
        "upgrade-insecure-requests",
    ):
        require(marker in csp, f"Suite production CSP missing {marker!r}: {csp!r}")

    require(response.headers.get("referrer-policy", "").lower() == "strict-origin-when-cross-origin", "Suite Referrer-Policy mismatch")
    require(response.headers.get("x-content-type-options", "").lower() == "nosniff", "Suite X-Content-Type-Options mismatch")
    require(response.headers.get("x-frame-options", "").upper() == "DENY", "Suite X-Frame-Options mismatch")
    require(response.headers.get("cross-origin-opener-policy", "").lower() == "same-origin", "Suite COOP mismatch")
    require(response.headers.get("cross-origin-resource-policy", "").lower() == "same-site", "Suite CORP mismatch")
    permissions = response.headers.get("permissions-policy", "").lower()
    for marker in ("camera=()", "microphone=()", "geolocation=()", "payment=()", "usb=()"):
        require(marker in permissions, f"Suite Permissions-Policy missing {marker!r}: {permissions!r}")


def git_blob_sha(data: bytes) -> str:
    prefix = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return sha1(prefix + data, usedforsecurity=False).hexdigest()


def require_exact_body(response: Response, relative: str) -> None:
    source = DIST / relative
    require(source.is_file() and not source.is_symlink(), f"reviewed Suite artifact missing: {relative}")
    expected = source.read_bytes()
    require(
        response.body == expected,
        f"live Suite {relative} differs from reviewed built artifact ({len(response.body)} live bytes vs {len(expected)} expected bytes)",
    )


def verify_root() -> None:
    response = fetch("/")
    require(response.status == 200, f"Suite root returned HTTP {response.status}; expected 200")
    require_cloudflare(response, "/")
    require_security_headers(response)
    cache = response.headers.get("cache-control", "").lower()
    require("max-age=0" in cache and "must-revalidate" in cache, f"Suite root cache policy mismatch: {cache!r}")
    require_exact_body(response, "index.html")

    text = response.body.decode("utf-8")
    for marker in (
        'data-glaze-version="1.3.0"',
        'name="goreecloud-glaze-ui" content="1.3.0"',
        f'name="goreecloud-glaze-source-revision" content="{EXPECTED_GLAZE_REVISION}"',
        "45</strong><span>verified Suite products",
        "9</strong><span>functional product groups",
    ):
        require(marker in text, f"Suite root missing current publication marker: {marker}")

    product_count = text.count('class="app-card"')
    group_count = text.count('class="product-group"')
    require(product_count == EXPECTED_PRODUCT_COUNT, f"Suite live product-card count is {product_count}; expected {EXPECTED_PRODUCT_COUNT}")
    require(group_count == EXPECTED_GROUP_COUNT, f"Suite live product-group count is {group_count}; expected {EXPECTED_GROUP_COUNT}")
    for product in REPRESENTATIVE_PRODUCTS:
        require(product in text, f"Suite live directory is missing reconciled product: {product}")


def verify_not_found() -> None:
    response = fetch("/__goreecloud-deployment-smoke__/missing/path")
    require(response.status == 404, f"Suite missing-path probe returned HTTP {response.status}; expected 404")
    require_cloudflare(response, "missing path")
    require_security_headers(response)
    cache = response.headers.get("cache-control", "").lower()
    require("no-store" in cache, f"Suite 404 must be no-store; got {cache!r}")
    require_exact_body(response, "404.html")


def verify_sitemap_and_robots() -> None:
    sitemap = fetch("/sitemap.xml")
    require(sitemap.status == 200, f"Suite sitemap returned HTTP {sitemap.status}; expected 200")
    require_cloudflare(sitemap, "/sitemap.xml")
    require_exact_body(sitemap, "sitemap.xml")
    require(b"https://suite.goreecloud.com/" in sitemap.body, "Suite sitemap lacks canonical production URL")

    robots = fetch("/robots.txt")
    require(robots.status == 200, f"Suite robots.txt returned HTTP {robots.status}; expected 200")
    require_cloudflare(robots, "/robots.txt")
    require_exact_body(robots, "robots.txt")
    require(b"https://suite.goreecloud.com/sitemap.xml" in robots.body, "Suite robots.txt lacks canonical sitemap URL")


def verify_glaze_entrypoint() -> None:
    response = fetch("/assets/glaze-v1.3.0.css")
    require(response.status == 200, f"Suite Glaze entrypoint returned HTTP {response.status}; expected 200")
    require_cloudflare(response, "/assets/glaze-v1.3.0.css")
    cache = response.headers.get("cache-control", "").lower()
    require("max-age=604800" in cache and "immutable" in cache, f"Suite Glaze cache policy mismatch: {cache!r}")
    require_exact_body(response, "assets/glaze-v1.3.0.css")
    actual_blob = git_blob_sha(response.body)
    require(actual_blob == EXPECTED_GLAZE_BLOB, f"Suite Glaze V1.3 blob mismatch: {actual_blob}")


def main() -> int:
    require(DIST.is_dir(), "Suite dist/ artifact is missing; build the reviewed artifact before production verification")
    verify_root()
    verify_not_found()
    verify_sitemap_and_robots()
    verify_glaze_entrypoint()
    print(
        "Suite production HTTP verification passed for suite.goreecloud.com: exact reviewed root/404/sitemap/robots/Glaze bytes, "
        "45 products, 9 groups, committed headers, canonical host, and Cloudflare delivery verified. "
        "Human rendered/accessibility acceptance and exact deployment-revision binding remain separate evidence gates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
