#!/usr/bin/env python3
"""Verify the live GoreeCloud Continuity Center against the reviewed artifact.

This verifier is read-only. It validates only the public static publication at
`everkeep.goreecloud.com`; it does not establish Everkeep recovery-effect authority,
application continuity acceptance, failover authority, or a global Recovery Ready state.
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
BASE_URL = "https://everkeep.goreecloud.com/"
HOST = "everkeep.goreecloud.com"
TIMEOUT_SECONDS = 20
MAX_BODY_BYTES = 2_000_000
EXPECTED_GLAZE_REVISION = "8354308445da9ac35ced2b37a7f503a08a0aaf72"
EXPECTED_GLAZE_BLOB = "4c3ad293ba9196e2e5a32700b530ec67fd01cef6"


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
    require(parsed.scheme == "https", f"Continuity Center production verifier requires HTTPS: {url}")
    require(parsed.hostname == HOST, f"Continuity Center verifier refuses non-canonical host: {url}")
    require(not parsed.username and not parsed.password and not parsed.fragment, f"unsafe Continuity Center URL: {url}")


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
            "User-Agent": "GoreeCloud-Everkeep-Production-Verifier/1.0",
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
            require(len(body) <= MAX_BODY_BYTES, f"Continuity Center response exceeded size limit: {url}")
            return Response(response.status, response.geturl(), {key.lower(): value for key, value in response.headers.items()}, body)
    except HTTPError as error:
        body = error.read(MAX_BODY_BYTES + 1)
        require(len(body) <= MAX_BODY_BYTES, f"Continuity Center error response exceeded size limit: {url}")
        return Response(error.code, error.geturl(), {key.lower(): value for key, value in error.headers.items()}, body)
    except URLError as error:
        raise RuntimeError(f"Continuity Center production request failed for {url}: {error.reason}") from error


def require_cloudflare(response: Response, label: str) -> None:
    require(urlparse(response.final_url).hostname == HOST, f"{label} left canonical Everkeep host: {response.final_url}")
    server = response.headers.get("server", "").lower()
    require("cloudflare" in server, f"{label} is not visibly served through Cloudflare: server={server!r}")


def require_security_headers(response: Response) -> None:
    csp = response.headers.get("content-security-policy", "").lower()
    for marker in (
        "default-src 'self'",
        "base-uri 'self'",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "form-action 'none'",
        "script-src 'none'",
        "style-src 'self'",
        "img-src 'self'",
        "connect-src 'none'",
        "upgrade-insecure-requests",
    ):
        require(marker in csp, f"Continuity Center CSP missing {marker!r}: {csp!r}")
    require(response.headers.get("referrer-policy", "").lower() == "no-referrer", "Continuity Center Referrer-Policy mismatch")
    require(response.headers.get("x-content-type-options", "").lower() == "nosniff", "Continuity Center X-Content-Type-Options mismatch")
    require(response.headers.get("x-frame-options", "").upper() == "DENY", "Continuity Center X-Frame-Options mismatch")
    require(response.headers.get("cross-origin-opener-policy", "").lower() == "same-origin", "Continuity Center COOP mismatch")
    permissions = response.headers.get("permissions-policy", "").lower()
    for marker in ("camera=()", "microphone=()", "geolocation=()", "payment=()", "usb=()"):
        require(marker in permissions, f"Continuity Center Permissions-Policy missing {marker!r}: {permissions!r}")
    hsts = response.headers.get("strict-transport-security", "").lower()
    require("max-age=31536000" in hsts, f"Continuity Center HSTS mismatch: {hsts!r}")


def git_blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data, usedforsecurity=False).hexdigest()


def require_exact_body(response: Response, relative: str) -> None:
    source = DIST / relative
    require(source.is_file() and not source.is_symlink(), f"reviewed Continuity Center artifact missing: {relative}")
    expected = source.read_bytes()
    require(response.body == expected, f"live Continuity Center {relative} differs from reviewed artifact ({len(response.body)} live bytes vs {len(expected)} expected bytes)")


def verify_root() -> None:
    response = fetch("/")
    require(response.status == 200, f"Continuity Center root returned HTTP {response.status}; expected 200")
    require_cloudflare(response, "/")
    require_security_headers(response)
    cache = response.headers.get("cache-control", "").lower()
    require("no-cache" in cache or "max-age=0" in cache, f"Continuity Center root cache policy mismatch: {cache!r}")
    require_exact_body(response, "index.html")
    text = response.body.decode("utf-8")
    for marker in (
        'data-glaze-version="1.3.0"',
        'name="goreecloud-glaze-ui" content="1.3.0"',
        f'name="goreecloud-glaze-source-revision" content="{EXPECTED_GLAZE_REVISION}"',
        'name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"',
        'rel="canonical" href="https://everkeep.goreecloud.com/"',
        "A backup existing is never presented as equivalent",
        "No global Everkeep Recovery Ready state is implied.",
        "GoreeCloud Care 0.1.0",
        "representative Zorin OS 17.3",
    ):
        require(marker in text, f"Continuity Center root missing publication marker: {marker}")


def verify_not_found() -> None:
    response = fetch("/__goreecloud-deployment-smoke__/missing/path")
    require(response.status == 404, f"Continuity Center missing-path probe returned HTTP {response.status}; expected 404")
    require_cloudflare(response, "missing path")
    require_security_headers(response)
    cache = response.headers.get("cache-control", "").lower()
    require("no-store" in cache or "no-cache" in cache, f"Continuity Center 404 must not be cacheable; got {cache!r}")
    require_exact_body(response, "404.html")


def verify_publication_files() -> None:
    for remote, relative in (
        ("/sitemap.xml", "sitemap.xml"),
        ("/robots.txt", "robots.txt"),
        ("/assets/style.css", "assets/style.css"),
        ("/assets/site-polish.css", "assets/site-polish.css"),
        ("/assets/v1.3-site.css", "assets/v1.3-site.css"),
        ("/assets/everkeep.svg", "assets/everkeep.svg"),
    ):
        response = fetch(remote)
        require(response.status == 200, f"Continuity Center {remote} returned HTTP {response.status}; expected 200")
        require_cloudflare(response, remote)
        require_exact_body(response, relative)
    sitemap = fetch("/sitemap.xml")
    robots = fetch("/robots.txt")
    require(b"https://everkeep.goreecloud.com/" in sitemap.body, "Continuity Center sitemap lacks canonical URL")
    require(b"https://everkeep.goreecloud.com/sitemap.xml" in robots.body, "Continuity Center robots.txt lacks canonical sitemap URL")


def verify_glaze_entrypoint() -> None:
    response = fetch("/assets/glaze-v1.3.0.css")
    require(response.status == 200, f"Continuity Center Glaze entrypoint returned HTTP {response.status}; expected 200")
    require_cloudflare(response, "/assets/glaze-v1.3.0.css")
    require_exact_body(response, "assets/glaze-v1.3.0.css")
    actual_blob = git_blob_sha(response.body)
    require(actual_blob == EXPECTED_GLAZE_BLOB, f"Continuity Center Glaze V1.3 blob mismatch: {actual_blob}")


def main() -> int:
    require(DIST.is_dir(), "Continuity Center dist/ artifact is missing; build before production verification")
    verify_root()
    verify_not_found()
    verify_publication_files()
    verify_glaze_entrypoint()
    print(
        "Continuity Center production HTTP verification passed for everkeep.goreecloud.com: exact reviewed root/404/sitemap/robots/site CSS/Everkeep identity/Glaze bytes, committed headers, canonical host, and Cloudflare delivery verified. "
        "Recovery-effect, product-runtime, and global Recovery Ready acceptance remain separate."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
