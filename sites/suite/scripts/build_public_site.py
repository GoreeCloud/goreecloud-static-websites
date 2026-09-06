#!/usr/bin/env python3
"""Build the explicit public artifact for suite.goreecloud.com."""

from __future__ import annotations

from pathlib import Path
import shutil
import sys

from glaze_ui_2 import apply_glaze_ui_2

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

SUITE_ICON_FILES = (
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
)

PUBLIC_FILES = (
    "index.html",
    "styles.css",
    "glaze-ui-2.1.0.css",
    "_headers",
    "robots.txt",
    "sitemap.xml",
    "site.webmanifest",
    "assets/goreecloud-logo.svg",
    *SUITE_ICON_FILES,
)


def main() -> int:
    try:
        if len(PUBLIC_FILES) != len(set(PUBLIC_FILES)):
            raise ValueError("public allowlist contains duplicate paths")
        if DIST.exists():
            if DIST.is_symlink():
                raise ValueError("dist must not be a symlink")
            shutil.rmtree(DIST)
        DIST.mkdir()
        for relative in PUBLIC_FILES:
            source = ROOT / relative
            if not source.is_file() or source.is_symlink():
                raise ValueError(f"invalid public source: {relative}")
            target = DIST / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if relative == "index.html":
                target.write_text(apply_glaze_ui_2(source.read_text(encoding="utf-8")), encoding="utf-8")
            else:
                shutil.copy2(source, target)
    except (OSError, ValueError) as exc:
        print(f"Suite website build failed: {exc}")
        return 1

    files = [path for path in DIST.rglob("*") if path.is_file()]
    print(f"Built Suite website artifact: {len(files)} files, {sum(path.stat().st_size for path in files)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
