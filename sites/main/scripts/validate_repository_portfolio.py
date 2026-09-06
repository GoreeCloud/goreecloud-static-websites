#!/usr/bin/env python3
"""Validate the GoreeCloud repository portfolio and build-time static rendering."""

from __future__ import annotations

from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
import sys

from normalize_homepage import normalize_homepage
from render_repository_portfolio import render_homepage, render_repository_directory

ROOT = Path(__file__).resolve().parents[1]
PLATFORM_SYSTEMS = (
    "Glaze UI",
    "Privacy Shield",
    "Wardveil Security",
    "Everkeep",
    "GoreeCloud Mesh",
    "GoreeCloud Identity",
)


def validate_manifest(data: dict) -> list[str]:
    errors: list[str] = []
    groups = data.get("groups")
    counts = data.get("counts")
    if data.get("schema_version") != 1:
        errors.append("Repository portfolio manifest must use schema_version 1.")

    as_of = data.get("as_of")
    try:
        reviewed_date = date.fromisoformat(as_of) if isinstance(as_of, str) else None
    except ValueError:
        reviewed_date = None
    if reviewed_date is None:
        errors.append("Repository portfolio manifest must contain a valid YYYY-MM-DD as_of date.")
    elif reviewed_date > date.today():
        errors.append(f"Repository portfolio manifest as_of date must not be in the future: {as_of}.")

    if not isinstance(groups, list) or not groups:
        errors.append("Repository portfolio manifest must contain at least one group.")
        return errors
    if not isinstance(counts, dict):
        errors.append("Repository portfolio manifest must contain declared counts.")
        return errors

    names: list[str] = []
    visibilities: list[str] = []
    group_ids: list[str] = []
    for group in groups:
        if not isinstance(group, dict):
            errors.append("Every repository portfolio group must be an object.")
            continue
        group_id = group.get("id")
        label = group.get("label")
        repositories = group.get("repositories")
        if not isinstance(group_id, str) or not group_id:
            errors.append("Every repository portfolio group must have a non-empty id.")
        else:
            group_ids.append(group_id)
        if not isinstance(label, str) or not label:
            errors.append(f"Repository portfolio group {group_id!r} must have a non-empty label.")
        if not isinstance(repositories, list) or not repositories:
            errors.append(f"Repository portfolio group {group_id!r} must contain repositories.")
            continue
        for repository in repositories:
            if not isinstance(repository, dict):
                errors.append(f"Repository entry in group {group_id!r} must be an object.")
                continue
            name = repository.get("name")
            visibility = repository.get("visibility")
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
                errors.append(f"Invalid repository name in group {group_id!r}: {name!r}.")
                continue
            if visibility not in {"public", "private"}:
                errors.append(f"Repository {name} must declare public or private visibility.")
                continue
            for field in ("description", "role"):
                value = repository.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"Repository {name} must declare a non-empty {field}.")
            names.append(name)
            visibilities.append(visibility)

    for group_id in sorted(name for name, count in Counter(group_ids).items() if count > 1):
        errors.append(f"Duplicate repository portfolio group id: {group_id}.")
    for name in sorted(name for name, count in Counter(names).items() if count > 1):
        errors.append(f"Duplicate repository portfolio entry: {name}.")

    computed = {
        "total": len(names),
        "public": visibilities.count("public"),
        "private": visibilities.count("private"),
        "functional_groups": len(group_ids),
    }
    for key, actual in computed.items():
        if counts.get(key) != actual:
            errors.append(f"Repository portfolio count {key!r} must be {actual}, found {counts.get(key)!r}.")

    expected_current = {
        "goreecloud-app-store",
        "goreecloud-file-manager",
        "goreecloud-maps",
        "goreecloud-index",
        "goreecloud-branding-assets",
        "goreecloud-identity",
        "goreecloud-mesh",
        "goreecloud-glaze-ui",
    }
    missing = sorted(expected_current.difference(names))
    if missing:
        errors.append("Repository portfolio is missing current repositories: " + ", ".join(missing) + ".")
    if "goreecloud-logo" in names:
        errors.append("Retired goreecloud-logo repository must not remain in the current portfolio.")
    return errors


def validate_discovery_enhancement(main_js: str, repository_css: str) -> list[str]:
    errors: list[str] = []
    required_js = (
        "const repositoryDirectory = document.querySelector('.repo-directory-section');",
        "tools.className = 'repo-tools';",
        "searchInput.type = 'search';",
        "searchInput.autocomplete = 'off';",
        "groupSelect",
        "Repository visibility",
        "status.setAttribute('role', 'status');",
        "status.setAttribute('aria-live', 'polite');",
        "card.hidden = !matches;",
        "group.hidden = visibleInGroup === 0;",
        "directoryHeading.insertAdjacentElement('afterend', tools);",
        "not stored, added to the URL, or sent anywhere",
        "repositoryCards.length",
        "searchInput.focus();",
    )
    for marker in required_js:
        if marker not in main_js:
            errors.append(f"Repository discovery enhancement is missing required behavior: {marker}")

    if "const repositoryDirectory =" in main_js:
        source = main_js.split("const repositoryDirectory =", 1)[1]
        for marker in ("localStorage", "sessionStorage", "URLSearchParams", "history.pushState", "history.replaceState", "fetch(", "XMLHttpRequest", "sendBeacon"):
            if marker in source:
                errors.append("Repository search/filter controls must remain local, ephemeral, and network-independent: " + marker)

    for prohibited in ("public-info.js", "current-platform-update", "native-application-update"):
        if prohibited in main_js:
            errors.append(f"Public JavaScript must not inject editorial homepage content at runtime: {prohibited}")

    required_css = (
        ".repo-tools {",
        "min-height: var(--glaze-target-comfortable);",
        ".repo-filter-button[aria-pressed=\"true\"]",
        "@media (max-width: 1023px)",
        "@media (max-width: 599px)",
        "@media (prefers-reduced-motion: reduce)",
        "@media (prefers-reduced-transparency: reduce)",
        "@media (prefers-contrast: more)",
        "@media (forced-colors: active)",
        "@media print",
        ".repo-card[hidden], .repo-group[hidden] { display: block !important; }",
    )
    for marker in required_css:
        if marker not in repository_css:
            errors.append(f"Repository discovery presentation is missing required Glaze UI behavior: {marker}")
    return errors


