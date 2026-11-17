# x3d.mathlab · Make a question visible

A local, inspectable mathematics laboratory for **curious to advanced** learners.
Six connected experiments pair manipulable geometry with equations, numerical
references, prediction questions and a path into the source. This is the first
working Math Lab edition, built on the supplied Manim MCP archive.

## Live (no install)

**https://hagopjay.github.io/x3d.mathslab/** runs the same six lessons on GitHub Pages. With no server there,
`web/static-api.js` loads pinned Pyodide 0.27.7 (CPython 3.12.7 on WebAssembly, SRI-checked) and runs the
unmodified `mathlab/*.py` kernels behind the same request gate. First visit downloads about 10 MB, cached after.
The page generates Manim **source text** only; rendering executes Python and stays local
(`python3 run_mathlab.py`, then the Manim steps in the field guide). There is no code-execution endpoint on Pages.
Details, measured parity and limits: [docs/PAGES.md](docs/PAGES.md).

## Start here

Unzip the complete distribution, then run `run.bat` on Windows or `bash run.sh`
in WSL/Linux/macOS. Alternatively:

```sh
python3 run_mathlab.py --open
```

Open **http://127.0.0.1:8850/** and keep the terminal running. Python 3.11+ is
required; 3.13+ is recommended. The observed development interpreter was 3.12.14.
The interactive lab uses the standard library and the bundled X_ITE 16.8.0
runtime. No npm install, Manim installation, LaTeX or API key is needed to play.
Do not open `web/index.html` directly: the local model API must be running.

## Six ways of seeing

| Experiment | Try this first | Go deeper |
|---|---|---|
| Linear transformations | Move transformation progress from identity to the target | Signed area, collapse, real eigendirections and residuals |
| Derivatives | Reduce h and watch the secant approach the tangent | Forward/central error and a known analytic derivative |
| Integration | Change rectangle count and left/mid/right sampling | Exact antiderivative, signed error and a scoped midpoint bound |
| Fourier motion | Animate rotating vectors, then add odd harmonics | Whole-period RMS, ringing and pointwise convergence distinctions |
| Lorenz dynamics | Compare two almost-identical beginnings | RK4, actual time step, initial-data sensitivity versus refinement error |
| Gradient descent | Increase the learning rate in a narrow valley | Hessian eigenvalues, exact recurrence and the stability boundary |

Use **Explore** for controls, **Understand** for short guided steps and the
prediction/reasoning loop, and **Source** for the current X3D document. Floating
inputs preserve exact catalog defaults such as β=8/3. Integer controls enforce
integer domains. Matrix and Fourier lessons can animate one parameter; reduced
motion disables that animation. Browser code serializes scene replacement and
keeps exports/camera/projection controls paused while a new model is pending.

The native view uses an actual X_ITE X3D scene. Drag to orbit and scroll to zoom.
A labeled SVG projection remains available when native 3D is unavailable; it
consumes the same sampled geometry. It is not a substitute for a native-rendering
or hardware-performance claim.

Read the self-contained [Mathlab Field Guide](docs/Mathlab-Field-Guide.html) for
roughly 6,000 words of derivations, experiments, heuristics and future vision.

## Why X3D belongs in the model loop

One normalized lesson configuration produces mathematical samples, native X3D,
and a baked Manim scene. The geometry has stable source IDs, bounded dimensions,
and metadata retaining lesson parameters and content identities. Standard
`IndexedLineSet`, `IndexedFaceSet`, `Sphere`, `Box`, `Transform` and `Viewpoint`
nodes preserve an inspectable artifact outside this web interface.

Exports are static sampled worlds. They do not serialize the HTML controls,
prove a theorem, promise another renderer's identical pixels, or create a
complete application checkpoint. X3D coordinates and floating-point shader
arithmetic have representation limits distinct from Python's numerical checks.
The [X3D contract](docs/X3D-CONTRACT.md) names these boundaries.

