# Wardveil Security Reporting Policy

GoreeCloud welcomes good-faith security reports affecting the public GoreeCloud website and publicly available GoreeCloud software.

**Wardveil Security by GoreeCloud** is the platform-wide first-party security system and shared security plane. Foundation 0.9 defines scoped Wardveil-native trust, policy, protection, detection, scanning, quarantine, response, audit, and Security Center capabilities while applications, hosting controls, infrastructure, scanners, authorized executors, and other owning systems remain authoritative for the technical state and actions they control.

## Reporting a vulnerability

Do **not** open a public GitHub issue, pull request, discussion, or other public thread containing vulnerability details, credentials, private data, exploit instructions, or sensitive infrastructure information.

Send security reports to **security@goreecloud.com**.

The public reporting policy is available at:

- https://www.goreecloud.com/security.html
- https://www.goreecloud.com/.well-known/security.txt

A useful report should identify the affected public URL, repository, application, or version; describe the security impact; provide minimal reproducible steps; and remove unrelated sensitive data from screenshots, logs, requests, responses, or proofs of concept.

## Scope and authorization boundary

The public reporting policy applies to public-facing GoreeCloud web properties and publicly available GoreeCloud software. It does not authorize testing of private family infrastructure, private services, accounts, devices, internal networks, administrative interfaces, credentials, or non-public data.

Do not access, retain, modify, or disclose information that does not belong to you. Do not perform destructive testing, denial-of-service activity, social engineering, credential attacks, service disruption, or high-volume automated testing that could materially degrade a GoreeCloud service.

## Wardveil identity boundary

**Sentinel Fold** is the owner-approved standalone primary visual mark for Wardveil Security. The Wardveil Security name and Security Center label are supporting identity rather than part of the emblem itself. Branding does not establish security evidence or technical acceptance.

Wardveil security claims must remain tied to the evidence and authority responsible for the represented state. A Policy decision, transport receipt, storage-health result, scanner brand, Security Center screen, or other presentation fact cannot by itself prove that a protection action executed. This repository policy does not use a blanket protection claim to imply that every GoreeCloud system or control has been independently verified.

ClamAV is the initial replaceable signature-based malware engine beneath Wardveil Scan. The production ClamAV scanner runtime is deployed and accepted at the scanner-evidence layer. That acceptance does not establish end-to-end Wardveil Scan application acceptance or a blanket antivirus claim. Authenticated application-consumer routing, quarantine execution, and environment-specific integration evidence remain separately gated before broader protection claims are made.

## Handling and disclosure

Credible reports are reviewed and prioritized according to likely impact, exploitability, exposure, and the safety of affected users or data. Additional technical detail may be requested when needed to reproduce or understand a report.

GoreeCloud does not currently offer a bug bounty or guaranteed response timeline. Please allow a reasonable opportunity to understand and remediate a report before publicly disclosing exploit details.

This repository policy is intended to stay consistent with the canonical public security-reporting guidance at https://www.goreecloud.com/security.html.