def validate_summary_counts(text: str, counts: dict, context: str) -> list[str]:
    errors: list[str] = []
    for key, label in (("total", "current repositories"), ("public", "public repositories"), ("private", "private repositories")):
        values = [int(v) for v in re.findall(rf"<strong>(\d+)</strong><span>{re.escape(label)}</span>", text)]
        expected = counts[key]
        if expected not in values:
            errors.append(f"{context} repository summary is missing current {label}: {expected}.")
        for value in sorted(v for v in set(values) if v != expected):
            errors.append(f"{context} repository summary contains stale {label}: {value}; expected {expected}.")
    return errors


def validate_homepage_structure(homepage: str) -> list[str]:
    errors: list[str] = []
    if 'id="platform"' in homepage:
        errors.append("Rendered homepage must not restore the removed Platform Foundation section.")
    if 'id="development"' in homepage:
        errors.append("Rendered homepage must not duplicate Suite content in a Software & Development section.")
    if 'href="#platform"' in homepage or 'href="#development"' in homepage:
        errors.append("Rendered homepage navigation must not link to removed duplicate sections.")

    hero_match = re.search(r'<div class="hero-labels[^>]*>(.*?)</div>', homepage, re.DOTALL)
    if not hero_match:
        errors.append("Rendered homepage is missing its focused hero context.")
    else:
        hero = hero_match.group(1)
        if "Private • Self-hosted • Recoverable" not in hero:
            errors.append("Rendered homepage hero must preserve the concise platform-focus label.")
        for label in PLATFORM_SYSTEMS:
            if label in hero:
                errors.append(f"Platform-system detail belongs in the ecosystem section, not the focused hero: {label}.")

    website_match = re.search(r'<section id="websites".*?</section>', homepage, re.DOTALL)
    if not website_match:
        errors.append("Rendered homepage is missing the official website ecosystem section.")
    else:
        website_section = website_match.group(0)
        for label in PLATFORM_SYSTEMS:
            if label not in website_section:
                errors.append(f"Website ecosystem section must name current platform system: {label}.")
        for marker in (
            "Glaze UI 2.1.0 Stable",
            "Ten independently deployed public destinations",
            "Identity Center is the eleventh official first-party surface",
            "Publication Pending",
            "current 57-repository portfolio",
        ):
            if marker not in website_section:
                errors.append(f"Website ecosystem section is missing current-state marker: {marker}.")
        for stale in ("Glaze UI 2.0.0 Stable", "Glaze UI 2.1 remains Candidate"):
            if stale in website_section:
                errors.append(f"Website ecosystem section still contains superseded state: {stale}.")

    if "current-platform-update" in homepage or "native-application-update" in homepage:
        errors.append("Rendered homepage must not contain legacy runtime editorial overlays.")
    return errors


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads((root / "docs" / "repository-portfolio.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Repository portfolio manifest cannot be read: {exc}"]
    errors.extend(validate_manifest(data))
    if errors:
        return errors

    source_directory = (root / "repositories.html").read_text(encoding="utf-8")
    source_homepage = (root / "index.html").read_text(encoding="utf-8")
    try:
        directory = render_repository_directory(source_directory, data)
        homepage = normalize_homepage(render_homepage(source_homepage, data))
    except ValueError as exc:
        return [f"Repository portfolio static rendering failed: {exc}"]

    counts = data["counts"]
    errors.extend(validate_summary_counts(directory, counts, "Repository directory"))
    errors.extend(validate_summary_counts(homepage, counts, "Homepage"))
    errors.extend(validate_homepage_structure(homepage))
    if f"<strong>{counts['functional_groups']}</strong><span>functional groups</span>" not in homepage:
        errors.append(f"Homepage repository summary is missing the current functional-group count: {counts['functional_groups']}.")
    if f"GoreeCloud currently maintains {counts['total']} repositories" not in homepage:
        errors.append("Homepage repository teaser must state the manifest-derived current total.")

    repositories = [repo for group in data["groups"] for repo in group["repositories"]]
    for repository in repositories:
        name = repository["name"]
        visibility = repository["visibility"]
        if directory.count(f"<h4>{name}</h4>") != 1:
            errors.append(f"Rendered repository directory must contain exactly one card for {name}.")
        if f'<span class="repo-visibility {visibility}">{visibility.title()}</span>' not in directory:
            errors.append(f"Rendered repository {name} must display {visibility} visibility.")
        public_url = f"https://github.com/GoreeCloud/{name}"
        if visibility == "public" and public_url not in directory:
            errors.append(f"Public repository {name} must link to its canonical GitHub URL.")
        if visibility == "private" and public_url in directory:
            errors.append(f"Private repository {name} must not publish a direct repository link.")

    errors.extend(validate_discovery_enhancement(
        (root / "js" / "main.js").read_text(encoding="utf-8"),
        (root / "css" / "repositories.css").read_text(encoding="utf-8"),
    ))
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Repository portfolio validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Repository portfolio validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())