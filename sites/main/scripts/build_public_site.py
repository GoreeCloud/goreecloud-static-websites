#!/usr/bin/env python3
"""Build the exact allowlisted static artifact for GoreeCloud's public website.

Repository-only governance, validators, and documentation never enter the public
artifact. GLAZE UI V1.3 is vendored from the exact canonical Stable revision at
build time and remains subject to independent rendered/deployment acceptance.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import sys

from glaze_v1_3 import collect_glaze_css
from normalize_homepage import normalize_homepage
from render_repository_portfolio import load_manifest, render_public_file

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

PUBLIC_ROOT_FILES = (
    "404.html",
    "_headers",
    "googlea0a636fd5dafd9e0.html",
    "index.html",
    "privacy.html",
    "repositories.html",
    "robots.txt",
    "security.html",
    "site.webmanifest",
    "sitemap.xml",
    ".well-known/security.txt",
)

RETIRED_SOURCE_ONLY_ASSET_FILES = (
    "assets/services/actual-budget.png",
    "assets/services/audiobookshelf.svg",
    "assets/services/element.svg",
    "assets/services/immich.svg",
    "assets/services/jellyfin.svg",
    "assets/services/matrix.svg",
    "assets/services/navidrome.png",
    "assets/services/nextcloud.svg",
    "assets/services/onlyoffice.ico",
    "assets/services/paperless-ngx.svg",
    "assets/services/stirling-pdf.png",
    "assets/services/vaultwarden.svg",
    "assets/roadmap/frigate.svg",
    "assets/roadmap/home-assistant.png",
)

PUBLIC_ASSET_FILES = (
    "assets/goreecloud-logo.svg",
    "assets/platform/adguard-home.svg",
    "assets/platform/caddy.svg",
    "assets/platform/debian.svg",
    "assets/platform/docker.png",
    "assets/platform/netbird.svg",
    "assets/platform/proxmox.svg",
    "assets/platform/uptime-kuma.svg",
    "assets/suite/ai.svg",
    "assets/suite/app-store.svg",
    "assets/suite/backup.svg",
    "assets/suite/bookmarks.svg",
    "assets/suite/browser.svg",
    "assets/suite/calendar.svg",
    "assets/suite/changelogs.svg",
    "assets/suite/code.svg",
    "assets/suite/contacts.svg",
    "assets/suite/dns.svg",
    "assets/suite/documents.svg",
    "assets/suite/drive.svg",
    "assets/suite/feed.svg",
    "assets/suite/file-manager.svg",
    "assets/suite/gallery.svg",
    "assets/suite/gateway.svg",
    "assets/suite/identity.svg",
    "assets/suite/index.svg",
    "assets/suite/keyboard.svg",
    "assets/suite/launcher.svg",
    "assets/suite/location.svg",
    "assets/suite/mail.svg",
    "assets/suite/manager.svg",
    "assets/suite/maps.svg",
    "assets/suite/memos.svg",
    "assets/suite/messenger.svg",
    "assets/suite/monitor.svg",
    "assets/suite/music.svg",
    "assets/suite/network.svg",
    "assets/suite/notes.svg",
    "assets/suite/notify.svg",
    "assets/suite/photos.svg",
    "assets/suite/search.svg",
    "assets/suite/sync.svg",
    "assets/suite/tasks.svg",
    "assets/suite/terminal.svg",
    "assets/suite/vault.svg",
    "assets/suite/video.svg",
    "assets/social/github.ico",
    "assets/social/instagram.ico",
    "assets/social/pinterest.ico",
    "assets/social/reddit.ico",
    "assets/social/threads.ico",
    "assets/social/tiktok.ico",
    "assets/social/x.ico",
    "assets/social/youtube.ico",
    "assets/social-preview.png",
)

PUBLIC_STYLE_FILES = (
    "css/development.css",
    "css/error.css",
    "css/glaze-polish.css",
    "css/glaze.css",
    "css/glaze-v1.3.0.css",
    "css/homepage-v6.css",
    "css/homepage-v7.css",
    "css/how-it-works.css",
    "css/platform.css",
    "css/repositories.css",
    "css/roadmap.css",
    "css/social.css",
    "css/status.css",
    "css/style.css",
    "css/websites.css",
)

PUBLIC_SCRIPT_FILES = (
    "js/main.js",
    "js/theme-init.js",
)

PUBLIC_FILES = (
    *PUBLIC_ROOT_FILES,
    *PUBLIC_ASSET_FILES,
    *PUBLIC_STYLE_FILES,
    *PUBLIC_SCRIPT_FILES,
)

GENERATED_HTML = {"index.html", "repositories.html", "privacy.html", "security.html", "404.html"}


def fail(message: str) -> int:
    print(f"Public-site build failed: {message}")
    return 1


def reject_symlink(path: Path) -> None:
    if path.is_symlink():
        raise ValueError(f"Deployable source must not be a symlink: {path.relative_to(ROOT)}")


def main() -> int:
    try:
        if len(PUBLIC_FILES) != len(set(PUBLIC_FILES)):
            return fail("public file allowlist contains a duplicate path")
        retired_overlap = sorted(set(PUBLIC_ASSET_FILES).intersection(RETIRED_SOURCE_ONLY_ASSET_FILES))
        if retired_overlap:
            return fail("retired source-only assets entered the public allowlist: " + ", ".join(retired_overlap))

        for relative in PUBLIC_FILES:
            source = ROOT / relative
            if not source.exists() or not source.is_file():
                return fail(f"required public source is missing: {relative}")
            reject_symlink(source)

        manifest = load_manifest(ROOT)
        glaze_css = collect_glaze_css(ROOT)

        if DIST.exists():
            if DIST.is_symlink():
                return fail("dist must not be a symlink")
            shutil.rmtree(DIST)
        DIST.mkdir()

        for relative in PUBLIC_FILES:
            source = ROOT / relative
            destination = DIST / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative.endswith(".html"):
                rendered = source.read_text(encoding="utf-8")
                if relative in GENERATED_HTML:
                    rendered = render_public_file(relative, rendered, manifest)
                    if relative == "index.html":
                        rendered = normalize_homepage(rendered)
                destination.write_text(rendered, encoding="utf-8")
            else:
                shutil.copy2(source, destination)

        for name, data in sorted(glaze_css.items()):
            target = DIST / "css" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

    except (OSError, ValueError) as exc:
        return fail(str(exc))

    file_count = sum(1 for path in DIST.rglob("*") if path.is_file())
    total_bytes = sum(path.stat().st_size for path in DIST.rglob("*") if path.is_file())
    print(f"Built isolated GLAZE UI V1.3 public artifact: {file_count} files, {total_bytes} bytes -> dist/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
