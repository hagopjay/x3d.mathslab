# Aha Atlas validation scope

Baseline: `24c9bbd8ad92e477c56f239476cd3dff7c05ecb2`.
Historical browser receipts describe the earlier six-lesson release.

| Instrument | Current scope |
|---|---|
| Python unittest suite | 119 tests: identities, extremes, presets, metadata recovery, export budgets, schemas, HTTP, MCP wrapper and inherited renderer controls |
| UI concurrency harness | Five request/scene/export controls with explicit DOM/native-consumer adapters |
| Learning UI harness | Search/filter, partial presets, explanations, legends, HTTPS resources, metadata reset and empty results |
| Original independent probe | Separate references for the original six lessons, including SciPy DOP853 Lorenz comparison |
| Aha independent probe | Randomized independent checks for the new models; `receipts/aha-independent.json` |
| Math MCP stdio probe | Initialization, three read-only tools, twelve-lesson catalog, scene calls for all twelve, source identity and refusal control |
| Pinned x3d_mcp | Twelve defaults pass X3D 4.0 XSD and semantic checks; two paired bad controls caught |
| Manim source | Defaults compile; additional extremes/presets parse. No video rendered. |

Run `python3 tools/check_release.py` for current numerical, transport, schema,
export and UI-adapter evidence. Receipts identify source hashes and environments;
they do not assert a theorem or measured learning outcomes.

## Browser limitation in this run

A fresh native X_ITE/Pyodide smoke could not execute here. Playwright's bundled
Chromium was absent. Installed Chromium could not create a required Unix socket
(`Operation not permitted`), and the separate cloud browser could not reach the
loopback server. These are environment limitations, not passing browser results.
No current screenshot, pixel-quality, GPU-performance, mobile-layout, or actual
Pyodide-run claim is made. The stdlib-only/static-module closure tests pass.

On a browser-capable host, start the local server and run
`node tools/browser_smoke.js http://127.0.0.1:8850/`. Set `MATHLAB_CHROMIUM` to a
system Chromium executable if necessary. Serve the repository root on another
port and open `/web/` to exercise Pyodide. Check all twelve scenes, animations,
presets, filters, exports, atlas link and a narrow viewport before deployment.
The smoke tool records launch failures as `not_run`, executed failures as `fail`,
and succeeds only when its declared checks pass.

The numerical models and X3D documents have direct automated evidence. Rendered
clarity and instructional effectiveness still require observation on target
hardware and with learners.
