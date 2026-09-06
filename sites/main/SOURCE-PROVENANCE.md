# Source Provenance

- Legacy repository: `GoreeCloud/goreecloud-website`
- Immutable source revision: `18f5276d21b8eb3b55adc18e00e88aa11b6edfd8`
- Legacy root tree: `49e1723e4d28310f3e680c8c80249cb0f1a0d76f`
- Initial migration method: exact Git checkout followed by bounded rsync into `sites/main`.
- Excluded from central main-site authority: legacy `.github/`, legacy `sites/` sub-sites, generated `dist/`, and `goreecloud.platform.yaml`.
- The legacy `sites/` subtree was not duplicated because Projects, Roadmap, Blog, and Archive already have independent canonical packages under the central repository's `sites/` hierarchy.
- After import, `scripts/validate_glaze_ui.py` and `scripts/validate_responsive_layout.py` were intentionally adapted so cross-site validation resolves those canonical sibling packages instead of expecting duplicate `sites/main/sites/...` copies. This is a central-layout path adaptation only; it does not change public website behavior.
- `LEGACY-REPOSITORY-README.md` preserves the source repository README as migration evidence; `README.md` identifies the new canonical source boundary.