**Keep this experiment** saves a JSON lesson card; **Open lesson card** restores
and recomputes it. `schemas/lesson-card.schema.json` derives its six domains from
the same catalog. Missing parameters take declared defaults. These are parameter
cards, not arbitrary programs. You can also recover a card from exported X3D:

```sh
python3 tools/recover_card.py examples/x3d/lorenz.x3d recovered-lorenz.json
```

Recovery uses validated metadata, not edited meshes. A geometry edit therefore
does not silently become a parameter change. The parameter identity must match.

## The Manim connection

The supplied archive contained an animation-service foundation, historical
handoffs and a reference implementation. It did not include its claimed rendered
movies or an existing X3D Math Lab interface. Those historical documents remain
unchanged as input evidence.

**Download Manim source** creates a `MathlabScene` using the exact current sampled
data. Six default scripts are already in `examples/manim/`. They use `Text` rather
than LaTeX, and bake geometry rather than independently re-solving the lesson.
See [BRIDGE-CONTRACT.md](docs/BRIDGE-CONTRACT.md). On a machine with Manim CE:

```sh
manim -ql examples/manim/fourier.py MathlabScene
```

Actual Manim rendering was not performed here: the available host lacked Manim
and its binary-only installation attempt could not obtain a required ManimPango
wheel. Generated sources compile and retain matching sample identities; that is
not a video-render result. Manim's Cairo/Pango/FFmpeg prerequisites remain a
separate optional installation.

The inherited seven-tool renderer was repaired as v2.1.0: shared concurrency,
same-job locking, engine-context/digest-aware cache checks, atomic publication,
nonblocking previews, child cleanup and stricter identifiers/budgets. It still
executes trusted local Python with host permissions. Syntax checks and a valid
scene name do not isolate that code. The Math Lab HTTP app never executes it.
See [MANIM-AUDIT.md](docs/MANIM-AUDIT.md) for specific repairs and test scopes.

## Optional mathematical MCP tools

The separate read-only Math Lab MCP adapter requires the official SDK, but does
not import Manim. The tested SDK was 1.29.0:

```sh
python3 -m pip install mcp==1.29.0
python3 run_mathlab_mcp.py
```

Configure an MCP client to run the absolute launcher path:

```json
{"mcpServers":{"mathlab":{"command":"python3","args":["/absolute/path/X3D-MathLab/run_mathlab_mcp.py"]}}}
```

It exposes `mathlab_list_lessons`, `mathlab_scene` and `mathlab_manim_source`.
The last tool generates source text; it does not execute it. Actual stdio
initialization, tool listing/calls and a refusal control are recorded in
`receipts/math-mcp.json`. The original `pyproject.toml` remains the separate
Manim renderer's packaging; this complete Math Lab launches from its source ZIP.

## Develop and inspect the evidence

```sh
python3 -m unittest discover -s tests -v
node tests/ui_state.test.mjs
python3 tools/export_examples.py
python3 -m pip install -r tools/requirements-validation.txt
python3 tools/validate_x3d.py
python3 tools/independent_probe.py
python3 tools/probe_math_mcp.py
python3 tools/check_release.py
```

Only optional development instruments need packages: pinned lxml/jsonschema for
X3D/schema checks, MCP SDK for transport checks, and SciPy for the independent
DOP853 comparison. The probe marks the SciPy comparison `not_run` and the
overall result `partial` when unavailable; it never relabels absence as success.
Node is used only by the UI concurrency test.

`VALIDATION.md` separates actual numerical checks, HTTP/MCP transport, adapted
subprocess tests, browser observations and missing hardware/human evidence.
The running server refuses changed producer files so it cannot label cached
Python code with a new disk hash; restart after editing a model producer.
The browser's accepted model/source is separate from a requested control state.

See [FOLDBACK.md](docs/FOLDBACK.md) and [PR.md](docs/PR.md) for portable findings
and a ready review description. The delivery includes a patch against the
supplied source archive. No external Git repository or pull request was changed.
