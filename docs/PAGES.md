# Static hosting (GitHub Pages) mode

Insight Expeditions adds `lessons_inference.py` and `lessons_science.py` to
the shared stdlib-only browser module inventory. The current catalog has eighteen
lessons. Static import-contract checks cover all dependencies; fresh browser
render evidence is recorded separately in [EXPEDITIONS-VALIDATION.md](EXPEDITIONS-VALIDATION.md).

The Aha Atlas extension adds `lessons_analysis.py` and `lessons_structures.py` to
the same stdlib-only Pyodide installation list. All twelve domains are now in
the catalog and parameter-card schema. Current automated contract checks pass;
a fresh native browser/Pyodide render could not run on this host. The measured
six-lesson browser results below describe the earlier release, not this one.
See [AHA-VALIDATION.md](AHA-VALIDATION.md).

Every number below names its instrument. Receipts: `receipts/browser-smoke-pages.json`,
`receipts/browser-smoke-server.json`, `receipts/runtime-parity.json`.

## Design

| Piece | Server mode (`run_mathlab.py`) | Pages mode |
|---|---|---|
| Transport | loopback HTTP `/api/*` | `web/static-api.js` calling Pyodide in the page |
| Python | local CPython | Pyodide 0.27.7 = CPython 3.12.7 on WebAssembly, `pyodide.js` pinned by SRI sha384 |
| Model code | `mathlab/*.py` | the same files, fetched from `../mathlab/` and written into the Pyodide filesystem |
| Request gate | `decode_request` (32 KiB, strict JSON, finite numbers) | the same function, same 4 MiB response budget |
| Manim | source text from `/api/manim` | source text from the same generator; **never imported or executed** |
| Selection | `/api/health` answers `x3d.mathlab` on 127.0.0.1/localhost | any other host uses Pyodide |

`tests/test_pages.py` fails if the installed-module list drifts from the files, if any installed module imports
something outside the standard library, or if `mcp_server` (the MCP SDK wrapper) is ever shipped to the browser.

## Safety boundary

Pages has no server: nothing accepts code, so there is no arbitrary-code endpoint. The in-browser Python can only
evaluate the six enumerated lessons. Manim rendering executes Python and remains a **local-only** step.
Third-party code loaded at runtime: `cdn.jsdelivr.net/pyodide/v0.27.7/full/` (pinned version; `pyodide.js` SRI-checked).

## Measured (Chromium via Playwright 1.63.0, Linux, software GL)

* All six lessons render a native X_ITE scene from Pyodide: 8 scene root nodes each; first scene about 5.0 s
  including the Pyodide download over the sandbox proxy; each later lesson switch about 2.1-2.5 s wall (includes a 1.5 s settle wait in the probe).
* Parameter nudge changes the model identity; Manim download yields `mathlab-gradient.py` (104,672 bytes) with a `Scene` class.
* Zero console errors in both modes.

## Cross-runtime reproducibility (a finding)

Same source files, same default parameters, native CPython 3.13.18/glibc versus Pyodide 3.12.7/Chromium:

| Lesson | floats compared | differing | max abs diff | sample hash equal |
|---|---:|---:|---:|---|
| linear | 990 | 18 | 2.220e-16 | no |
| derivative | 759 | 5 | 4.441e-16 | no |
| integral | 1206 | 0 | 0 | yes |
| fourier | 2314 | 20 | 3.331e-16 | no |
| lorenz | 6073 | 0 | 0 | yes |
| gradient | 5041 | 0 | 0 | yes |

The three differing lessons use `sin`, `cos`, `exp`; the three identical ones use +, *, sqrt. Differences are about
one unit in the last place, so the identity hash (`sample_sha256`) is a **same-runtime** identity. Source hashes match
across runtimes. Compare numbers with a tolerance across runtimes, never by hash.

## Enable Pages

Settings -> Pages -> Build and deployment -> Source: **Deploy from a branch** -> Branch **main**, folder **/ (root)** -> Save.
The root `index.html` redirects to `web/`. `.nojekyll` is present so vendored files are served as-is.

## Known limits

* First load needs the network for Pyodide (about 10 MB); offline use needs the local server.
* The 3D view zooms the authored viewpoint 25% closer at runtime (view-only; the X3D bytes are unchanged).
* The shipped `receipts/*` were produced on Linux; they are not claims about your machine.

## 18-lesson verification (17 Nov 2026, second launch)

Instruments: CPython 3.13.18, mcp 2.3.0, SciPy 1.17.0, Node 22.23.4, Chromium 153.0.8010.12 via Playwright 1.63.0 (software GL),
Pyodide 0.27.7, `x3d_mcp` b5c9956 (XSD 4.0 plus semantic checks, 18 worlds plus 2 negative controls).

* `tools/check_release.py`: pass, 9 instruments, 148 Python tests, 3 Node UI tests, source drift none.
* Both transports render all 18 lessons natively with 0 console errors; a parameter nudge changes the model identity;
  the Manim source download works (`receipts/browser-smoke-pages-18.json`, `receipts/browser-smoke-server-18.json`).
* Cross-runtime parity extended to all 18 (`receipts/runtime-parity-18.json`): 7 lessons bit-identical
  (integral, lorenz, gradient, probability, least_squares, bayes, refraction), 11 differ by at most
  4.44e-16 absolute. The bound did not grow with the 12 new lessons.
* The first six lessons are preserved at branch `archive-v0.1.1-six-lessons`.
