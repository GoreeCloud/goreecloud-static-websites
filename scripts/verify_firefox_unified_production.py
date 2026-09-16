#!/usr/bin/env python3
"""Verify the unified Firefox Extensions production publication and compatibility redirect."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import ssl
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
MOUNTED = ROOT / "dist" / "firefox-extensions"
CANONICAL = "https://www.goreecloud.com/firefox-extensions/"
LEGACY = "https://firefox.goreecloud.com/"
GLAZE_VERSION = "1.4.1"
GLAZE_REVISION = "4fab9da0fad2e5c974e0e66ec88632c61745751c"
TIMEOUT = 20
MAX_BODY = 4_194_304
REQUIRED_HEADERS = {
    "content-security-policy": ("default-src 'self'", "frame-ancestors 'none'", "object-src 'none'"),
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


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _allowed(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in {"www.goreecloud.com", "firefox.goreecloud.com"}


def fetch(url: str, *, follow: bool = True) -> Response:
    if not _allowed(url):
        raise ValueError(f"verification URL is outside the approved GoreeCloud hosts: {url}")
    request = Request(
        url,
        method="GET",
        headers={
            "User-Agent": "GoreeCloud-Firefox-Unified-Production-Verifier/1.0",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    handlers = [HTTPSHandler(context=ssl.create_default_context())]
    if not follow:
        handlers.insert(0, NoRedirect())
    opener = build_opener(*handlers)
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            body = response.read(MAX_BODY + 1)
            if len(body) > MAX_BODY:
                raise RuntimeError(f"response exceeded verifier limit: {url}")
            return Response(response.status, response.geturl(), {k.lower(): v for k, v in response.headers.items()}, body)
    except HTTPError as error:
        body = error.read(MAX_BODY + 1)
        return Response(error.code, error.geturl(), {k.lower(): v for k, v in error.headers.items()}, body)
    except URLError as error:
        raise RuntimeError(f"network request failed for {url}: {error.reason}") from error


def expected_files() -> dict[str, bytes]:
    if not MOUNTED.is_dir() or not (MOUNTED / "index.html").is_file():
        raise RuntimeError("unified Firefox artifact is missing; run scripts/build_www_namespace.py first")
    result: dict[str, bytes] = {}
    for path in sorted(MOUNTED.rglob("*")):
        if not path.is_file():
            continue
        if path.is_symlink():
            raise RuntimeError(f"symlink is not allowed in unified Firefox artifact: {path}")
        relative = path.relative_to(MOUNTED).as_posix()
        if relative == "_headers":
            continue
        result[relative] = path.read_bytes()
    return result


def production_url(relative: str) -> str:
    return CANONICAL if relative == "index.html" else urljoin(CANONICAL, relative)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def verify_exact_bytes(errors: list[str]) -> None:
    for relative, expected in expected_files().items():
        url = production_url(relative)
        response = fetch(url)
        if response.status != 200:
            errors.append(f"{relative} returned HTTP {response.status}; expected 200")
            continue
        if response.body != expected:
            errors.append(
                f"deployed byte mismatch for {relative}: expected {sha256(expected).hexdigest()}, "
                f"deployed {sha256(response.body).hexdigest()}"
            )
        content_type = response.headers.get("content-type", "")
        disposition = response.headers.get("content-disposition", "")
        if relative.endswith(".svg"):
            require(
                content_type.lower().startswith("image/svg+xml"),
                f"SVG media type is not render-safe for {relative}: content-type={content_type!r}, content-disposition={disposition!r}",
                errors,
            )
        if relative.endswith(".css"):
            require(
                content_type.lower().startswith("text/css"),
                f"CSS media type drift for {relative}: content-type={content_type!r}",
                errors,
            )


def verify_root(errors: list[str]) -> None:
    response = fetch(CANONICAL)
    require(response.status == 200, f"canonical Firefox root returned HTTP {response.status}; expected 200", errors)
    require(response.final_url == CANONICAL, f"canonical Firefox root redirected unexpectedly: {response.final_url}", errors)
    text = response.body.decode("utf-8", errors="replace")
    require('<link rel="canonical" href="https://www.goreecloud.com/firefox-extensions/">' in text, "canonical Firefox root does not publish the governed canonical URL", errors)
    require(f'name="goreecloud-glaze-ui" content="{GLAZE_VERSION}"' in text, f"canonical Firefox root does not publish Glaze UI {GLAZE_VERSION}", errors)
    require(f'name="goreecloud-glaze-source-revision" content="{GLAZE_REVISION}"' in text, "canonical Firefox root does not publish the accepted Glaze source revision", errors)
    require("GoreeCloud Firefox Extensions" in text, "canonical Firefox identity is missing", errors)
    require("goreecloud-extension-inventory-schema" in text and 'content="2"' in text, "Firefox schema-v2 inventory marker is missing", errors)
    for header, fragments in REQUIRED_HEADERS.items():
        value = response.headers.get(header, "")
        for fragment in fragments:
            require(fragment in value, f"required response header missing {header}: {fragment}", errors)


def verify_missing_path(errors: list[str]) -> None:
    response = fetch(CANONICAL + "__goreecloud_firefox_verifier__/missing/path")
    require(response.status == 404, f"canonical Firefox missing path returned HTTP {response.status}; expected 404", errors)


def verify_redirect(errors: list[str]) -> None:
    root = fetch(LEGACY, follow=False)
    require(root.status == 301, f"legacy Firefox root returned HTTP {root.status}; expected 301", errors)
    require(root.headers.get("location") == CANONICAL, f"legacy Firefox root redirect target drifted: {root.headers.get('location')}", errors)
    suffix_source = LEGACY + "__goreecloud_firefox_verifier__/missing?migration=1"
    suffix_target = CANONICAL + "__goreecloud_firefox_verifier__/missing?migration=1"
    suffix = fetch(suffix_source, follow=False)
    require(suffix.status == 301, f"legacy Firefox suffix redirect returned HTTP {suffix.status}; expected 301", errors)
    require(suffix.headers.get("location") == suffix_target, f"legacy Firefox suffix/query preservation drifted: {suffix.headers.get('location')}", errors)


def main() -> int:
    errors: list[str] = []
    try:
        verify_exact_bytes(errors); verify_root(errors); verify_missing_path(errors); verify_redirect(errors)
    except (RuntimeError, ValueError) as error:
        errors.append(str(error))
    if errors:
        print("Unified Firefox production verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Unified Firefox production verification passed: exact deployed bytes, render-safe asset media types, canonical URL, Glaze UI 1.4.1, security headers, explicit 404, and 301 legacy redirect with suffix/query preservation are verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
