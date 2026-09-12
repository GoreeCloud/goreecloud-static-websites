#!/usr/bin/env python3
"""Governed publication metadata for GoreeCloud's simple static sites.

This registry is intentionally narrow. It records only the canonical public host,
verified Cloudflare Pages namespace when one exists, expected title, and local site
path required by publication verification. It does not assert that Cloudflare
source authority has been cut over to the central repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SiteSpec:
    site_id: str
    path: str
    title: str
    canonical_host: str
    pages_domain: str | None


SITES = {
    "roadmap": SiteSpec(
        site_id="roadmap",
        path="sites/roadmap",
        title="GoreeCloud Roadmap",
        canonical_host="roadmap.goreecloud.com",
        pages_domain="goreecloud-roadmap.pages.dev",
    ),
    "blog": SiteSpec(
        site_id="blog",
        path="sites/blog",
        title="GoreeCloud Blog",
        canonical_host="blog.goreecloud.com",
        pages_domain="goreecloud-blog.pages.dev",
    ),
    "archive": SiteSpec(
        site_id="archive",
        path="sites/archive",
        title="GoreeCloud Archive",
        canonical_host="archive.goreecloud.com",
        pages_domain="goreecloud-archive.pages.dev",
    ),
    "firefox": SiteSpec(
        site_id="firefox",
        path="sites/firefox",
        title="GoreeCloud Firefox Extensions",
        canonical_host="firefox.goreecloud.com",
        pages_domain=None,
    ),
}


def resolve_site(value: str) -> SiteSpec:
    candidate = value.strip().rstrip("/")
    if candidate in SITES:
        return SITES[candidate]
    normalized = Path(candidate).as_posix().lstrip("./")
    for spec in SITES.values():
        if normalized == spec.path:
            return spec
    raise ValueError(f"unsupported governed simple-static site: {value}")
