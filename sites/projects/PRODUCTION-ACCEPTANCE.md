# Projects production acceptance

The Projects V1.4 source/build migration is not production acceptance.

Production acceptance requires all of the following against the canonical `goreecloud-projects` Cloudflare Pages project:

1. Repository: `GoreeCloud/goreecloud-static-websites`.
2. Production branch: `main`.
3. Root directory: `sites/projects`.
4. Build command: `python3 build.py`.
5. Build output directory: `dist`.
6. Custom domain: `projects.goreecloud.com`.
7. Exact deployed-byte and response-header verification using `python verify_v14_deployment.py --target production` after building the candidate artifact.
8. Canonical-domain rendered browser acceptance using `python browser_v14_remote_smoke.py`.
9. Verified rollback/legacy-source retirement state before advancing the migration registry.

Do not infer production acceptance from a successful source build, GitHub Actions run, Cloudflare deployment notification, or an apparently healthy public page alone.
