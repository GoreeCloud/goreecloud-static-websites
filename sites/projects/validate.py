#!/usr/bin/env python3
from pathlib import Path
import hashlib
import re

SITE = Path(__file__).resolve().parent
GLAZE_VERSION = "1.3.0"
GLAZE_REVISION = "8354308445da9ac35ced2b37a7f503a08a0aaf72"

required = [
    "index.html", "404.html", "README.md", "_headers",
    "assets/app.js", "assets/suite-portfolio.js", "assets/icon-refresh.js",
    "assets/styles.css", "assets/mobile-refresh.css", "assets/glaze-v1.3-consumer.css",
    "assets/goreecloud-logo.svg", "assets/manager.svg", "assets/glaze-ui-mark.svg", "assets/everkeep.svg",
    "assets/privacy-shield-icon.svg", "assets/wardveil-security-icon.svg",
    "assets/goreecloud-mesh-mark.svg", "assets/identity.svg",
]
for name in required:
    if not (SITE / name).is_file():
        raise SystemExit(f"missing Projects site file: {name}")

for obsolete in ("assets/glaze-ui-2.1.0.css",):
    if (SITE / obsolete).exists():
        raise SystemExit(f"obsolete Projects Glaze runtime asset must be absent: {obsolete}")

html = (SITE / "index.html").read_text(encoding="utf-8")
error_html = (SITE / "404.html").read_text(encoding="utf-8")
js = (SITE / "assets/app.js").read_text(encoding="utf-8")
portfolio = (SITE / "assets/suite-portfolio.js").read_text(encoding="utf-8")
icons = (SITE / "assets/icon-refresh.js").read_text(encoding="utf-8")
mobile = (SITE / "assets/mobile-refresh.css").read_text(encoding="utf-8")
readme = (SITE / "README.md").read_text(encoding="utf-8")
glaze = (SITE / "assets/glaze-v1.3-consumer.css").read_text(encoding="utf-8")
headers = (SITE / "_headers").read_text(encoding="utf-8")
combined = html + js + portfolio + icons + readme
active_direction = html + js + portfolio + readme


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


for needle in [
    "Suite products", "Integral platform systems", "GLAZE UI V1.3", "Privacy Shield",
    "Wardveil Security", "Everkeep", "GoreeCloud Mesh", "GoreeCloud Identity", "GoreeCloud Manager",
    "GoreeCloud AI", "GoreeCloud Code", "GoreeCloud Documents", "GoreeCloud Messenger",
    "GoreeCloud Gateway", "GoreeCloud Quill", "GoreeCloud File Manager", "GoreeCloud Maps",
    "GoreeCloud App Store", "GoreeCloud Index", "GoreeVault", "GoreeCloud Health",
    "GoreeCloud Reader", "GoreeCloud Router OS", "GoreeCloud Social", "GoreeCloud Home",
    "GoreeCloud Home Security", "Design Center", "Privacy Center", "Security Center",
    "Continuity Center", "Mesh Center", "Identity Center", "Sentinel Fold", "Weave",
]:
    if needle not in combined:
        raise SystemExit(f"current portfolio marker missing: {needle}")

for page_name, page in (("index", html), ("404", error_html)):
    for marker in (
        'data-glaze-version="1.3.0"',
        'name="goreecloud-glaze-ui" content="1.3.0"',
        f'name="goreecloud-glaze-source-revision" content="{GLAZE_REVISION}"',
        'data-glaze-ui="1.3.0"',
        "glaze-canvas",
    ):
        if marker not in page:
            raise SystemExit(f"{page_name} missing Glaze UI V1.3 marker: {marker}")

for stale in (
    'data-glaze-ui="2.1.0"',
    'name="goreecloud-glaze-ui" content="2.1.0"',
    "Glaze UI 2.1</strong><span>Current Stable baseline",
    "Design Center · Stable 2.1",
    "2.1.0 current Stable",
    "Glaze UI 2.1.0 Stable",
):
    if stale in active_direction + error_html:
        raise SystemExit(f"superseded active Glaze UI direction remains: {stale}")

