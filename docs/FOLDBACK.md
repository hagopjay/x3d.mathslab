# Math Lab: portable lessons and design boundaries

This extension starts from the supplied `manimV2.zip` source, not from an already
implemented X3D Math Lab. The archive's prior render counts, package installations,
"production-ready" labels and remote commit identifiers are historical claims.
The delivered validation record owns fresh results. The lessons below are
bounded source/design observations, not new Loom laws or a formal acceptance
receipt.

## 1. Give the mathematical answer an owner before adding another renderer

**Risk.** An interactive diagram and a film can appear to teach the same lesson
while evaluating different formulas, parameter defaults or numerical methods.
A renderer's decorative coordinate change can also leak into a metric.

**Implemented boundary.** The Python kernel evaluates known lesson definitions
into a shared numerical sample. That sample carries normalized parameters,
primitives, metrics, numerical data and display bounds. Native X3D and the Manim
snapshot generator consume that sample; they do not independently solve a
second version of the question. The browser is a controller and consumer.

**Concrete examples.** Lorenz display coordinates map the state `(x,y,z)` to
`(0.36x,0.36(z−23),0.36y)`. The gradient surface height uses a viewing scale
`0.6/sqrt(condition)`. Endpoint separation, loss and stability metrics remain in
the original mathematical quantities. The two display maps must not be treated
as alternate physical or numerical models.

**Precision boundary.** The current scene uses `Coordinate.point` (`MFVec3f`).
Seventeen decimal digits in XML do not remove that single-precision field
boundary. Kernel metrics, serialized coordinates and rendered buffers need their
own declared precision domains.

**Review targets.** Retain exact sample/configuration identities. Compare the
baked primitive data with what each adapter consumes. Check that changing camera,
projection, styling or export medium cannot change a mathematical answer.

**Portable heuristic.** Treat a renderer as an observer over a versioned model.
When two media disagree, first compare their consumed model and transformation
contracts, then compare pixels.

## 2. A check needs a mathematical noun after "error"

**Risk.** A small diagnostic becomes an overly broad correctness claim when
analytic truth, truncation bounds, sampled residuals and refinement differences
share one unlabeled "error" field.

**Implemented examples.** The derivative lesson compares forward and central
finite differences with the analytic derivative, and separately gives the
central truncation bound. The integral lesson uses an antiderivative reference
and labels the midpoint-only bound. The linear lesson reports the displayed
interpolated matrix's determinant and a residual for its drawn real eigenvectors.
The gradient lesson compares iteration with an independent eigen-coordinate
closed form.

**Review targets.** Keep a deliberately wrong or limiting case beside each
healthy one: a singular map; a coarse rectangle sum; an incorrect derivative
scheme; an unstable gradient step. Do not check a result by invoking its own
mistaken helper twice. A theoretical bound need not be tight, and a small
residual does not establish every desired property.

**Portable heuristic.** Store the reference, comparison operation, units,
assumptions and numerical setting with the diagnostic. Avoid promoting one
quantity into another through a short UI label.

## 3. Keep dynamical sensitivity separate from numerical refinement

**Risk.** Two diverging Lorenz paths can be presented as proof of chaos, or as a
numerical-method failure, without identifying what changed.

**Implemented boundary.** One path comparison changes the initial state while
retaining the RK4 method and base step. Another retains the intended initial
state while comparing the base step with two half steps. The implementation
adjusts the base step downward to end at the requested duration exactly; its
actual value is reported. A fixed finite-time experiment does not establish an
infinite-time attractor or a Lyapunov exponent.

**Review targets.** Check endpoint time alignment, finite generated coordinates,
parameter ranges and step budgets. Compare short horizons before long horizons.
Do not call the h-versus-h/2 endpoint difference a rigorous global error bound.
Analytic negative flow divergence is not by itself a chaos detector.

**Portable heuristic.** Name the controlled variable before interpreting a
trajectory difference: initial condition, equation parameter, discretization,
host or presentation.

## 4. Output geometry has limits after parameters have passed

