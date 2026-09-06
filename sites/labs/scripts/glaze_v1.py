#!/usr/bin/env python3
"""Fetch the exact current Stable GLAZE UI V1.1 web bundle for same-origin publication.

The immutable 1.1.0 Stable source has one known CSS import-closure defect:
glaze-v1.components.css imports a nonexistent glaze-v1.candidate.css. Until a
corrected immutable Stable release is published, Website builds fail closed on
that exact defect and remove only that single dangling import from the generated
artifact. Any other upstream drift remains a hard failure.
"""
from __future__ import annotations

from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import re

GLAZE_VERSION = "1.1.0"
GLAZE_SOURCE_REVISION = "15cc76d2bcd4065552dc31c77145b63f34d9e7b2"
BASE_URL = f"https://raw.githubusercontent.com/GoreeCloud/goreecloud-glaze-ui/{GLAZE_SOURCE_REVISION}/css"
FILES = (
    "glaze-v1.1.0.css",
    "glaze-v1.0.0.css",
    "glaze-v1.foundation.css",
    "glaze-v1.components.css",
    "glaze-v1.components.adaptive.css",
    "glaze-v1.components.runtime.css",
    "glaze-v1.structure.css",
    "glaze-v1.overlay.css",
    "glaze-v1.advanced.css",
    "glaze-v1.visual-refinement.css",
    "glaze-v1.optical-reachability.css",
    "glaze-v1.1.css",
    "glaze-v1.1-appearance.css",
)

KNOWN_STABLE_DEFECT_OWNER = "glaze-v1.components.css"
KNOWN_STABLE_DEFECT_IMPORT = "glaze-v1.candidate.css"
KNOWN_STABLE_DEFECT_DIRECTIVE = '@import url("./glaze-v1.candidate.css");'
KNOWN_STABLE_WORKAROUND_MARKER = (
    "GoreeCloud Website build workaround: removed the single known dangling "
    "GLAZE UI 1.1.0 Stable import; consumer conformance remains pending."
)


def _imports(text: str) -> set[str]:
    return set(re.findall(r'@import\s+url\(["\']\./([^"\']+)["\']\)', text))


def _request(name: str) -> Request:
    return Request(
        f"{BASE_URL}/{name}",
        headers={"User-Agent": "GoreeCloud-Website-Build/1.1"},
    )


def confirm_known_stable_defect_missing(timeout: float = 20.0) -> None:
    try:
        with urlopen(_request(KNOWN_STABLE_DEFECT_IMPORT), timeout=timeout) as response:
            raise ValueError(
                "Refusing GLAZE workaround because the known Stable dependency now exists "
                f"(HTTP {response.status}): {KNOWN_STABLE_DEFECT_IMPORT}"
            )
    except HTTPError as exc:
        if exc.code != 404:
            raise ValueError(
                "Unable to prove the known GLAZE Stable dependency is absent: "
                f"HTTP {exc.code} for {KNOWN_STABLE_DEFECT_IMPORT}"
            ) from exc
    except (URLError, TimeoutError) as exc:
        raise ValueError(
            "Unable to prove the known GLAZE Stable dependency is absent: "
            f"{KNOWN_STABLE_DEFECT_IMPORT}: {exc}"
        ) from exc


def _validate_common(bundle: dict[str, str]) -> None:
    missing = sorted(set(FILES) - set(bundle))
    if missing:
        raise ValueError("GLAZE V1.1 bundle is incomplete: " + ", ".join(missing))
    entry = bundle["glaze-v1.1.0.css"]
    if "official Stable web entrypoint" not in entry:
        raise ValueError("GLAZE V1.1 Stable entrypoint marker is missing")
    expected_entry = {"glaze-v1.0.0.css", "glaze-v1.1.css", "glaze-v1.1-appearance.css"}
    if _imports(entry) != expected_entry:
        raise ValueError("GLAZE V1.1 Stable entrypoint import closure changed unexpectedly")
    v10 = bundle["glaze-v1.0.0.css"]
    expected_v10 = {
        "glaze-v1.foundation.css", "glaze-v1.components.css", "glaze-v1.components.adaptive.css",
        "glaze-v1.components.runtime.css", "glaze-v1.structure.css", "glaze-v1.overlay.css",
        "glaze-v1.advanced.css", "glaze-v1.visual-refinement.css", "glaze-v1.optical-reachability.css",
    }
    if _imports(v10) != expected_v10:
        raise ValueError("GLAZE V1.0 inherited import closure changed unexpectedly")
    v11 = bundle["glaze-v1.1.css"]
    if "GLAZE UI V1.1" not in v11 or 'html[data-glaze-version="1.1"]' not in v11:
        raise ValueError("GLAZE V1.1 optical layer markers are missing")
    appearance = bundle["glaze-v1.1-appearance.css"]
    for marker in ('data-glz-appearance="light"', 'data-glz-appearance="dark"', 'forced-colors: active'):
        if marker not in appearance:
            raise ValueError(f"GLAZE V1.1 appearance marker is missing: {marker}")
    for name, text in bundle.items():
        if not text.strip():
            raise ValueError(f"Downloaded GLAZE source is empty: {name}")
        if "raw.githubusercontent.com" in text or "https://" in text or "http://" in text:
            raise ValueError(f"GLAZE runtime CSS must not introduce remote resources: {name}")