for marker in (
    "GLAZE UI V1.3 / 1.3.0 consumer layer",
    GLAZE_REVISION,
    "--projects-v13-touch:48px",
    "--projects-v13-touch-assisted:56px",
    "prefers-reduced-motion:reduce",
    "prefers-reduced-transparency:reduce",
    "prefers-contrast:more",
    "forced-colors:active",
    "pointer:coarse",
    "focus-visible",
    "backdrop-filter",
):
    if marker not in glaze:
        raise SystemExit(f"Projects V1.3 consumer-layer marker missing: {marker}")

suite_expected = [
    "GoreeCloud Notes", "GoreeCloud Memos", "GoreeCloud Tasks", "GoreeCloud Calendar", "GoreeCloud Contacts", "GoreeCloud Documents",
    "GoreeCloud Drive", "GoreeCloud File Manager", "GoreeCloud Sync", "GoreeCloud Photos", "GoreeCloud Gallery", "GoreeCloud Music", "GoreeCloud Video", "GoreeCloud Bookmarks", "GoreeCloud Reader",
    "GoreeCloud Mail", "GoreeCloud Messenger", "GoreeCloud Search", "GoreeCloud Browser", "GoreeCloud Feed", "GoreeCloud Location", "GoreeCloud Maps", "GoreeCloud Social",
    "GoreeCloud Keyboard", "GoreeCloud Launcher", "GoreeCloud Terminal",
    "GoreeCloud Manager", "GoreeCloud App Store", "GoreeCloud Identity", "GoreeVault", "GoreeCloud Backup", "GoreeCloud Network", "GoreeCloud DNS", "GoreeCloud Gateway", "GoreeCloud Notify", "GoreeCloud Monitor", "GoreeCloud Changelogs",
    "GoreeCloud AI", "GoreeCloud Index", "GoreeCloud Code",
    "GoreeCloud Health", "GoreeCloud Home", "GoreeCloud Home Security",
    "GoreeCloud Router OS", "GoreeCloud Website",
]
if len(suite_expected) != 45 or len(set(suite_expected)) != 45:
    raise SystemExit("validator Suite portfolio authority must contain exactly 45 unique product names")
try:
    group_block = portfolio.split("const suitePortfolioGroups=Object.freeze({", 1)[1].split("});", 1)[0]
except IndexError as exc:
    raise SystemExit("Projects Suite portfolio group authority is missing") from exc
portfolio_names = re.findall(r"'((?:GoreeCloud|GoreeVault)[^']*)'", group_block)
if len(portfolio_names) != 45 or set(portfolio_names) != set(suite_expected):
    missing = sorted(set(suite_expected) - set(portfolio_names))
    extra = sorted(set(portfolio_names) - set(suite_expected))
    raise SystemExit(f"Projects Suite portfolio drift: count={len(portfolio_names)} missing={missing} extra={extra}")
if len(re.findall(r"^\s*'[^']+':\[", group_block, flags=re.MULTILINE)) != 9:
    raise SystemExit("Projects Suite portfolio must preserve exactly 9 functional product groups")
for marker in (
    "suitePortfolioNames.size!==45",
    "Object.keys(suitePortfolioGroups).length!==9",
    "entry.suiteMember=suitePortfolioNames.has(entry.name)",
    "filter==='Suite products'",
    "suiteProducts.length!==45",
    "Integral platform systems",
):
    if marker not in portfolio + html:
        raise SystemExit(f"Projects Suite membership contract missing: {marker}")
for extra_project in ("GoreeCloud GitHub Dashboard", "GoreeCloud Firefox Extensions", "GoreeCloud Autobiography", "GoreeCloud Vault Server"):
    if extra_project in portfolio_names:
        raise SystemExit(f"additional project must not be counted as a Suite product: {extra_project}")
if '<strong id="app-count">45</strong><span>Suite products</span>' not in html:
    raise SystemExit("Projects static summary must expose the authoritative 45-product Suite count")
if '<strong id="foundation-count">7</strong><span>Integral platform systems</span>' not in html:
    raise SystemExit("Projects static summary must expose the seven Integral Platform Systems")

for current in [
    "GoreeCloud AI", "GoreeCloud Code", "GoreeCloud Documents", "GoreeCloud Messenger",
    "GoreeCloud Gateway", "GoreeCloud Quill", "GoreeCloud Mesh", "GoreeCloud File Manager",
    "GoreeCloud Maps", "GoreeCloud App Store", "GoreeCloud Index", "GoreeVault",
    "GoreeCloud Health", "GoreeCloud Reader", "GoreeCloud Router OS", "GoreeCloud Social",
    "GoreeCloud Home", "GoreeCloud Home Security",
]:
    if f"name:'{current}'" not in js + portfolio:
        raise SystemExit(f"Projects source-native portfolio missing: {current}")

