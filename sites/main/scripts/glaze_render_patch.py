"""Install the Glaze UI 2.0 normalization at the public HTML render boundary.

This module is imported by the isolated site builder before any caller captures
``render_repository_portfolio.render_public_file``. That makes the same reviewed
render function available to the build artifact validator and the remote deployment
verifier, so byte-for-byte checks compare Cloudflare output with the actual Glaze UI
2.0 candidate rather than pre-normalized source templates.
"""

from __future__ import annotations

import render_repository_portfolio as portfolio

from glaze_ui_2 import apply_glaze_ui_2

_PATCH_FLAG = "_goreecloud_glaze_ui_2_render_patch"

if not getattr(portfolio, _PATCH_FLAG, False):
    _base_render_public_file = portfolio.render_public_file

    def render_public_file(relative: str, source: str, manifest: dict) -> str:
        return apply_glaze_ui_2(_base_render_public_file(relative, source, manifest))

    portfolio.render_public_file = render_public_file
    setattr(portfolio, _PATCH_FLAG, True)