def validate_upstream_bundle(bundle: dict[str, str]) -> None:
    _validate_common(bundle)
    for name, text in bundle.items():
        unexpected = _imports(text) - set(FILES)
        if name == KNOWN_STABLE_DEFECT_OWNER:
            if unexpected != {KNOWN_STABLE_DEFECT_IMPORT}:
                raise ValueError(f"Known GLAZE V1.1 Stable import defect changed unexpectedly in {name}: {sorted(unexpected)}")
            if text.count(KNOWN_STABLE_DEFECT_DIRECTIVE) != 1:
                raise ValueError("Known GLAZE V1.1 Stable dangling import must occur exactly once")
        elif unexpected:
            raise ValueError(f"GLAZE CSS imports an unpinned file from {name}: {sorted(unexpected)}")


def apply_known_stable_workaround(bundle: dict[str, str]) -> dict[str, str]:
    normalized = dict(bundle)
    source = normalized[KNOWN_STABLE_DEFECT_OWNER]
    if source.count(KNOWN_STABLE_DEFECT_DIRECTIVE) != 1:
        raise ValueError("Refusing GLAZE workaround because the known defect no longer matches")
    normalized[KNOWN_STABLE_DEFECT_OWNER] = source.replace(
        KNOWN_STABLE_DEFECT_DIRECTIVE,
        f"/* {KNOWN_STABLE_WORKAROUND_MARKER} */",
        1,
    )
    return normalized


def validate_bundle(bundle: dict[str, str]) -> None:
    _validate_common(bundle)
    owner = bundle[KNOWN_STABLE_DEFECT_OWNER]
    if KNOWN_STABLE_DEFECT_DIRECTIVE in owner:
        raise ValueError("Generated GLAZE artifact still contains the known dangling Stable import")
    if KNOWN_STABLE_WORKAROUND_MARKER not in owner:
        raise ValueError("Generated GLAZE artifact is missing the bounded workaround marker")
    for name, text in bundle.items():
        unexpected = _imports(text) - set(FILES)
        if unexpected:
            raise ValueError(f"Generated GLAZE CSS imports an unpinned file from {name}: {sorted(unexpected)}")


def fetch_bundle(timeout: float = 20.0) -> dict[str, str]:
    confirm_known_stable_defect_missing(timeout=timeout)
    raw_bundle: dict[str, str] = {}
    for name in FILES:
        try:
            with urlopen(_request(name), timeout=timeout) as response:
                if response.status != 200:
                    raise ValueError(f"Unexpected HTTP status for {name}: {response.status}")
                raw = response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            raise ValueError(f"Unable to fetch pinned GLAZE source {name}: {exc}") from exc
        try:
            raw_bundle[name] = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"Pinned GLAZE source is not UTF-8: {name}") from exc
    validate_upstream_bundle(raw_bundle)
    bundle = apply_known_stable_workaround(raw_bundle)
    validate_bundle(bundle)
    return bundle


def install_glaze(destination: Path) -> tuple[Path, ...]:
    bundle = fetch_bundle()
    destination.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        raise ValueError("GLAZE destination must not be a symlink")
    written: list[Path] = []
    for name in FILES:
        path = destination / name
        path.write_text(bundle[name], encoding="utf-8")
        written.append(path)
    return tuple(written)
