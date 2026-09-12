#!/usr/bin/env python3
"""Verify an approved GoreeCloud Design Center deployment against exact dist bytes.

The verifier is intentionally fail-closed. It only accepts the canonical Design
Center hostname and the verified `goreecloud-design.pages.dev` namespace. Provider
success alone is not production acceptance: every fetchable built artifact must
match the reviewed central build byte-for-byte and required response headers must
be present.
"""

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
DIST = SITE / "dist"
PRODUCTION_URL = "https://design.goreecloud.com"
PAGES_DOMAIN = "goreecloud-design.pages.dev"
BRANCH_NAME_RE = re.compile(r"[^a-z0-9-]+")
TIMEOUT_SECONDS = 15
MAX_BODY_BYTES = 2_097_152
NON_FETCHABLE = frozenset({"_headers"})

REQUIRED_HEADERS = {
    "content-security-policy": (
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self'",
        "connect-src 'none'",
        "frame-ancestors 'none'",
        "object-src 'none'",
    ),
    "permissions-policy": ("camera=()", "geolocation=()", "microphone=()"),
    "referrer-policy": ("strict-origin-when-cross-origin",),
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


def normalize_branch_preview_label(branch: str) -> str:
    label = BRANCH_NAME_RE.sub("-", branch.strip().lower().replace("/", "-")).strip("-")
    label = re.sub(r"-+", "-", label)[:28].rstrip("-")
    if not label:
        raise ValueError("Design Center branch preview name resolves to an empty label")
    return label


def branch_preview_url() -> str:
    branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not branch:
        raise ValueError("Branch preview verification requires GITHUB_HEAD_REF or GITHUB_REF_NAME")
    return f"https://{normalize_branch_preview_label(branch)}.{PAGES_DOMAIN}"


def target_url(target: str) -> str:
    return PRODUCTION_URL if target == "production" else branch_preview_url()


def host_allowed(hostname: str | None) -> bool:
    return bool(
        hostname
        and (hostname == "design.goreecloud.com" or hostname.endswith(f".{PAGES_DOMAIN}"))
    )


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not host_allowed(parsed.hostname):
        raise ValueError(f"Design Center verifier target is outside approved HTTPS hosts: {url}")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(f"Design Center verifier target contains unsupported URL components: {url}")


class SafeRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url: str) -> Response:
    validate_url(url)
    request = Request(
        url,
        headers={
            "User-Agent": "GoreeCloud-Design-Deployment-Verifier/1.3",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
        method="GET",
    )
    opener = build_opener(SafeRedirects(), HTTPSHandler(context=ssl.create_default_context()))
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BODY_BYTES + 1)
            if len(body) > MAX_BODY_BYTES:
                raise RuntimeError(f"response exceeded verifier limit: {url}")
            return Response(
                response.status,
                response.geturl(),
                {key.lower(): value for key, value in response.headers.items()},
                body,
            )
    except HTTPError as error:
        body = error.read(MAX_BODY_BYTES + 1)
        return Response(
            error.code,
            error.geturl(),
            {key.lower(): value for key, value in error.headers.items()},
            body,
        )
    except URLError as error:
        raise RuntimeError(f"network request failed for {url}: {error.reason}") from error


def candidate_files() -> dict[str, bytes]:
    if not DIST.is_dir():
        raise ValueError("Design Center dist/ is missing; run validate.py/build.py first")
    files: dict[str, bytes] = {}
    for path in sorted(DIST.rglob("*")):
        if not path.is_file():
            continue
        if path.is_symlink():
            raise ValueError(f"Design Center built artifact must not contain symlink: {path}")
        relative = path.relative_to(DIST).as_posix()
        if relative in NON_FETCHABLE:
            continue
        files[relative] = path.read_bytes()
    if "index.html" not in files or "404.html" not in files:
        raise ValueError("Design Center built artifact is incomplete")
    return files


def remote_path(relative: str) -> str:
    if relative == "index.html":
        return "/"
    path = Path(relative)
    if relative.startswith("/") or ".." in path.parts:
        raise ValueError(f"unsafe Design Center artifact path: {relative}")
    return f"/{relative}"


def verify_exact_files(base: str, errors: list[str]) -> None:
    try:
        expected = candidate_files()
    except (OSError, ValueError) as error:
        errors.append(str(error))
        return
    for relative, expected_bytes in sorted(expected.items()):
        url = urljoin(base.rstrip("/") + "/", remote_path(relative).lstrip("/"))
        try:
            response = fetch(url)
        except (RuntimeError, ValueError) as error:
            errors.append(str(error))
            continue
        if response.status != 200:
            errors.append(f"{remote_path(relative)} returned HTTP {response.status}; expected 200")
            continue
        if response.body != expected_bytes:
            errors.append(
                f"candidate mismatch for {remote_path(relative)}: expected "
                f"{sha256(expected_bytes).hexdigest()}, deployed {sha256(response.body).hexdigest()}"
            )


def verify_root(base: str, target: str, errors: list[str]) -> None:
    try:
        response = fetch(base.rstrip("/") + "/")
    except RuntimeError as error:
        errors.append(str(error))
        return
    if response.status != 200:
        errors.append(f"Design Center root returned HTTP {response.status}; expected 200")
        return
    if target == "production" and urlparse(response.final_url).hostname != "design.goreecloud.com":
        errors.append(f"canonical Design Center root redirected away from production host: {response.final_url}")
    text = response.body.decode("utf-8", errors="replace")
    for marker in (
        "<title>GoreeCloud Design Center — GLAZE UI V1.3</title>",
        'name="goreecloud-glaze-ui" content="1.3.0"',
        'name="goreecloud-glaze-source-revision" content="8354308445da9ac35ced2b37a7f503a08a0aaf72"',
        'name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"',
        "Current Official Stable · 1.3.0",
        "Design Center rendered acceptance pending",
    ):
        if marker not in text:
            errors.append(f"Design Center root is missing production marker: {marker}")
    for forbidden in (
        "Current Stable · GLAZE UI V1.1",
        "GLAZE UI V1.1 is GoreeCloud's current Stable",
        "glaze-ui-2.1.0.css",
        'data-glaze-ui="2.1.0"',
        'content="accepted"',
    ):
        if forbidden in text:
            errors.append(f"Design Center root exposes stale or unsupported marker: {forbidden}")
    for header, fragments in REQUIRED_HEADERS.items():
        value = response.headers.get(header, "")
        for fragment in fragments:
            if fragment not in value:
                errors.append(f"required Design Center response header missing {header}: {fragment}")


def verify_not_found(base: str, errors: list[str]) -> None:
    try:
        response = fetch(base.rstrip("/") + "/__goreecloud_design_deployment_verifier__/missing")
    except RuntimeError as error:
        errors.append(str(error))
        return
    if response.status != 404:
        errors.append(f"Design Center missing-path check returned HTTP {response.status}; expected 404")


def verify(target: str) -> int:
    base = target_url(target)
    validate_url(base)
    errors: list[str] = []
    verify_exact_files(base, errors)
    verify_root(base, target, errors)
    verify_not_found(base, errors)
    if errors:
        print(f"Design Center remote deployment verification failed for {target}: {base}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Design Center exact V1.3 remote deployment verification passed for {target}: {base}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("branch-preview", "production"), required=True)
    args = parser.parse_args()
    return verify(args.target)


if __name__ == "__main__":
    raise SystemExit(main())
