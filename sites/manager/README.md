# GoreeCloud Manager public website

Canonical static website source for `manage.goreecloud.com`.

This package was migrated from `GoreeCloud/goreecloud-manager/website`. It contains only the public informational website; the authenticated private Manager application remains in `GoreeCloud/goreecloud-manager` and is outside this repository's static-site boundary.

## Build and validation

From the repository root:

```bash
python sites/manager/scripts/validate_public_site.py
GLAZE_UI_SOURCE=/path/to/goreecloud-glaze-ui python sites/manager/scripts/build_public_site.py
python sites/manager/scripts/validate_public_site.py --dist
node --check sites/manager/site.js
```

The site pins Glaze UI 2.2.0 Stable at commit `6731098b28dd0393faa878c70d989a221d714a20`. The build verifies every Glaze CSS blob against `glaze.lock.json` before writing `sites/manager/dist/`.

## Migration status

Source and the reproducible build/validation contract are now centralized here. Deployment still points at the legacy source until a separate Cloudflare Pages cutover and production verification are completed. Do not remove the legacy Manager website source before that cutover is accepted.