for required_truth in [
    "1.3.0 current Official Stable",
    "Adaptive Resonance",
    "Identity platform · active development",
    "Recursive resolution remains a separate responsibility",
    "Foundation 0.9 active · production runtime acceptance separate",
    "addCurrentPortfolioEntries();",
    "entry.status=update[0]",
    "entry.role=update[1]",
    "render();",
]:
    if required_truth not in js:
        raise SystemExit(f"current Projects source truth boundary missing: {required_truth}")

if "public-refresh.js" in html:
    raise SystemExit("Projects still depends on the superseded public-refresh overlay")
if "MutationObserver" in js + portfolio:
    raise SystemExit("Projects current source must not depend on a DOM MutationObserver for portfolio truth")

for stale in [
    "Gitea is the planned permanent",
    "planned permanent source-control authority",
    "1.5.0 current Stable",
    "2.0.0 current Stable",
    "2.1 remains Candidate",
    "Mesh Center · artwork pending approval",
    "GoreeCloud Mesh has no approved canonical artwork",
    "text-only-pending-approved-artwork",
    "recursive resolution, authoritative DNS",
    "27 current Suite applications",
]:
    if stale in active_direction:
        raise SystemExit(f"superseded Projects direction remains public: {stale}")

branding_repo = "GoreeCloud/goreecloud-branding-assets"
if f"brandingAuthority='{branding_repo}'" not in icons:
    raise SystemExit("Projects identity mapping must name the unified branding repository as authority")
for needle in [branding_repo, "catalog.json", "synchronized publication derivatives", "Sentinel Fold", "Weave"]:
    if needle not in readme:
        raise SystemExit(f"Projects branding-authority documentation missing: {needle}")

system_blobs = {
    "assets/goreecloud-logo.svg": "082936062de7839148db89ea3ab4e86ff71341b0",
    "assets/manager.svg": "024d82d5b5911e426216dfbd6a19d95cd6d71fc3",
    "assets/glaze-ui-mark.svg": "af8b70387bdaedb8d8388a1660b2d2ca29548fe2",
    "assets/privacy-shield-icon.svg": "62b10029d4104d0235afe634c21f55d0a826a63d",
    "assets/wardveil-security-icon.svg": "fb3d643cca5477c3f8d4e03ce10a3458fd12f407",
    "assets/everkeep.svg": "5f70a483e06147193944c816291d42774a8648b2",
    "assets/goreecloud-mesh-mark.svg": "0b2c6881668ce319081390b217f6d59b4298dd4d",
    "assets/identity.svg": "dc8287e385f86767f0105c48a8f234d8440d7623",
}
for relative, expected in system_blobs.items():
    actual = git_blob_sha(SITE / relative)
    if actual != expected:
        raise SystemExit(f"Projects synchronized branding derivative drifted: {relative}: expected {expected}, got {actual}")

for source in [
    "products/manager/app-icon.svg", "products/browser/app-icon.svg", "products/ai/app-icon.svg", "products/index/app-icon.svg",
    "systems/glaze-ui/glaze-ui-mark.svg", "systems/everkeep/everkeep.svg",
    "systems/wardveil-security/wardveil-security-icon.svg",
    "systems/goreecloud-mesh/goreecloud-mesh-mark.svg",
]:
    if source not in icons:
        raise SystemExit(f"Projects canonical branding source mapping missing: {source}")
if len(re.findall(r"'goreecloud-[^']+':\['products/[^']+/app-icon\.svg','[^']+\.svg'\]", icons)) < 31:
    raise SystemExit("Projects must map established products to approved unified-catalog artwork")
for forbidden in ["projectMonogram", "meshSymbol", "data:image/svg+xml"]:
    if forbidden in icons:
        raise SystemExit(f"Projects must not fabricate branding artwork: {forbidden}")

if '<img src="/assets/manager.svg"' not in html or "GoreeCloud Manager" not in html:
    raise SystemExit("Projects must present GoreeCloud Manager as an Integral Platform System using approved artwork")
