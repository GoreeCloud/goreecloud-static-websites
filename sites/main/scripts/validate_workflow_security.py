#!/usr/bin/env python3
"""Validate GitHub Actions supply-chain, revision-integrity, and least-privilege controls."""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
VALIDATE_WORKFLOW = WORKFLOWS / "validate.yml"
VERIFY_WORKFLOW = WORKFLOWS / "verify-deployment.yml"
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
USES_RE = re.compile(r"^\s*uses:\s*([^\s#]+)", re.MULTILINE)
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
WRITE_PERMISSION_RE = re.compile(r"(?mi)^\s*[A-Za-z0-9_-]+\s*:\s*write\s*(?:#.*)?$")
MUTABLE_RUNNER_RE = re.compile(r"(?m)^\s*runs-on:\s*[^\s#]*-latest\s*(?:#.*)?$")
REQUIRED_RUNNER = "ubuntu-24.04"
REQUIRED_PYTHON = "3.13.14"
REQUIRED_NODE = "22.22.0"
VALIDATION_SOURCE_REF = "ref: ${{ github.event.pull_request.head.sha || github.sha }}"
REMOTE_SOURCE_REF = "ref: ${{ github.sha }}"
REQUIRED_ACTIONS = (
    "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",  # v7.0.1
    "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97",  # v7.0.0
    "actions/setup-node@820762786026740c76f36085b0efc47a31fe5020",  # v7.0.0
)


