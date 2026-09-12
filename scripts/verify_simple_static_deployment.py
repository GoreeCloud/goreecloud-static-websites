#!/usr/bin/env python3
"""Verify a governed simple-static deployment against its exact built artifact."""

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

from simple_static_publication import resolve_site

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT_SECONDS = 15
MAX_BODY_BYTES = 4_194_304
NON_FETCHABLE = frozenset({"_headers"})
BRANCH_NAME_RE = re.compile(r"[^a-z0-9-]+")
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


def branch_label() -> str:
    raw = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not raw:
        raise ValueError("branch preview verification requires GITHUB_HEAD_REF or GITHUB_REF_NAME")
    label = BRANCH_NAME_RE.sub("-", raw.lower().replace("/", "-")).strip("-")
    label = re.sub(r"-+", "-", label)[:28].rstrip("-")
    if not label:
        raise ValueError("branch preview label is empty")
    return label


def target_url(spec, target: str) -> str:
    if target == "production":
        return f"https://{spec.canonical_host}"
    return f"https://{branch_label()}.{spec.pages_domain}"


def validate_url(spec, url: str) -> None:
    parsed = urlparse(url)
    allowed = parsed.hostname == spec.canonical_host or bool(
        parsed.hostname and parsed.hostname.endswith(f".{spec.pages_domain}")
    )
    if parsed.scheme != "https" or not allowed:
        raise ValueError(f"{spec.site_id} deployment verifier target is outside approved HTTPS hosts: {url}")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(f"{spec.site_id} deployment verifier target contains unsupported URL components: {url}")


class SafeRedirects(HTTPRedirectHandler):
    def __init__(self, spec):
        super().__init__()
        self.spec = spec

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(self.spec, newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(spec, url: str) -> Response:
    validate_url(spec, url)
    request = Request(
        url,
        headers={
            "User-Agent": "GoreeCloud-Simple-Static-Deployment-Verifier/1.3",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
        method="GET",
    )
    opener = build_opener(SafeRedirects(spec), HTTPSHandler(context=ssl.create_default_context()))
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BODY_BYTES + 1)
            if len(body) > MAX_BODY_BYTES:
                raise RuntimeError(f"response exceeded verifier limit: {url}")
            return Response(response.status, response.geturl(), {k.lower(): v for k, v in response.headers.items()}, body)
    except HTTPError as error:
        body = error.read(MAX_BODY_BYTES + 1)
        return Response(error.code, error.geturl(), {k.lower(): v for k, v in error.headers.items()}, body)
    except URLError as error:
        raise RuntimeError(f"network request failed for {url}: {error.reason}") from error


def candidate_files(spec) -> dict[str, bytes]:
    dist = ROOT / spec.path / "dist"
    if not dist.is_dir():
        raise ValueError(f"{spec.site_id} dist/ is missing; build exact artifact first")
    result: dict[str, bytes] = {}
    for path in sorted(dist.rglob("*")):
        if not path.is_file():
            continue
        if path.is_symlink():
            raise ValueError(f"{spec.site_id} built artifact contains symlink: {path}")
        relative = path.relative_to(dist).as_posix()
        if relative in NON_FETCHABLE:
            continue
        result[relative] = path.read_bytes()
    if "index.html" not in result or "404.html" not in result:
        raise ValueError(f"{spec.site_id} built artifact is incomplete")
    return result


def remote_path(relative: str) -> str:
    if relative == "index.html":
        return "/"
    path = Path(relative)
    if relative.startswith("/") or ".." in path.parts:
        raise ValueError(f"unsafe simple-static artifact path: {relative}")
    return f"/{relative}"


def verify(spec, target: str) -> list[str]:
    base = target_url(spec, target)
    validate_url(spec, base)
    errors: list[str] = []
    try:
        expected = candidate_files(spec)
    except (OSError, ValueError) as error:
        return [str(error)]

    for relative, expected_bytes in sorted(expected.items()):
        url = urljoin(base.rstrip("/") + "/", remote_path(relative).lstrip("/"))
        try:
            response = fetch(spec, url)
        except (RuntimeError, ValueError) as error:
            errors.append(str(error))
            continue
        if response.status != 200:
            errors.append(f"{remote_path(relative)} returned HTTP {response.status}; expected 200")
            continue
        if response.body != expected_bytes:
            errors.append(
                f"candidate mismatch for {remote_path(relative)}: expected {sha256(expected_bytes).hexdigest()}, "
                f"deployed {sha256(response.body).hexdigest()}"
            )

    try:
        root = fetch(spec, base.rstrip("/") + "/")
        if target == "production" and urlparse(root.final_url).hostname != spec.canonical_host:
            errors.append(f"canonical {spec.site_id} root redirected away from production host: {root.final_url}")
        text = root.body.decode("utf-8", errors="replace")
        for marker in (
            'name="goreecloud-glaze-ui" content="1.3.0"',
            'name="goreecloud-glaze-source-revision" content="8354308445da9ac35ced2b37a7f503a08a0aaf72"',
            'name="goreecloud-glaze-consumer-state" content="source-migrated-rendered-acceptance-pending"',
        ):
            if marker not in text:
                errors.append(f"{spec.site_id} root missing V1.3 publication marker: {marker}")
        for header, fragments in REQUIRED_HEADERS.items():
            value = root.headers.get(header, "")
            for fragment in fragments:
                if fragment not in value:
                    errors.append(f"required {spec.site_id} response header missing {header}: {fragment}")
    except RuntimeError as error:
        errors.append(str(error))

    try:
        missing = fetch(spec, base.rstrip("/") + "/__goreecloud_publication_verifier__/missing/path")
        if missing.status != 404:
            errors.append(f"{spec.site_id} missing-path check returned HTTP {missing.status}; expected 404")
    except RuntimeError as error:
        errors.append(str(error))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site")
    parser.add_argument("--target", choices=("branch-preview", "production"), required=True)
    args = parser.parse_args()
    spec = resolve_site(args.site)
    errors = verify(spec, args.target)
    base = target_url(spec, args.target)
    if errors:
        print(f"{spec.site_id} remote deployment verification failed for {args.target}: {base}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"{spec.site_id} exact V1.3 remote deployment verification passed for {args.target}: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