**Risk.** Valid scalar parameters can expand into too many coordinates, faces,
objects or generated source bytes. XML escaping alone does not establish finite
geometry or valid mesh indexing.

**Implemented boundary.** The X3D adapter validates known primitive kinds,
finite coordinate/material fields, positive dimensions, bounds, mesh faces and
aggregate work limits before emission. It generates safe DEF identities rather
than trusting display titles as identifiers. The Manim bridge reuses the sample
validator and adds its own baked-source and polygon budgets. Refusal is explicit;
it does not silently reduce a surface while reporting the original model.

**Review targets.** Exercise both a within-limit case and an over-budget twin;
malformed indices; nonfinite values; escaped metadata; repeated output identity;
and unsupported primitive kinds. Check that a rejected proposal leaves the last
valid experiment available.

**Portable heuristic.** Validate each expansion at the boundary that owns its
work. A parameter budget, a coordinate budget and a render-polygon budget are
related but not interchangeable.

## 5. The current response owns the visible experiment

**Risk.** A slow response for an earlier parameter set can arrive after a later
one. Without response ownership, the UI can combine a new title or slider value
with old metrics and a downloadable scene from another experiment.

**Design boundary.** The web controller should associate every evaluation with
the current request sequence and normalized configuration. Only the latest
accepted response may replace the view, metrics and export payload. Pending or
failed work needs a clear state; a download must not silently mix versions.

**Review targets.** Make the earlier request complete late, change lessons while
a request is pending, submit invalid parameters, and export immediately after a
change. Observe the actual browser path as well as any isolated controller
control. An aborted request is not necessarily cancelled work on the server.

**Portable heuristic.** Scene identity, parameter identity and response identity
form one ownership decision. Updating them independently creates a plausible
but incoherent lesson.

## 6. Syntax validation is not an execution sandbox

**Source observation.** The attachment's server writes caller-supplied Python
and runs Manim as a subprocess. Its scene-name validator and static diagnostics
can improve correctness and argument handling, but they do not isolate Python
execution from the local user's privileges.

**Boundary.** The interactive Math Lab evaluates known lesson parameters and
does not require arbitrary Python execution. The Manim bridge generates a baked
snapshot source file; generating that source, compiling it and rendering it are
three different outcomes. Running the optional Manim tool remains trusted local
code execution. It should not be repackaged as a public arbitrary-code HTTP
endpoint without a separately designed and verified isolation system.

**Review targets.** Render IDs and artifact paths need containment checks;
configuration and cleanup counts need valid ranges; timeout/cancellation needs
child-process reaping; shared output publication and concurrency need explicit
ownership. Cache identity must name its engine/environment scope. Read
`MANIM-AUDIT.md` and the final validation record for the exact repaired and
executed scope, rather than inferring it from this review list.

**Implemented audit repairs.** The active v2 service now tightens artifact-ID
and symlink containment, bounded environment/input/batch values, a shared
single/batch concurrency cap, duplicate render ownership, cache engine context
and video digest/publication checks, selected final-file lookup, bounded process
output, asynchronous preview work and timeout/cancellation reaping. Its
controls use an explicit MCP registration adapter and fake render payloads;
one also owns a real Python child for lifecycle testing. They do not constitute
a Manim/FFmpeg media run or a live MCP-client test. Engine context is deliberately
narrower than a complete font/asset/plugin/configuration/hardware identity.

**Portable heuristic.** A validator should say what it establishes. "Parses",
"contains a scene", "uses supported primitives", "rendered successfully" and
"isolated untrusted execution" are distinct claims.

## 7. Pedagogical evidence is a separate instrument

**Risk.** An attractive model, passing numerical checks or a correctly encoded
X3D scene is treated as evidence that a learner understood the mathematics.

**Design boundary.** The experience targets curious-to-advanced learners. Its
first question invites a prediction; equations and diagnostics reveal deeper
layers. Human teaching observations should ask whether a learner can explain a
changed example, identify an approximation and transfer an idea to a new case.