def require(errors: list[str], text: str, marker: str, message: str) -> None:
    if marker not in text:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    workflow_paths = sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")])

    if not workflow_paths:
        errors.append("No GitHub Actions workflow files were found.")

    for path in workflow_paths:
        text = path.read_text(encoding="utf-8")
        if MUTABLE_RUNNER_RE.search(text):
            errors.append(f"Workflow runner must not use a mutable *-latest label: {path.relative_to(ROOT)}")
        for action_ref in USES_RE.findall(text):
            if action_ref.startswith("./") or action_ref.startswith("docker://"):
                continue
            if "@" not in action_ref:
                errors.append(f"External action is missing an immutable ref in {path.relative_to(ROOT)}: {action_ref}")
                continue
            action, ref = action_ref.rsplit("@", 1)
            if not action or not SHA_RE.fullmatch(ref):
                errors.append(
                    f"External action must be pinned to a full 40-character commit SHA in "
                    f"{path.relative_to(ROOT)}: {action_ref}"
                )

    if not VALIDATE_WORKFLOW.exists():
        errors.append(".github/workflows/validate.yml is required.")
    else:
        validation = VALIDATE_WORKFLOW.read_text(encoding="utf-8")

        if re.search(r"(?m)^\s*pull_request_target\s*:", validation):
            errors.append("Validation workflow must not use pull_request_target.")
        if re.search(r"(?mi)^\s*permissions\s*:\s*write-all\s*(?:#.*)?$", validation):
            errors.append("Validation workflow must not request write-all permissions.")
        if WRITE_PERMISSION_RE.search(validation):
            errors.append("Validation workflow must not request any write permission.")
        if "${{ secrets." in validation:
            errors.append("Validation workflow must not consume repository or environment secrets.")

        require(errors, validation, "permissions:\n  contents: read", "Validation workflow must declare read-only contents permission.")
        require(errors, validation, "concurrency:\n", "Validation workflow must define concurrency control.")
        require(errors, validation, "cancel-in-progress: true", "Validation workflow must cancel superseded runs.")
        require(errors, validation, f"runs-on: {REQUIRED_RUNNER}", f"Validation job must use the explicit {REQUIRED_RUNNER} runner family.")
        require(errors, validation, "timeout-minutes: 10", "Validation job must retain its 10-minute timeout.")
        require(errors, validation, VALIDATION_SOURCE_REF, "Validation checkout must execute the exact pull-request head SHA or exact push SHA.")
        require(errors, validation, "persist-credentials: false", "Checkout must keep persisted Git credentials disabled.")
        require(errors, validation, "fetch-depth: 0", "Validation checkout must retain full reachable history for publication preflight.")
        require(errors, validation, f'python-version: "{REQUIRED_PYTHON}"', f"Validation Python must be pinned exactly to {REQUIRED_PYTHON}.")
        require(errors, validation, f'node-version: "{REQUIRED_NODE}"', f"Validation Node.js must be pinned exactly to {REQUIRED_NODE}.")

        for action_ref in REQUIRED_ACTIONS:
            require(
                errors,
                validation,
                action_ref,
                f"Validation workflow must retain the reviewed Node 24-capable immutable action pin: {action_ref}",
            )

        required_validation_commands = (
            ("python scripts/validate_workflow_security.py", "workflow-security validator"),
            ("python scripts/validate_repository_hygiene.py", "repository sensitive-file hygiene validator"),
            ("python scripts/validate_repository_history.py", "full-history publication safety preflight"),
            ("python scripts/validate_license.py", "source-license and notice validator"),
            ("python scripts/validate_governance_readiness.py", "GoreeCloud governance-readiness validator"),
            ("python scripts/validate_repository_portfolio.py", "repository portfolio integrity validator"),
            ("python scripts/validate_public_runtime_status.py", "public runtime status integrity validator"),
            ("python scripts/validate_security_policy.py", "security-reporting and security.txt freshness validator"),
            ("python scripts/validate_privacy_policy.py", "privacy-statement validator"),
            ("python scripts/validate_browser_origin_integrity.py", "first-party browser-origin and statelessness validator"),
            ("python scripts/validate_accessibility.py", "whole-site structural accessibility validator"),
            ("python scripts/validate_glaze_ui.py", "Glaze UI design-contract validator"),
            ("python scripts/validate_public_semantics.py", "canonical search/social metadata validator"),
            ("python scripts/validate_public_surface.py", "whole-site crawler/sitemap validator"),
            ("python scripts/validate_performance_budget.py", "performance-budget validator"),
            ("python scripts/build_public_site.py", "isolated public-site build"),
            ("python scripts/validate_build_artifact.py", "isolated build-artifact validator"),
            ("python scripts/verify_remote_deployment.py --check-config", "remote-verifier configuration check"),
            ("python scripts/verify_remote_deployment.py --target branch-preview", "same-repository pull-request branch-preview verifier"),
            ("python scripts/verify_remote_deployment.py --target production", "main-branch production verifier"),
            ('python -m unittest discover -s tests -p "test_*.py"', "offline regression test suite"),
            ("python scripts/validate_release_evidence.py", "candidate release-evidence validator"),
        )
        for command, label in required_validation_commands:
            require(errors, validation, command, f"Validation workflow must run the {label}.")

        require(
            errors,
            validation,
            "github.event_name == 'pull_request'",
            "Branch-preview verification must remain limited to pull-request events.",
        )
        require(
            errors,
            validation,
            "github.event.pull_request.head.repo.full_name == github.repository",
            "Branch-preview verification must remain limited to same-repository pull requests.",
        )
        require(
            errors,
            validation,
            "Branch preview verification failed after $attempts attempts.",
            "Branch-preview verification must remain fail-closed after bounded retries.",
        )
        require(
            errors,
            validation,
            "github.event_name == 'push' && github.ref == 'refs/heads/main'",
            "Production verification must remain limited to pushes on main.",
        )
        require(
            errors,
            validation,
            "Production deployment verification failed after $attempts attempts.",
            "Production verification must remain fail-closed after bounded retries.",
        )

        build_position = validation.find("python scripts/build_public_site.py")
        artifact_position = validation.find("python scripts/validate_build_artifact.py")
        if build_position >= 0 and artifact_position >= 0 and build_position > artifact_position:
            errors.append("Validation workflow must build the isolated public artifact before validating it.")

    if not VERIFY_WORKFLOW.exists():
        errors.append(".github/workflows/verify-deployment.yml is required for deployed-site smoke verification.")
    else:
        remote = VERIFY_WORKFLOW.read_text(encoding="utf-8")
        if "${{ secrets." in remote:
            errors.append("Remote deployment verification workflow must not consume repository or environment secrets.")
        if WRITE_PERMISSION_RE.search(remote):
            errors.append("Remote deployment verification workflow must not request write permissions.")
        if re.search(r"(?m)^\s*pull_request_target\s*:", remote):
            errors.append("Remote deployment verification workflow must not use pull_request_target.")

        require(errors, remote, "workflow_dispatch:", "Remote deployment verification must remain manually dispatchable.")
        require(errors, remote, "schedule:", "Remote deployment verification must retain its production schedule.")
        if not re.search(r"(?m)^\s*-\s*cron:\s*(['\"]?)17 8 \* \* \*\1\s*$", remote):
            errors.append("Production smoke schedule must remain 8:17 AM America/Chicago.")
        if not re.search(r"(?m)^\s*timezone:\s*(['\"]?)America/Chicago\1\s*$", remote):
            errors.append("Production smoke schedule must retain the America/Chicago timezone.")
        require(errors, remote, "permissions:\n  contents: read", "Remote deployment workflow must remain read-only.")
        require(errors, remote, f"runs-on: {REQUIRED_RUNNER}", f"Remote deployment job must use the explicit {REQUIRED_RUNNER} runner family.")
        require(errors, remote, REMOTE_SOURCE_REF, "Remote deployment verification must check out the exact workflow run SHA.")
        require(errors, remote, "persist-credentials: false", "Remote verification checkout must disable persisted credentials.")
        require(errors, remote, "timeout-minutes: 5", "Remote deployment verification must retain its five-minute timeout.")
        require(errors, remote, f'python-version: "{REQUIRED_PYTHON}"', f"Remote verification Python must be pinned exactly to {REQUIRED_PYTHON}.")
        require(errors, remote, "- branch-preview", "Manual remote verification must retain branch-preview as a fixed choice.")
        require(errors, remote, "- production", "Manual remote verification must retain production as a fixed choice.")
        require(errors, remote, 'TARGET: ${{ inputs.target }}', "Manual target input must pass through an environment variable.")
        require(errors, remote, 'python scripts/verify_remote_deployment.py --target "$TARGET"', "Manual remote verification must invoke the fixed-target verifier safely.")
        require(errors, remote, "python scripts/verify_remote_deployment.py --target production", "Scheduled verification must use the literal production target.")
        require(errors, remote, "github.event_name == 'workflow_dispatch'", "Manual verification job must be event-guarded.")
        require(errors, remote, "github.event_name == 'schedule'", "Scheduled production verification job must be event-guarded.")

        for action_ref in REQUIRED_ACTIONS[:2]:
            require(
                errors,
                remote,
                action_ref,
                f"Remote deployment verification must retain immutable reviewed action pin: {action_ref}",
            )

        if "${{ inputs.target }}" in remote.replace('run-name: Verify ${{ inputs.target }} deployment', ""):
            unsafe_lines = [
                line for line in remote.splitlines()
                if "${{ inputs.target }}" in line and "TARGET:" not in line
            ]
            if unsafe_lines:
                errors.append("Manual deployment target must not be interpolated directly outside the env assignment.")

    if not DEPENDABOT.exists():
        errors.append(".github/dependabot.yml is required to keep pinned GitHub Actions reviewably updated.")
    else:
        dependabot = DEPENDABOT.read_text(encoding="utf-8")
        required_markers = (
            'package-ecosystem: "github-actions"',
            'directory: "/"',
            'interval: "weekly"',
            'day: "monday"',
            "open-pull-requests-limit: 5",
        )
        for marker in required_markers:
            if marker not in dependabot:
                errors.append(f"Dependabot GitHub Actions configuration is missing: {marker}")

    if errors:
        print("Workflow security validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Workflow security validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
