#!/usr/bin/env python3
"""Compatibility helpers for the source-native GoreeCloud Main website.

Public HTML is now authored directly in its deployable V1.3 form. The historical
repository manifest remains available to audit old reviewed inventory records, but
it is not used to manufacture live counts or rewrite public HTML.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_manifest(root: Path = ROOT) -> dict:
    return json.loads((root / "docs" / "repository-portfolio.json").read_text(encoding="utf-8"))


def render_public_file(relative: str, source: str, manifest: dict) -> str:
    del relative, manifest
    return source