**Review targets.** Observe hesitation, interpretation of controls, predicted
outcomes and the explanation after a counterexample. Separate those observations
from CPU time, renderer availability and mathematical residuals. Keep accessible
text and numerical readings available when the 3D view is unavailable.

**Portable heuristic.** A lesson's success criterion is more than the existence
of its picture. Pair technical acceptance with a concrete learning question.

## Evidence and artifact map

Three defects found during this implementation sharpen the general heuristics:

1. **Decorative spacing changed a mathematical quantity.** Rectangle width was
   initially `0.97*dx`, so the drawn area represented only 97% of the displayed
   sum. The fix uses exact `dx`; an independent check now sums emitted box
   dimensions. When geometry encodes area, volume or probability, styling must
   preserve that measure or explicitly declare a separate display convention.
2. **Valid geometry escaped nominal framing.** Fixed bounds missed some allowed
   Lorenz trajectories, high-order Fourier geometry and integral boxes. Bounds
   now derive from emitted points and full sphere/box extents, with padding.
   Containment tests exercise defaults and extremes. A valid model is not yet a
   legible model; framing is an output-derived invariant.
3. **A new disk hash could describe old loaded code.** A long-running Python
   process retains imported modules while files can change underneath it. The
   server now captures producer hashes at load and refuses model work after
   source drift. Restart is explicit. A content identity must name the producer
   that actually ran, not merely the file most recently found at its path.

The lesson-card schema is likewise generated from the catalog rather than a
second handwritten parameter table. Recovering a card from X3D validates its
configuration identity and recomputes the lesson; it never silently treats an
edited mesh as an inverse solution. A future bidirectional editor should make
that inverse problem a separate, constrained operation with its own evidence.

| Domain | Owner | Relevant checks or record |
|---|---|---|
| Formula, parameter and numerical meaning | `mathlab/catalog.py`, `mathlab/kernel.py` | `tests/test_kernel.py` |
| Native spatial representation | `mathlab/x3d.py` | `tests/test_x3d.py`, `docs/X3D-CONTRACT.md` |
| Baked explanatory representation | `mathlab/manim_bridge.py` | Bridge contract and final validation |
| Current interactive state | `web/app.js`, `mathlab/server.py` | Controller/server controls and direct browser observations |
| Optional trusted rendering service | `src/manim_mcp/server.py` | `tests/test_manim_v2.py`, `docs/MANIM-AUDIT.md` |
| Executed scope and retained identities | Release validation and receipts | Final delivery record |

The field guide provides derivations, experiments and a staged future vision.
Its prose does not substitute for executed controls. Historical source records
remain historical; native X3D appearance, movie rendering and human learning
each require their own observed outcome.

## Addendum (17 Nov 2026): lessons from putting the lab on a static host

Observed while launching this lab in `x3d.mathslab`; instruments and numbers in `docs/PAGES.md` and `receipts/`.

7. **A dependency major version is part of the validation identity.** The first fresh run under `mcp` 2.3.0 failed 4 of 89
   tests because `mcp.server.fastmcp` was renamed `MCPServer` and model attributes became snake_case. The shipped receipts named
   mcp 1.29.0, which is why this was invisible. `mcp_server.py` now imports either, tests/probe read attributes under both
   spellings, and `receipts/math-mcp.json` records 2.3.0. Pin or adapt, and write the version in the receipt.
8. **A float hash is a same-runtime identity.** The same `mathlab/*.py` gives bit-identical samples on native CPython and
   Pyodide for lessons using only +, *, sqrt, and a different hash (max 4.441e-16 absolute) for lessons using sin/cos/exp.
   Compare numbers with a stated tolerance across runtimes; keep the hash for same-runtime replay.
9. **A static host does not need a second model.** Pure-stdlib kernels ran unmodified in Pyodide behind the same request gate,
   so there is one model owner (lesson 1) and no JavaScript re-implementation to drift. The Manim renderer, which executes
   Python, is the part that must not move to a public page.
10. **Overlays change the framing contract.** A scene framed for a full-height canvas was partly hidden under the equation
    card (visible in 1440x900 screenshots). Size the canvas to the unobstructed region and compare screenshots, not just node counts.
