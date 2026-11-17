# Source and third-party notices

The supplied Manim MCP source retains its original MIT declaration and author
metadata in `pyproject.toml`. Historical planning/handoff documents are retained
as supplied; their environment and render claims are not fresh evidence.

| Component | Retained identity | Notice |
|---|---|---|
| X_ITE | 16.8.0 published npm archive, SHA-512 pinned by `tools/vendor_xite.py` | MIT primary license, `web/vendor/x_ite/LICENSE.md`; all published bundled notices retained under `LICENSES/` |
| x3d_mcp validation subset | `b5c9956917714747fe1d034c729612e99b0f09c9` | Unmodified 19-file source/schema/license subset; Web3D license at `vendor/x3d_mcp/LICENSE` |
| MCP Python SDK | 1.29.0 observed in protocol checks | Optional installed development/transport dependency, upstream MIT notice |
| lxml / jsonschema | Pinned in `tools/requirements-validation.txt` | Optional validation dependencies, respective upstream notices |
| SciPy | Version retained in independent probe | Optional development comparator, upstream BSD notices |

X_ITE's whole published dist tree, package metadata and license files are
retained unchanged, rather than assuming its dynamically loaded component/font
assets are optional. `web/vendor/x_ite/ORIGIN.json` inventories every retained
byte. `vendor/x3d_mcp/ORIGIN.json` and the local validation adapter identify the
consumed upstream subset. Those hashes identify local inputs, not independently
authenticated publishers or complete dependency-environment reproducibility.

No Manim library installation or rendered video is bundled. The project supplies
Manim source generation and the inherited trusted-local renderer source.