if '<img src="/assets/goreecloud-mesh-mark.svg"' not in html or "Mesh Center · Weave" not in html:
    raise SystemExit("Projects Mesh foundation identity must publish the approved Weave mark")
if "Security Center · Sentinel Fold" not in html:
    raise SystemExit("Projects Wardveil foundation identity must identify Sentinel Fold")
if '<img src="/assets/identity.svg"' not in html or "Identity Center" not in html:
    raise SystemExit("Projects must present GoreeCloud Identity as a substantive platform system using approved origin-local artwork")
if "article.querySelector('.project-icon')?.remove()" not in icons or "entry.icon=''" not in icons:
    raise SystemExit("Projects must remove fallback platform logos from entries without approved artwork")
if "'goreecloud-index':['products/index/app-icon.svg','index.svg']" not in icons:
    raise SystemExit("Projects must use the approved canonical Index identity mapping")

for src in re.findall(r'src=["\']([^"\']+)', html):
    if src.startswith(("http:", "https:")):
        raise SystemExit(f"remote static browser resource prohibited in HTML: {src}")
for directive in ["Content-Security-Policy:", "Permissions-Policy:", "X-Content-Type-Options: nosniff"]:
    if directive not in headers:
        raise SystemExit(f"security header missing: {directive}")
if "img-src 'self' https://www.goreecloud.com" not in headers:
    raise SystemExit("Projects CSP must allow only self plus the first-party Website publication origin for imagery")
for forbidden in ["data:", "raw.githubusercontent.com", "githubusercontent.com"]:
    if forbidden in headers + icons:
        raise SystemExit(f"Projects image provenance policy must not allow or reference: {forbidden}")

if "localStorage" not in js or "data-theme-choice" not in html:
    raise SystemExit("local appearance preference contract missing")
release_boundary = "Public source, a successful build, active development, a release candidate, or a platform identity does not automatically establish production acceptance or protection."
if release_boundary not in html:
    raise SystemExit("source-versus-production boundary missing")
for pending in (
    "source-migrated-rendered-acceptance-pending",
    "Rendered, accessibility, performance, rollback, and production approval remain independently acceptance-gated.",
):
    if pending not in html:
        raise SystemExit(f"V1.3 consumer acceptance boundary missing: {pending}")

for needle in ["min-height:48px", "overflow-x:hidden", ".card-meta{flex-wrap:wrap", "@media(max-width:380px)"]:
    if needle not in mobile:
        raise SystemExit(f"Projects mobile hardening marker missing: {needle}")

for stylesheet in [
    "/assets/mobile-refresh.css?v=20260827-mobile2",
    "/assets/glaze-v1.3-consumer.css?v=20260910-v13",
]:
    if stylesheet not in html:
        raise SystemExit(f"Projects stylesheet reference missing: {stylesheet}")
for script in [
    "/assets/app.js?v=20260910-v13",
    "/assets/suite-portfolio.js?v=20260910-v45",
    "/assets/icon-refresh.js?v=20260910-portfolio45",
]:
    if script not in html:
        raise SystemExit(f"Projects cache-busted script reference missing: {script}")
if not (html.index("/assets/app.js?") < html.index("/assets/suite-portfolio.js?") < html.index("/assets/icon-refresh.js?")):
    raise SystemExit("Projects portfolio and branding scripts must execute in app → Suite authority → branding order")
if "Cache-Control: public, max-age=0, must-revalidate" not in headers:
    raise SystemExit("Projects mutable assets must revalidate instead of remaining browser-fresh for a day")
for stale_cache in ["max-age=86400", "stale-while-revalidate"]:
    if stale_cache in headers:
        raise SystemExit(f"Projects stale asset cache policy remains: {stale_cache}")

for forbidden in (
    "Projects V1.3 conformance passed",
    "production visually accepted",
    "production acceptance complete",
):
    if forbidden in active_direction:
        raise SystemExit(f"unsupported Projects acceptance claim: {forbidden}")

print(
    "GoreeCloud Projects source portfolio validation passed for GLAZE UI V1.3 source migration: "
    "exact 45-product / 9-group Suite membership, seven Integral Platform Systems, approved branding provenance, "
    "responsive/accessibility consumer layer, additional-project separation, and explicit production acceptance boundary"
)
