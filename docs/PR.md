# Add x3d.mathlab: six inspectable lessons with native X3D and a shared Manim path

The supplied archive provides a Manim rendering server and historical planning
notes. This change builds the first runnable X3D Math Lab around a shared,
bounded mathematical model rather than a collection of disconnected animations.

Curious-to-advanced learners can manipulate matrix transformations, derivative
limits, Riemann sums, Fourier epicycles, Lorenz trajectories and quadratic
gradient descent. Each scene includes equations, numerical references, guided
steps, prediction/reasoning and inspectable source. The native X_ITE view and
the labeled SVG projection consume the same geometry. No API key is required.

## Technical changes

- Add strict catalog-driven parameters and six pure-Python kernels, analytic
  references/residuals, finite geometry and explicit numerical-method scopes.
- Export deterministic standard-node X3D 4.0 with stable source IDs, metadata,
  parameter/sample identities and geometry-derived bounds. Retain exact-width
  integration rectangles and framing regression controls.
- Add lesson-card schemas/import/export and X3D metadata-to-card recovery;
  edited geometry is not silently treated as a parameter edit.
- Add a loopback app/API with bounded inputs/responses and source-drift refusal,
  plus a polished responsive UI with serialized scene commits and pending-state
  ownership. Bundle the pinned X_ITE runtime/assets/licenses.
- Generate Manim scene source from the exact sampled model without re-solving.
  Add three optional read-only mathematical MCP tools, with a real stdio probe.
- Repair the inherited Manim renderer's process lifecycle, shared concurrency,
  cache identity/integrity, atomic artifact publication and input boundaries.
  Its trusted-local Python execution remains explicit.
- Add a deep field guide, contracts, audit, reproducible independent probes,
  generated examples and release evidence. Historical source documents remain.

## Validation and review scope

See `../VALIDATION.md` and `../receipts/` for exact test counts and identities.
Checks include actual loopback HTTP, native X3D/implemented semantic validation,
independent numerical calculations, real mathematical MCP stdio transport,
adapted legacy renderer controls and UI concurrency functions with explicit
adapters. Live browser observations cover all six native scenes, a derivative
parameter change, projection fallback, guided steps, animation, source display,
exact defaults, a narrow viewport and the guide.

Native rendering used ANGLE/SwiftShader. No hardware GPU benchmark, cross-host
numerical equivalence, classroom learning-outcome study, actual Manim video or
live legacy Manim-render MCP result is claimed. Generated Manim source is not a
movie. The current lesson collection is a first vertical slice of a broader
Mathematical Lab vision, not coverage of all mathematics.

## Patch base

The patch targets the source files in the supplied `manimV2.zip`, omitting
cached bytecode. The kit includes a file-hash baseline, exact application check
and instructions. There was no repository URL for this archive and no external
repository or PR was changed. This file is a ready PR body for the chosen home.
