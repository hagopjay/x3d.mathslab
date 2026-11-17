# Validation record

This is evidence for the delivered first Math Lab edition. It is not a formal
Loom acceptance, a complete mathematical proof, or a learning-outcome study.
The archive's historical render and deployment claims are not reused as fresh
results. Machine-readable receipts retain the actual source and artifact hashes.

## Executed release checks

`python3 tools/check_release.py` completed with **status `pass`**, no skipped
Python tests and **source drift `none`**, on Python 3.12.14/Linux. Its five
instruments ran against one captured source set:

| Instrument | Observed result | Scope |
|---|---|---|
| Python unittest discovery | **89 passed** | 21 kernel, 18 X3D, 13 bridge, 18 inherited-renderer, 9 HTTP server, 4 card recovery, 2 card schema, 4 mathematical MCP controls |
| Node UI state controls | **5 passed** | Actual controller functions with explicit DOM/X_ITE adapters; late responses, serialized commits, fallback, pending-state ownership and queue recovery |
| Independent mathematics probe | **6 groups passed** | Separate numerical expressions, drawn geometry and short-time SciPy DOP853 comparison |
| Mathematical MCP stdio probe | **6 checks passed** | Actual official SDK client/server initialization, listing, calls, identities and invalid-boolean refusal |
| Pinned X3D validator | **6 worlds passed; 2 negative twins caught** | Actual XSD 4.0 validation and implemented semantic checks |

The release checker also verified **143 X_ITE distribution files** and the
**19-file x3d_mcp validation subset** against retained manifests. It checked
generated example bytes, model-source identities and the lesson-card schema.
`receipts/release-checks.json` retains commands, outputs, timing and identities;
the other receipts hold the detailed subordinate results.

The tested MCP SDK was 1.29.0. Its nonfatal Pydantic settings warning appeared on
stderr; initialization and all tool exchanges completed. This is a real test of
the three read-only mathematical tools, not a live test of the legacy Manim
rendering service.

## Mathematical evidence

The independent probe does not call a lesson's answer helper to manufacture its
reference. It checked:

- 500 seeded matrices and 696 emitted real eigenvector directions, with maximum
  recomputed residual approximately **9.16e-16**.
- A five-point derivative stencil at four locations, plus a deliberately wrong
  derivative omitting the quadratic term. The wrong twin was detected.
- Independent 20,000-subinterval quadrature against the antiderivative at three
  intervals. Separately, emitted rectangle dimensions reproduced the reported
  rectangle sum, with area ratios equal to one to floating-point rounding.
- A separately expanded Hessian recurrence at stable, unstable and neutral
  boundary settings; maximum relative difference was approximately **4.41e-15**.
- Sixteen Lorenz parameter corners for finite output and geometry containment.
- SciPy 1.17.0 DOP853 against a short-time RK4 step ladder. Endpoint differences
  were approximately **0.0047610**, **0.00013969** and **0.0000044019** at steps
  0.02, 0.01 and 0.005 respectively. This is a finite experiment, not a global
  error bound or proof of long-time chaotic behavior.

Unit controls additionally exercise singular maps, analytic derivative and
midpoint bounds, Fourier Parseval RMS, exact gradient recurrence, invalid inputs,
finite geometry, adapter budgets, escaped metadata and deterministic identities.
They do not establish arbitrary symbolic mathematics outside these six authored
lesson domains. The independent probe marks its overall outcome `partial` when
SciPy is unavailable rather than treating the missing comparison as a pass.

## Native X3D and representation

Six default examples were checked using the retained x3d_mcp code at commit
`b5c9956917714747fe1d034c729612e99b0f09c9`. The XSD invocation explicitly uses
**4.0**; that subset's semantic helper uses its default **4.1 vocabulary**.
These are distinct checks, documented in `receipts/x3d-validation.json`. They
are not an assertion of complete X3D conformance or exhaustive semantic coverage.
The controls caught an invalid numeric radius at XSD stage and a missing ROUTE
source at semantic stage.

Exports retain normalized parameters, configuration/sample identities, metrics,
scope and per-primitive source IDs. Recovery of all six default cards regenerates
the same X3D bytes. A separately edited mesh is deliberately not interpreted as
a new mathematical parameter setting. `Coordinate.point` remains `MFVec3f`;
Python binary64 diagnostics and rendered coordinates have different precision
boundaries even when XML prints round-trip decimal values.

## Direct browser observations

All six scenes were visually observed in the actual X_ITE viewer. Native 3D used
**ANGLE/SwiftShader software rendering**. This confirms that the native consumer
loaded and displayed these worlds on the observed host; it is not a hardware GPU
performance result.

The observed interaction set included:

- Matrix grids, transformed basis/eigenlines; derivative secant/tangent;
  integration rectangles; Fourier epicycles/waveform; paired 3D Lorenz paths;
  and the gradient surface/path.
- A real keyboard edit of derivative `h` from **0.6 to 0.1**. The analytic slope
  remained about **0.974842**, while central error decreased from **0.045072**
  to **0.0012741**, within the displayed bounds 0.06 and 0.0016667. Pending
  metrics visibly dimmed and exports disabled before the new accepted sample.
- Preservation of the Lorenz default beta value **2.6666666666666665** in the
  numeric control; integer and floating controls have separate step semantics.
- The explicitly labeled SVG projection in a browser without native WebGL,
  lesson navigation, guided previous/next steps, prediction/reveal, Fourier
  animation/pause and the current-source display.
- A 390-pixel wrapper with inner document client/scroll widths both **375 px**,
  without horizontal overflow. This is a narrow viewport observation, not a
  physical mobile-device certification.
- Opening and visually checking the self-contained field guide.

Browser controls do not stand in for the separate deterministic concurrency
tests. Actual file-download/import dialogs, fullscreen, assistive-technology
navigation, mobile hardware, cross-browser pixels and sustained frame rates
were not exhaustively exercised.

## Manim and inherited service boundaries

All six generated Manim sources compile without importing Manim and retain the
same canonical sampled data identity as their native X3D counterparts. The
bridge does not independently solve the mathematics. **No actual Manim video
was rendered.** A binary-only installation attempt could not obtain the needed
ManimPango wheel, and the host lacked the optional Cairo/Pango render stack.
The included Python source is a deliverable, not a claimed movie.

The inherited renderer's 18 controls use an explicit MCP registration adapter,
subprocess adapters and fake render media. One control also starts, terminates
and reaps an owned real Python child. These establish the exercised cache,
publication, containment, concurrency and lifecycle behaviors; they do not
establish Manim/FFmpeg media output, live legacy-render MCP transport, Windows
process-tree equivalence or isolation of untrusted Python.

## Reproduction and remaining evidence

The complete interactive application needs only Python 3.11+ and a browser.
The full development check additionally needs Node, the pinned validation
requirements, MCP SDK 1.29.0 and SciPy. See README commands and the exact receipt
environment. Python 3.13+ is a recommendation, not an interpreter tested here.

Packaging adds an exact normalized attachment baseline, a full-index Git patch,
and an independently applied tree-equality result in the foldback kit. No remote
repository, branch or pull request was published. Actual classroom transfer,
accessibility assessment, hardware profiling, cross-host numerical comparisons
and optional Manim video rendering remain specific future validation work.
