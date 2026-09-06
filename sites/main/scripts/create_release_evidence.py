#!/usr/bin/env python3
"""Create one fail-closed release-evidence record from the canonical template.

The generator intentionally does not determine release readiness, fetch remote evidence,
mark acceptance checkboxes, or authorize any action. It only creates a correctly named,
candidate-bound working record for later human and automated evidence entry.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "docs" / "release-evidence-template.md"
OUTPUT_DIR = ROOT / "docs" / "release-evidence"
CENTRAL = ZoneInfo("America/Chicago")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fail(message: str) -> int:
    print(f"Release evidence record creation failed: {message}", file=sys.stderr)
    return 1


def validate_commit_sha(value: str) -> str:
    """Require the canonical lowercase 40-character Git commit form."""
    if not SHA_RE.fullmatch(value):
        raise ValueError("--commit must be exactly 40 lowercase hexadecimal characters")
    return value


def validate_record_date(value: str) -> str:
    """Require a real ISO calendar date suitable for the technical filename."""
    if not DATE_RE.fullmatch(value):
        raise ValueError("--date must use ISO YYYY-MM-DD format")
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("--date must be a valid calendar date") from exc
    return value


def commit_exists(commit_sha: str) -> bool:
    """Confirm the supplied SHA resolves to a commit in the local repository."""
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{commit_sha}^{{commit}}"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def format_central_timestamp(moment: datetime) -> str:
    """Format a timestamp using GoreeCloud's Central Time / 12-hour convention."""
    local = moment.astimezone(CENTRAL)
    hour = local.strftime("%I").lstrip("0") or "12"
    return f"{local.strftime('%B')} {local.day}, {local.year} at {hour}:{local.strftime('%M %p %Z')}"


def render_record(template_text: str, commit_sha: str, created_at: datetime) -> str:
    """Bind a working template copy to one exact candidate without accepting it."""
    if "[x]" in template_text.lower():
        raise ValueError("canonical release evidence template unexpectedly contains a pre-checked item")

    record_date = created_at.astimezone(CENTRAL).date().isoformat()
    short_sha = commit_sha[:12]
    title = f"# GoreeCloud Website Release Evidence — {record_date} — {short_sha}"

    lines = template_text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError("canonical release evidence template is missing its expected title")
    lines[0] = title
    rendered = "\n".join(lines).rstrip() + "\n"

    candidate_marker = "- Exact candidate commit (40-character SHA):"
    if rendered.count(candidate_marker) != 1:
        raise ValueError("canonical template must contain exactly one candidate-SHA field")
    rendered = rendered.replace(candidate_marker, f"{candidate_marker} {commit_sha}", 1)

    metadata = (
        "\n## Record metadata\n\n"
        "- Record state: **Working — not accepted**\n"
        f"- Record created: {format_central_timestamp(created_at)}\n"
        f"- Bound candidate commit: `{commit_sha}`\n"
        "- Generator behavior: template copy and candidate binding only; no validation, acceptance, or authorization is inferred\n"
    )

    purpose_heading = "\n## Purpose\n"
    if purpose_heading not in rendered:
        raise ValueError("canonical template is missing its Purpose section")
    rendered = rendered.replace(purpose_heading, metadata + purpose_heading, 1)

    if "[x]" in rendered.lower():
        raise ValueError("generated record unexpectedly contains a pre-checked item")
    return rendered


def create_record(
    commit_sha: str,
    *,
    record_date: str | None = None,
    created_at: datetime | None = None,
    output_dir: Path = OUTPUT_DIR,
    verify_commit: bool = True,
) -> Path:
    """Create a new candidate-bound record and refuse any overwrite."""
    commit_sha = validate_commit_sha(commit_sha)
    now = created_at or datetime.now(CENTRAL)
    chosen_date = validate_record_date(record_date) if record_date else now.astimezone(CENTRAL).date().isoformat()

    if verify_commit and not commit_exists(commit_sha):
        raise ValueError("--commit does not resolve to a commit in this repository")

    if not TEMPLATE.is_file():
        raise ValueError("canonical release evidence template is missing")
    if TEMPLATE.is_symlink():
        raise ValueError("canonical release evidence template must not be a symlink")

    template_text = TEMPLATE.read_text(encoding="utf-8")
    rendered = render_record(template_text, commit_sha, now)

    if chosen_date != now.astimezone(CENTRAL).date().isoformat():
        generated_date = now.astimezone(CENTRAL).date().isoformat()
        rendered = rendered.replace(
            f"# GoreeCloud Website Release Evidence — {generated_date} — {commit_sha[:12]}",
            f"# GoreeCloud Website Release Evidence — {chosen_date} — {commit_sha[:12]}",
            1,
        )

    if output_dir.exists() and output_dir.is_symlink():
        raise ValueError("release evidence output directory must not be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)

    destination = output_dir / f"{chosen_date}-{commit_sha[:12]}-release-evidence.md"
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"refusing to overwrite existing release evidence record: {destination}")

    with destination.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered)
    return destination


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a fail-closed GoreeCloud website release-evidence record for one exact Git commit."
    )
    parser.add_argument(
        "--commit",
        required=True,
        help="Exact lowercase 40-character Git commit SHA for the release candidate.",
    )
    parser.add_argument(
        "--date",
        help="Optional ISO YYYY-MM-DD record date; defaults to today's date in America/Chicago.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        destination = create_record(args.commit, record_date=args.date)
    except (OSError, ValueError, FileExistsError) as exc:
        return fail(str(exc))

    print(f"Created working release evidence record: {destination.relative_to(ROOT)}")
    print("No validation, acceptance, merge, visibility, DNS, Cloudflare, or production authorization was inferred.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
